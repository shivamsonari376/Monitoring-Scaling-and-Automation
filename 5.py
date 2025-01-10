import boto3

# Initialize boto3 clients
ec2_client = boto3.client('ec2')
autoscaling_client = boto3.client('autoscaling')
elb_client = boto3.client('elbv2')
sns_client = boto3.client('sns')

# Variables
autoscaling_group_name = "ShivamASG"
launch_template_name = "Shivam-ASG-Launch-Template"
load_balancer_name = "ShivamALB"
sns_topic_name = "InfrastructureNotificationsTopic"

# Deploy Infrastructure
def deploy_infrastructure():
    print("Deploying Infrastructure...")
    # Launch Template
    create_launch_template()
    # Auto Scaling Group
    create_auto_scaling_group()
    # Load Balancer
    create_application_load_balancer()
    # SNS Notification
    create_sns_topic()

# Update Infrastructure
def update_infrastructure():
    print("Updating Infrastructure...")
    # Logic to update infrastructure as needed (e.g., change instance types, scaling policies, etc.)
    # This could include updating launch templates or ASG settings.
    pass

# Tear Down Infrastructure
def tear_down_infrastructure():
    print("Tearing Down Infrastructure...")
    # Delete Auto Scaling Group
    try:
        autoscaling_client.delete_auto_scaling_group(
            AutoScalingGroupName=autoscaling_group_name,
            ForceDelete=True,
        )
        print(f"Deleted Auto Scaling Group: {autoscaling_group_name}")
    except Exception as e:
        print(f"Error deleting Auto Scaling Group: {e}")

    # Delete Launch Template
    try:
        ec2_client.delete_launch_template(LaunchTemplateName=launch_template_name)
        print(f"Deleted Launch Template: {launch_template_name}")
    except Exception as e:
        print(f"Error deleting Launch Template: {e}")

    # Delete Load Balancer
    try:
        elb_client.delete_load_balancer(LoadBalancerArn=load_balancer_arn)
        print(f"Deleted Load Balancer: {load_balancer_name}")
    except Exception as e:
        print(f"Error deleting Load Balancer: {e}")

    # Delete SNS Topic
    try:
        response = sns_client.list_topics()
        for topic in response['Topics']:
            if sns_topic_name in topic['TopicArn']:
                sns_client.delete_topic(TopicArn=topic['TopicArn'])
                print(f"Deleted SNS Topic: {sns_topic_name}")
    except Exception as e:
        print(f"Error deleting SNS Topic: {e}")

# Main Function
def main():
    action = input("Enter action (deploy/update/teardown): ").lower()
    if action == "deploy":
        deploy_infrastructure()
    elif action == "update":
        update_infrastructure()
    elif action == "teardown":
        tear_down_infrastructure()
    else:
        print("Invalid action. Please choose 'deploy', 'update', or 'teardown'.")

if __name__ == "__main__":
    main()
