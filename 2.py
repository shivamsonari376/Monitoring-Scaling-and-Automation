import boto3
import random

# Initialize boto3 clients
ec2_client = boto3.client('ec2')
elb_client = boto3.client('elbv2')

# Variables
vpc_id = "vpc-09f02049d6176fe30"
subnet_ids = ["subnet-01874c4512136bd62"]
security_group_id = "sg-0737192091ac43905"
alb_name = "My-Application-Load-Balancer"
target_group_name = "ShivamTG"
port = 80

# Step 1: Fetch Random EC2 Instance from the VPC
def fetch_random_instance():
    print("Fetching a random EC2 instance from the VPC...")
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {"Name": "vpc-id", "Values": [vpc_id]},
                {"Name": "instance-state-name", "Values": ["running"]}
            ]
        )
        instances = [
            instance["InstanceId"]
            for reservation in response["Reservations"]
            for instance in reservation["Instances"]
        ]
        if not instances:
            print("No running instances found in the specified VPC.")
            return None
        instance_id = random.choice(instances)
        print(f"Selected random instance: {instance_id}")
        return instance_id
    except Exception as e:
        print(f"Error fetching instances: {e}")

# Step 2: Create an Application Load Balancer (ALB)
def create_alb():
    print("Creating Application Load Balancer...")
    try:
        response = elb_client.create_load_balancer(
            Name=alb_name,
            Subnets=subnet_ids,
            SecurityGroups=[security_group_id],
            Scheme="internet-facing",
            Type="application",
            IpAddressType="ipv4"
        )
        alb_arn = response["LoadBalancers"][0]["LoadBalancerArn"]
        print(f"ALB created successfully. ARN: {alb_arn}")
        return alb_arn
    except Exception as e:
        print(f"Error creating ALB: {e}")

# Step 3: Create a Target Group
def create_target_group():
    print("Creating Target Group...")
    try:
        response = elb_client.create_target_group(
            Name=target_group_name,
            Protocol="HTTP",
            Port=port,
            VpcId=vpc_id,
            TargetType="instance"
        )
        target_group_arn = response["TargetGroups"][0]["TargetGroupArn"]
        print(f"Target Group created successfully. ARN: {target_group_arn}")
        return target_group_arn
    except Exception as e:
        print(f"Error creating Target Group: {e}")

# Step 4: Register EC2 Instances with the Target Group
def register_instance_with_target_group(target_group_arn, instance_id):
    print("Registering EC2 instance with Target Group...")
    try:
        elb_client.register_targets(
            TargetGroupArn=target_group_arn,
            Targets=[{"Id": instance_id}]
        )
        print(f"Instance {instance_id} registered successfully.")
    except Exception as e:
        print(f"Error registering instance: {e}")

# Step 5: Create a Listener for the ALB
def create_listener(alb_arn, target_group_arn):
    print("Creating Listener for ALB...")
    try:
        elb_client.create_listener(
            LoadBalancerArn=alb_arn,
            Protocol="HTTP",
            Port=port,
            DefaultActions=[{"Type": "forward", "TargetGroupArn": target_group_arn}]
        )
        print("Listener created successfully.")
    except Exception as e:
        print(f"Error creating Listener: {e}")

# Main Function
def main():
    instance_id = fetch_random_instance()
    if not instance_id:
        print("No instances available to register. Exiting.")
        return

    alb_arn = create_alb()
    if not alb_arn:
        return

    target_group_arn = create_target_group()
    if not target_group_arn:
        return

    register_instance_with_target_group(target_group_arn, instance_id)
    create_listener(alb_arn, target_group_arn)
    print("Load Balancer setup complete.")

if __name__ == "__main__":
    main()
