import os
import boto3
from dotenv import load_dotenv


def get_env_variables():
    """Fetch all necessary configurations from environment variables."""
    return {
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.getenv('AWS_REGION'),
        'SEARCH_CACHE_TABLE': os.getenv('SEARCH_CACHE_TABLE')
    }
    
def get_dynamodb_client(options):
    """Get the DynamoDB client based on options."""
    aws_region = options.get('AWS_REGION')
    return boto3.resource('dynamodb', region_name=aws_region)

def create_cache_table(dynamodb, options):
    try:
        table_name = options['SEARCH_CACHE_TABLE']
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'CacheKey',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'CacheKey',
                    'AttributeType': 'S'  # String
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table creation initiated, waiting for completion...")
        table.wait_until_exists()
        print(f"Table '{table_name}' created successfully.")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f"Table '{table_name}' already exists.")
        

# Load the .env file
load_dotenv()
options = get_env_variables()
dynamodb = get_dynamodb_client(options)
create_cache_table(dynamodb, options)