import boto3
from datetime import datetime


def get_env_variables():
    """Fetch all necessary configurations from environment variables."""
    return {
        'DEVELOPER_KEY': os.getenv('DEVELOPER_KEY'),
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'RESULTS_TABLE_NAME': os.getenv('RESULTS_TABLE_NAME'),
        'AWS_REGION': os.getenv('AWS_REGION')  # Add AWS region to the environment variables
    }
    
def get_dynamodb_client(options):
    """Get the DynamoDB client based on options."""
    aws_region = options.get('AWS_REGION')
    return boto3.resource('dynamodb', region_name=aws_region)

def current_timestamp():
    """Returns the current timestamp formatted for readability."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def create_results_table(dynamodb, options):
    """
    Creates a DynamoDB table for storing video results.

    :param table_name: Name of the DynamoDB table to create.
    :param region: AWS region where the table will be created.
    """
    table_name=options['RESULTS_TABLE_NAME']
    # Define the table schema
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'VideoID',
                'KeyType': 'HASH'  # Partition key
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'VideoID',
                'AttributeType': 'S'  # String
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait for the table to be created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    print(f"Table {TableName} created successfully.")


# Load the .env file
load_dotenv()

options = get_env_variables()
dynamodb = get_dynamodb_client(options)
if dynamodb:
    print("Successfully configured dynamodb.")
else:
    print("Failed to configure boto3.") 
create_results_table(dynamodb, options)