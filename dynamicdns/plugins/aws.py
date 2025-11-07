import boto3

from . import DynamicDnsPlugin


class AWS(DynamicDnsPlugin):
    def update(self, ip):
        """
        Updates an A record in AWS Route53.

        Required config keys:
        - aws_access_key_id: AWS access key
        - aws_secret_access_key: AWS secret key
        - aws_region: AWS region (optional, defaults to 'us-east-1')
        - hosted_zone_id: Route53 hosted zone ID
        """
        # Get AWS credentials from config
        aws_access_key_id = self.config['aws_access_key_id']
        aws_secret_access_key = self.config['aws_secret_access_key']
        aws_region = self.config.get('aws_region', 'us-east-1')
        hosted_zone_id = self.config['hosted_zone_id']

        # Initialize Route53 client
        client = boto3.client(
            'route53',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )

        # Ensure domain ends with a dot for Route53
        domain_name = self.domain if self.domain.endswith('.') else self.domain + '.'

        # Update the DNS record
        try:
            response = client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    'Comment': 'Updated by django-dynamic-dns',
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': domain_name,
                                'Type': 'A',
                                'TTL': 300,
                                'ResourceRecords': [
                                    {
                                        'Value': ip
                                    }
                                ]
                            }
                        }
                    ]
                }
            )

            # Check if the change was successful
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise RuntimeError(
                    f"Failed to update Route53 record for {self.domain}. "
                    f"HTTP Status: {response['ResponseMetadata']['HTTPStatusCode']}"
                )

        except client.exceptions.NoSuchHostedZone:
            raise LookupError(
                f"Hosted zone {hosted_zone_id} not found in Route53"
            )
        except client.exceptions.InvalidChangeBatch as e:
            raise RuntimeError(
                f"Invalid change batch for {self.domain}: {str(e)}"
            )
        except Exception as e:
            raise RuntimeError(
                f"Error updating Route53 record for {self.domain}: {str(e)}"
            )
