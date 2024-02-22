import os
import boto3
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

def get_env_variables():
    """Fetch all necessary configurations from environment variables."""
    return {
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.getenv('AWS_REGION', 'us-east-2')  # Add AWS region to the environment variables
    }



def configure_boto3_from_docker_secrets(options):
    """
    Configures a boto3 session using AWS credentials read from Docker secrets.
    
    Assumes AWS credentials are stored in Docker secrets at the specified paths.
    Returns a boto3 DynamoDB resource configured with these credentials.
    """
    try:

        # Configure the boto3 session with the read credentials
        session = boto3.Session(
            aws_access_key_id=options['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=options['AWS_SECRET_ACCESS_KEY'],
            region_name=options['AWS_REGION']  # Specify your AWS region
        )

        # Return the configured DynamoDB resource
        return session.resource('dynamodb')

    except Exception as e:
        print(f"Error configuring boto3 from Docker secrets: {e}")
        return None


options = get_env_variables()
print(options)
dynamodb_resource = configure_boto3_from_docker_secrets(options)
if dynamodb_resource:
    print("Successfully configured boto3 with Docker secrets.")
else:
    print("Failed to configure boto3.") 
print(dynamodb_resource)