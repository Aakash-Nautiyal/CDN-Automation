import boto3
import uuid

client = boto3.client('cloudfront')

def create_distribution():
    origin_domain = input("Enter Origin Domain (e.g. mybucket.s3.amazonaws.com): ")
    origin_id = input("Enter Origin ID: ")
    default_root = input("Default root object (press enter to skip): ") or ""
    
    enabled_input = input("Enable distribution? (yes/no): ").lower()
    enabled = True if enabled_input == "yes" else False

    protocol_policy = input("Viewer Protocol Policy (allow-all / redirect-to-https / https-only): ")

    price_class = input("Price Class (PriceClass_100 / PriceClass_200 / PriceClass_All): ")

    caller_reference = str(uuid.uuid4())

    response = client.create_distribution(
        DistributionConfig={
            'CallerReference': caller_reference,
            'Comment': 'Created via Boto3 script',
            'Enabled': enabled,
            'PriceClass': price_class,
            'DefaultRootObject': default_root,

            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'Id': origin_id,
                        'DomainName': origin_domain,
                        'CustomOriginConfig': {
                            'HTTPPort': 80,
                            'HTTPSPort': 443,
                            'OriginProtocolPolicy': 'http-only'
                        }
                    }
                ]
            },

            'DefaultCacheBehavior': {
                'TargetOriginId': origin_id,
                'ViewerProtocolPolicy': protocol_policy,

                'AllowedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD'],
                    'CachedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD']
                    }
                },

                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {
                        'Forward': 'none'
                    }
                },

                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0
                },

                'MinTTL': 0
            },

            'ViewerCertificate': {
                'CloudFrontDefaultCertificate': True
            },

            'Restrictions': {
                'GeoRestriction': {
                    'RestrictionType': 'none',
                    'Quantity': 0
                }
            }
        }
    )

    print("Distribution Created!")
    print("Domain Name:", response['Distribution']['DomainName'])


if __name__ == "__main__":
    create_distribution()