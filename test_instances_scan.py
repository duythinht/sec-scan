import boto3

from moto import mock_ec2
from instances_scan import scan_and_fix


def test_scan_and_fix_instance():
    with mock_ec2():
        ec2 = boto3.client('ec2', region_name='us-east-1')

        __create_mock_resource(ec2, boto3.resource('ec2', region_name='us-east-1'))

        scan_and_fix(ec2)
        for reservation in ec2.describe_instances().get('Reservations', []):
            for instance in reservation.get('Instances', []):
                tag = instance.get('Tags', [{}])[0]
                assert (tag.get('Key', '') == 'AllowSSH'
                        and tag.get('Value', '') == 'true'
                        and len(instance['SecurityGroups']) == 1
                        ) or len(instance['SecurityGroups']) == 0


def __create_mock_resource(ec2, ec2_resource):
    vpc_id = ec2.describe_vpcs().get('Vpcs', [{}])[0].get('VpcId', '')

    image_id = ec2.describe_images().get('Images', [{}])[0].get('ImageId', '')

    security_group_id = ec2.create_security_group(
        GroupName='allow ssh',
        Description='ssh allow for 0.0.0.0/0',
        VpcId=vpc_id)['GroupId']

    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ])

    # create instance with AllowSSH Tag
    ec2_resource.create_instances(
        ImageId=image_id,
        MinCount=1,
        MaxCount=2,
        InstanceType="t2.micro",
        KeyName="KeyPair1",
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'AllowSSH',
                        'Value': 'true'
                    }
                ]
            }
        ],
        SecurityGroups=[security_group_id]
    )

    # create instances without tags
    ec2_resource.create_instances(
        ImageId=image_id,
        MinCount=5,
        MaxCount=10,
        InstanceType="t2.micro",
        KeyName="KeyPair2",
        SecurityGroups=[security_group_id]
    )
