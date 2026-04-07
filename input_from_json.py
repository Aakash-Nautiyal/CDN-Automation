import boto3
import json

cf = boto3.client('cloudfront')


def load_config():
    with open('config.json') as f:
        return json.load(f)


def get_distribution_config(dist_id):
    res = cf.get_distribution_config(Id=dist_id)
    return res['DistributionConfig'], res['ETag']


def build_behavior(base_config, path_pattern):
    return {
        'PathPattern': path_pattern,
        'TargetOriginId': base_config['target_origin_id'],
        'ViewerProtocolPolicy': base_config['viewer_protocol_policy'],

        'CachePolicyId': base_config['cache_policy_id'],
        'OriginRequestPolicyId': base_config['origin_request_policy_id'],
        'ResponseHeadersPolicyId': base_config['response_headers_policy_id'],

        'AllowedMethods': {
            'Quantity': len(base_config['allowed_methods']),
            'Items': base_config['allowed_methods'],
            'CachedMethods': {
                'Quantity': 2,
                'Items': ['GET', 'HEAD']
            }
        },

        'Compress': base_config.get('compress', True),
        'SmoothStreaming': False,

        'FieldLevelEncryptionId': '',

        'LambdaFunctionAssociations': {
            'Quantity': 0
        },

        'FunctionAssociations': {
            'Quantity': 0
        },

        'TrustedSigners': {
            'Enabled': False,
            'Quantity': 0
        }
    }


def add_behaviors(config, behavior_config):
    paths = behavior_config['path_patterns']

    existing = [
        b['PathPattern']
        for b in config.get('CacheBehaviors', {}).get('Items', [])
    ]

    for path in paths:
        if path in existing:
            print(f"Skipping (already exists): {path}")
            continue

        new_behavior = build_behavior(behavior_config, path)

        if config.get('CacheBehaviors', {}).get('Quantity', 0) == 0:
            config['CacheBehaviors'] = {
                'Quantity': 1,
                'Items': [new_behavior]
            }
        else:
            config['CacheBehaviors']['Items'].append(new_behavior)
            config['CacheBehaviors']['Quantity'] += 1

        print(f"Added: {path}")

    return config


def update_distribution(dist_id, config, etag):
    res = cf.update_distribution(
        Id=dist_id,
        IfMatch=etag,
        DistributionConfig=config
    )

    print("\nUpdate Status:", res['Distribution']['Status'])
    print("Domain:", res['Distribution']['DomainName'])


def main():
    data = load_config()

    dist_id = data['distribution_id']
    behavior_config = data['behavior']

    config, etag = get_distribution_config(dist_id)

    updated_config = add_behaviors(config, behavior_config)

    update_distribution(dist_id, updated_config, etag)


if __name__ == "__main__":
    main()