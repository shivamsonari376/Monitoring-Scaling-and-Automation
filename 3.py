import boto3

# Initialize boto3 clients
ec2_client = boto3.client('ec2')
autoscaling_client = boto3.client('autoscaling')

# Variables
vpc_id = "vpc-09f02049d6176fe30"
subnet_ids = ["subnet-01874c4512136bd62"]  # Comma-separated subnet IDs
security_group_id = "sg-0737192091ac43905"
key_name = "Shivam_key"
launch_template_name = "ShivamASG-Launch-Template"
autoscaling_group_name = "ShivamASG"
instance_type = "t2.micro"  # Replace with your desired instance type
min_size = 1
max_size = 3
desired_capacity = 1
cpu_utilization_threshold = 50  # CPU utilization threshold for scaling

# Step 1: Create a Launch Template
def create_launch_template():
    print("Creating Launch Template...")
    try:
        response = ec2_client.create_launch_template(
            LaunchTemplateName=launch_template_name,
            LaunchTemplateData={
                "ImageId": "ami-1234567890abcdef0",  # Replace with your AMI ID
                "InstanceType": instance_type,
                "KeyName": key_name,
                "SecurityGroupIds": [security_group_id],
                "UserData": "#!/bin/bash\nyum update -y\nyum install -y httpd\nsystemctl start httpd\nsystemctl enable httpd\n"
            },
        )
        launch_template_id = response["LaunchTemplate"]["LaunchTemplateId"]
        print(f"Launch Template created successfully. ID: {launch_template_id}")
        return launch_template_id
    except Exception as e:
        print(f"Error creating Launch Template: {e}")

# Step 2: Create an Auto Scaling Group (ASG)
def create_auto_scaling_group(launch_template_id):
    print("Creating Auto Scaling Group...")
    try:
        response = autoscaling_client.create_auto_scaling_group(
            AutoScalingGroupName=autoscaling_group_name,
            LaunchTemplate={"LaunchTemplateId": launch_template_id},
            MinSize=min_size,
            MaxSize=max_size,
            DesiredCapacity=desired_capacity,
            VPCZoneIdentifier=",".join(subnet_ids),
            Tags=[
                {
                    "Key": "Name",
                    "Value": "ASG-Web-Instance",
                    "PropagateAtLaunch": True,
                }
            ],
        )
        print(f"Auto Scaling Group created successfully: {autoscaling_group_name}")
    except Exception as e:
        print(f"Error creating Auto Scaling Group: {e}")

# Step 3: Create Scaling Policies
def create_scaling_policies():
    print("Creating Scaling Policies...")
    try:
        # CPU Utilization Alarm for Scale Out
        scale_out_policy = autoscaling_client.put_scaling_policy(
            AutoScalingGroupName=autoscaling_group_name,
            PolicyName="ScaleOutPolicy",
            PolicyType="TargetTrackingScaling",
            TargetTrackingConfiguration={
                "PredefinedMetricSpecification": {
                    "PredefinedMetricType": "ASGAverageCPUUtilization",
                },
                "TargetValue": cpu_utilization_threshold,
            },
        )
        print(f"Scale-Out Policy created. ARN: {scale_out_policy['PolicyARN']}")

        # CPU Utilization Alarm for Scale In
        scale_in_policy = autoscaling_client.put_scaling_policy(
            AutoScalingGroupName=autoscaling_group_name,
            PolicyName="ScaleInPolicy",
            PolicyType="TargetTrackingScaling",
            TargetTrackingConfiguration={
                "PredefinedMetricSpecification": {
                    "PredefinedMetricType": "ASGAverageCPUUtilization",
                },
                "TargetValue": 
