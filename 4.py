import boto3

# Initialize boto3 clients
sns_client = boto3.client('sns')
lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')

# Variables
sns_topic_names = {
    "HealthIssues": "HealthIssuesTopic",
    "ScalingEvents": "ScalingEventsTopic",
    "HighTraffic": "HighTrafficTopic",
}
lambda_function_name = "ShivamSNSNotificationHandler"
email_address = "shivamsonari376@gmail.com"  # Replace with your email address for notifications
sms_phone_number = "+918235449009"  # Replace with your phone number for SMS notifications

# Step 1: Create SNS Topics
def create_sns_topics():
    topic_arns = {}
    print("Creating SNS Topics...")
    for topic_name, topic_display_name in sns_topic_names.items():
        response = sns_client.create_topic(Name=topic_name)
        topic_arns[topic_name] = response['TopicArn']
        print(f"Created SNS Topic: {topic_name} (ARN: {response['TopicArn']})")
        
        # Subscribe email to the topic
        sns_client.subscribe(
            TopicArn=response['TopicArn'],
            Protocol='email',
            Endpoint=email_address,
        )
        print(f"Subscribed email: {email_address} to {topic_name}")
        
        # Subscribe SMS to the topic (optional)
        sns_client.subscribe(
            TopicArn=response['TopicArn'],
            Protocol='sms',
            Endpoint=sms_phone_number,
        )
        print(f"Subscribed phone: {sms_phone_number} to {topic_name}")
    return topic_arns

# Step 2: Create Lambda Function for Notification Handling
def create_lambda_function(sns_topic_arns):
    print("Creating Lambda Function...")
    try:
        # Create IAM Role for Lambda
        lambda_role_name = "SNSLambdaExecutionRole"
        lambda_role = iam_client.create_role(
            RoleName=lambda_role_name,
            AssumeRolePolicyDocument='''{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }'''
        )
        iam_client.attach_role_policy(
            RoleName=lambda_role_name,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        )

        # Create Lambda Function
        lambda_code = '''def lambda_handler(event, context):
    print("Received event:", event)
    for record in event['Records']:
        print("Message:", record['Sns']['Message'])
    return "Success"
        '''
        lambda_client.create_function(
            FunctionName=lambda_function_name,
            Runtime='python3.9',
            Role=lambda_role['Role']['Arn'],
            Handler='index.lambda_handler',
            Code={'ZipFile': lambda_code.encode()},
        )
        print(f"Created Lambda Function: {lambda_function_name}")
    except Exception as e:
        print(f"Error creating Lambda Function: {e}")

# Step 3: Integrate SNS with Lambda
def integrate_sns_with_lambda(sns_topic_arns):
    print("Integrating SNS with Lambda...")
    try:
        for topic_name, topic_arn in sns_topic_arns.items():
            sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol='lambda',
                Endpoint=lambda_function_name,  # ARN of Lambda function
            )
            print(f"Integrated {topic_name} SNS Topic with Lambda")
    except Exception as e:
        print(f"Error integrating SNS with Lambda: {e}")

# Main Function
def main():
    sns_topic_arns = create_sns_topics()
    create_lambda_function(sns_topic_arns)
    integrate_sns_with_lambda(sns_topic_arns)

if __name__ == "__main__":
    main()
