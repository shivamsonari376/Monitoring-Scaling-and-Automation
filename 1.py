import boto3

# Initialize boto3 clients
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')

# Variables
bucket_name = "serverless-arch-shivam"  # Existing bucket name
instance_type = "t2.micro"
ami_id = "ami-0c02fb55956c7d316"  # Amazon Linux 2 AMI
security_group_name = "Shivam_SG"  # Existing security group
key_pair_name = "Shivam_key"  # Existing key pair
region = "us-east-1"
html_file_name = "index.html"
web_app_html = "<html><h1>Hello, World from S3!</h1></html>"  # Static HTML content
user_data_script = """#!/bin/bash
yum update -y
yum install -y httpd aws-cli
systemctl start httpd
systemctl enable httpd
aws s3 cp s3://{bucket}/{html_file} /var/www/html/index.html
""".format(bucket=bucket_name, html_file=html_file_name)

# Step 1: Upload the HTML file to the S3 bucket
def upload_html_to_s3():
    print("Uploading HTML file to S3 bucket...")
    try:
        s3_client.put_object(Bucket=bucket_name, Key=html_file_name, Body=web_app_html, ContentType='text/html')
        print(f"HTML file '{html_file_name}' uploaded successfully to bucket '{bucket_name}'.")
    except Exception as e:
        print(f"Error uploading HTML file: {e}")

# Step 2: Launch an EC2 Instance
def launch_ec2_instance():
    print("Launching EC2 instance...")
    try:
        response = ec2_client.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_pair_name,
            SecurityGroupIds=[security_group_name],
            MinCount=1,
            MaxCount=1,
            UserData=user_data_script
        )
        instance_id = response['Instances'][0]['InstanceId']
        print(f"EC2 instance launched with ID: {instance_id}")
        return instance_id
    except Exception as e:
        print(f"Error launching EC2 instance: {e}")

# Step 3: Wait for the Instance to Be Running
def wait_for_instance(instance_id):
    print("Waiting for instance to be in running state...")
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    print(f"Instance {instance_id} is now running.")

# Main Function
def main():
    upload_html_to_s3()
    instance_id = launch_ec2_instance()
    wait_for_instance(instance_id)
    print("Web application deployed successfully.")

if __name__ == "__main__":
    main()
