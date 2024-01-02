import boto3
ec2=boto3.client("ec2")
ec2.run_instances(ImageId="ami-0a0f1259d8",InstanceType="t2.micro",MinCount=1,MaxCount=1)
