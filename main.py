import boto3

from instances_scan import scan_and_fix


def __main():
    ec2 = boto3.client('ec2')
    scan_and_fix(ec2)


if __name__ == '__main__':
    __main()
