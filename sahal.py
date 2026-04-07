import boto3

cf = boto3.client('cloudfront')


# -----------------------------
# LIST DISTRIBUTIONS
# -----------------------------
def list_distributions():
    res = cf.list_distributions()
    items = res.get('DistributionList', {}).get('Items', [])

    print("\nAvailable Distributions:\n")
    for i, d in enumerate(items):
        print(f"{i+1}. {d['Id']} | {d['DomainName']}")

    return items


# -----------------------------
# SELECT DISTRIBUTION
# -----------------------------
def select_distribution(dists):
    choice = int(input("\nSelect distribution number: ")) - 1
    return dists[choice]['Id']


# -----------------------------
# GET CONFIG
# -----------------------------
def get_config(dist_id):
    res = cf.get_distribution_config(Id=dist_id)
    return res['DistributionConfig'], res['ETag']


# -----------------------------
# LIST ORIGINS
# -----------------------------
def list_origins(config):
    print("\nAvailable Origins:\n")
    for o in config['Origins']['Items']:
        print(f"- {o['Id']}")


# -----------------------------
# LIST POLICIES
# -----------------------------
def list_cache_policies():
    res = cf.list_cache_policies(Type='managed')
    items = res['CachePolicyList']['Items']

    print("\nCache Policies:\n")
    for i, p in enumerate(items):
        print(f"{i+1}. {p['CachePolicy']['Id']} | {p['CachePolicy']['CachePolicyConfig']['Name']}")

    return items


def list_origin_request_policies():
    res = cf.list_origin_request_policies(Type='managed')
    items = res['OriginRequestPolicyList']['Items']

    print("\nOrigin Request Policies:\n")
    for i, p in enumerate(items):
        print(f"{i+1}. {p['OriginRequestPolicy']['Id']} | {p['OriginRequestPolicy']['OriginRequestPolicyConfig']['Name']}")

    return items


def list_response_headers_policies():
    res = cf.list_response_headers_policies(Type='managed')
    items = res['ResponseHeadersPolicyList']['Items']

    print("\nResponse Headers Policies:\n")
    for i, p in enumerate(items):
        print(f"{i+1}. {p['ResponseHeadersPolicy']['Id']} | {p['ResponseHeadersPolicy']['ResponseHeadersPolicyConfig']['Name']}")

    return items


# -----------------------------
# CREATE BEHAVIOR
# -----------------------------
def create_behavior(config):

    print("\n--- Enter Behavior Details ---")

    path_pattern = input("Path Pattern (e.g. /images/*): ")

    list_origins(config)
    target_origin_id = input("Target Origin ID: ")

    protocol = input("Viewer Protocol Policy (allow-all / redirect-to-https / https-only): ")

    # Policies
    cache_policies = list_cache_policies()
    cp_choice = int(input("Select Cache Policy: ")) - 1
    cache_policy_id = cache_policies[cp_choice]['CachePolicy']['Id']

    origin_req_policies = list_origin_request_policies()
    orp_choice = int(input("Select Origin Request Policy: ")) - 1
    origin_request_policy_id = origin_req_policies[orp_choice]['OriginRequestPolicy']['Id']

    resp_policies = list_response_headers_policies()
    rp_choice = int(input("Select Response Headers Policy: ")) - 1
    response_headers_policy_id = resp_policies[rp_choice]['ResponseHeadersPolicy']['Id']

    new_behavior = {
        'PathPattern': path_pattern,
        'TargetOriginId': target_origin_id,
        'ViewerProtocolPolicy': protocol,

        'CachePolicyId': cache_policy_id,
        'OriginRequestPolicyId': origin_request_policy_id,
        'ResponseHeadersPolicyId': response_headers_policy_id,

        'AllowedMethods': {
            'Quantity': 2,
            'Items': ['GET', 'HEAD'],
            'CachedMethods': {
                'Quantity': 2,
                'Items': ['GET', 'HEAD']
            }
        },

        'Compress': True,
        'SmoothStreaming': False,

        # ✅ ADD THIS (fix)
        'FieldLevelEncryptionId': '',

        'LambdaFunctionAssociations': {
            'Quantity': 0
        },
        
        'LambdaFunctionAssociations': {
            'Quantity': 0
        },

        'TrustedSigners': {
            'Enabled': False,
            'Quantity': 0
        }
    }

    # Add behavior
    if config.get('CacheBehaviors', {}).get('Quantity', 0) == 0:
        config['CacheBehaviors'] = {
            'Quantity': 1,
            'Items': [new_behavior]
        }
    else:
        config['CacheBehaviors']['Items'].append(new_behavior)
        config['CacheBehaviors']['Quantity'] += 1

    return config


# -----------------------------
# UPDATE DISTRIBUTION
# -----------------------------
def update_distribution(dist_id, config, etag):
    res = cf.update_distribution(
        Id=dist_id,
        IfMatch=etag,
        DistributionConfig=config
    )

    print("\nBehavior added successfully!")
    print("Status:", res['Distribution']['Status'])
    print("Domain:", res['Distribution']['DomainName'])


# -----------------------------
# MAIN
# -----------------------------
def main():
    dists = list_distributions()
    dist_id = select_distribution(dists)

    config, etag = get_config(dist_id)

    updated_config = create_behavior(config)

    update_distribution(dist_id, updated_config, etag)


if __name__ == "__main__":
    main()