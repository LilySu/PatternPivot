from storage_videoId import videoId_list_in_dynamodb
import boto3
import json
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from runscript_rotate_search_parameters import SearchOptionsCycler
from datetime import datetime
from dotenv import load_dotenv
import time

def start_timer():
    return time.time()

def end_timer(start_time):
    end_time = time.time()
    return end_time - start_time

def current_timestamp():
    """Returns the current timestamp formatted for readability."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_env_variables():
    """Fetch all necessary configurations from environment variables."""
    return {
        'DEVELOPER_KEY': os.getenv('DEVELOPER_KEY'),
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'SEARCH_CACHE_TABLE': os.getenv('SEARCH_CACHE_TABLE'),
        'RESULTS_TABLE_NAME': os.getenv('RESULTS_TABLE_NAME'),
        'SEARCH_QUERY': os.getenv('SEARCH_QUERY'),
        'MAX_RESULTS': int(os.getenv('MAX_RESULTS', 999396)),
        'ORDER': os.getenv('ORDER', 'viewCount'),
        'VIDEO_DURATION': os.getenv('VIDEO_DURATION', 'medium'),
        'PUBLISHED_AFTER': os.getenv('PUBLISHED_AFTER', '2010-01-01T00:00:00Z'),
        'PUBLISHED_BEFORE': os.getenv('PUBLISHED_BEFORE', '2024-12-31T23:59:59Z'),
        'RELEVANCE_LANGUAGE': os.getenv('RELEVANCE_LANGUAGE', 'en'),
        # 'VIDEO_CATEGORY_ID': os.getenv('VIDEO_CATEGORY_ID', '10'),
        'AWS_REGION': os.getenv('AWS_REGION')  # Add AWS region to the environment variables
    }

def open_aws_dynamodb_session(options):
    """
    Configures a boto3 session using AWS credentials read from environment variable.
    Returns a boto3 DynamoDB resource configured with these credentials.
    """
    try:

        # Configure the boto3 session with the read credentials
        session = boto3.Session(
            aws_access_key_id=options['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=options['AWS_SECRET_ACCESS_KEY'],
            region_name=options['AWS_REGION']  # Specify your AWS region
        )
        dynamodb_resource = session.resource('dynamodb')
        print(f"Successfully open_aws_dynamodb_session with environment variables. at {current_timestamp()}\n")
        # Return the configured DynamoDB resource
        return dynamodb_resource

    except Exception as e:
        print(f"Error open_aws_dynamodb_session from environment variables: {e} at {current_timestamp()}\n")
        return None


def first_time_check_cache(options, search_cache_table_value, dynamodb):
    """Check if search options are in the cache on AWS DynamoDB."""
    print(f"Checking cache at {current_timestamp()}\n")
    non_search_terms = ['DEVELOPER_KEY', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'SEARCH_CACHE_TABLE', 'RESULTS_TABLE_NAME', 'AWS_REGION', 'MAX_RESULTS']
    search_query_options = {k: v for k, v in options.items() if k not in non_search_terms}
    key = json.dumps(search_query_options, sort_keys=True)
    try:
        cache_table = dynamodb.Table(search_cache_table_value)
        response = cache_table.get_item(
        Key={
                'CacheKey': key
                # 'Timestamp': sort_key_value  # You'll need to provide the appropriate sort key value here
            }
        )
        if 'Item' in response:
            print("Cache hit.")
            return response
    except Exception as e:
        print(f"Error accessing DynamoDB due to 'check_cache' malfunctioniong: {e} at {current_timestamp()}\n")
    print("--------------------------------------------------------------------------------------\n")
    print("--------------------------------------Cache hit-1st-time------------------------------\n")
    print("--------------------------------------------------------------------------------------\n")
    return {'Item': {'Timestamp': '2024-02-28 15:03:32', 'CacheKey': '{"ORDER": "relevance", "PUBLISHED_AFTER": "2010-01-01T00:00:00Z", "PUBLISHED_BEFORE": "2024-12-31T23:59:59Z", "RELEVANCE_LANGUAGE": "en", "SEARCH_QUERY": "affirmation", "VIDEO_DURATION": "medium"}'}, 'ResponseMetadata': {'RequestId': 'QJN027G2KSUGOH95GUQH2G70UNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Thu, 29 Feb 2024 06:23:28 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '290', 'connection': 'keep-alive', 'x-amzn-requestid': 'QJN027G2KSUGOH95GUQH2G70UNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3681715306'}, 'RetryAttempts': 0}}

def check_cache(dynamodb, search_cache_table_value, full_youtube_cycled_options_dict):
    """Check if search options are in the cache on AWS DynamoDB."""
    print(f"Checking cache at {current_timestamp()}\n")
    key = json.dumps(full_youtube_cycled_options_dict, sort_keys=True)
    # sort_key_value = current_timestamp()

    try:
        cache_table = dynamodb.Table(search_cache_table_value)
        response = cache_table.get_item(
        Key={
                'CacheKey': key #,
                # 'Timestamp': sort_key_value  # You'll need to provide the appropriate sort key value here
            }
        )
        if 'Item' in response:
            print("--------------------------------------Cache hit---------------------------------------\n")
            print(f"The following parameters have already been searched for the past:\n{full_youtube_cycled_options_dict}")
            return response
    except Exception as e:
        print(f"Error accessing DynamoDB due to 'check_cache' malfunctioniong: {e} at {current_timestamp()}\n")
        print("--------------------------------------Cache miss--------------------------------------\n")
    return None

def update_cache(dynamodb, search_cache_table_value, full_youtube_cycled_options_dict):
    """Update the cache with new search results, including the search time."""
    print(f"Updating cache at {current_timestamp()}\n")
    print(f"Searching the following parameters for the first time according to the cache:\n{full_youtube_cycled_options_dict}")
    
    timestamp = current_timestamp()  # Capture the search timestamp
    key = json.dumps(full_youtube_cycled_options_dict, sort_keys=True)
    try:
        search_cache_table = search_cache_table_value
        cache_table = dynamodb.Table(search_cache_table)
        cache_table.put_item(Item={
            'CacheKey': key,
            'Timestamp': timestamp  # Store the search time
        })
        return True
    except Exception as e:
        print(f"Error updating DynamoDB due to 'update_cache' malfunctioniong: {e} at {current_timestamp()}\n")
        return False

def merge_dicts_return_larger(dict1, dict2):
    # Determine which dictionary is larger
    larger_dict = dict1 if len(dict1) > len(dict2) else dict2
    smaller_dict = dict2 if larger_dict is dict1 else dict1

    # Update the values of the larger dictionary with values from the smaller dictionary
    # Gets any unique keys from the smaller dictionary.
    for key in smaller_dict.keys():
        if key in larger_dict:
            # Update the larger dictionary with values from the smaller one
            larger_dict[key] = smaller_dict[key]

    # Output the larger dictionary with updated values
    return larger_dict

def youtube_search_all_videos(options, dynamodb):
    """Perform a search on YouTube Data API and return all videos based on the options, with caching and paging."""
    print(f"Performing YouTube search at {current_timestamp()}\n")

    developer_key = options['DEVELOPER_KEY']
    youtube = build('youtube', 'v3', developerKey=developer_key)
    
    all_videos = []
    page_token = None
    # 10 per page
    max_iterations = 100000  # Adjust based on how many pages you want to retrieve

    try:
        for _ in range(max_iterations):
            search_response = youtube.search().list(
                q=options['SEARCH_QUERY'],
                part='id,snippet',
                maxResults=options['MAX_RESULTS'],
                order=options['ORDER'],
                type='video',
                videoDuration=options['VIDEO_DURATION'],
                publishedAfter=options['PUBLISHED_AFTER'],
                publishedBefore=options['PUBLISHED_BEFORE'],
                relevanceLanguage=options['RELEVANCE_LANGUAGE'],
                # videoCategoryId=options['VIDEO_CATEGORY_ID'], # When there is a category ID assigned, if number 10, then results are mostly music.
                pageToken=page_token
            ).execute()

            # Create a temporary map of video ID to search result item
            video_id_to_search_item = {}
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                video_id_to_search_item[video_id] = item
        
            video_ids = list(video_id_to_search_item.keys())
        
            if video_ids:
                details_response = youtube.videos().list(
                    id=','.join(video_ids),
                    part='contentDetails,statistics,status,topicDetails,liveStreamingDetails,localizations'
                ).execute()
        
                # Update search result items with additional details
                for detail_item in details_response.get('items', []):
                    video_id = detail_item['id']
                    if video_id in video_id_to_search_item:
                        # Combine the detail item with the search result item
                        search_item = video_id_to_search_item[video_id]
                        search_item['details'] = detail_item  # Add a new key for additional details
                        
                        # Append the updated search item to all_videos
                        all_videos.append(search_item)
            time.sleep(1.8)
            page_token = search_response.get('nextPageToken')
            if not page_token:
                break

    except HttpError as e:
        print(f"An HTTP error occurred: {e.resp.status} {e.content} at {current_timestamp()}\n")

    print(f"Function 'youtube_search_all_videos' was run at {current_timestamp()}\n")
    return all_videos


def send_to_dynamodb(options, dynamodb, flattened_single_video_dict):   
    """Send Youtube Data API results on the video and subtitle transcripts to Dynamodb."""
    try:
        results_table_name = options['RESULTS_TABLE_NAME']
        results_table = dynamodb.Table(results_table_name)
        response = results_table.put_item(Item=flattened_single_video_dict)
        print(f"Successfully inserted api results into DynamoDB  at {current_timestamp()}\n", response)
    except Exception as e:
        print(f"Error inserting into DynamoDB: {e}")
    
def flatten_dict(d):
    """
    Flatten a nested dictionary, concatenating keys with a specified separator.

    :param d: The dictionary to flatten
    :param parent_key: The base key string to use for constructing new key names
    :param sep: The separator to use between concatenated keys
    :return: A flattened dictionary
    """
    parent_key=''
    sep='-'
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v).items())
        else:
            items.append((new_key, v))
    return dict(items)

def get_video_ids_from_table(table_name, dynamodb=None):
    """
    Retrieves all videoIds from a specified DynamoDB table.

    :param table_name: The name of the DynamoDB table.
    :param dynamodb: The DynamoDB session object (optional).
    :return: A list of videoIds.
    """
    if dynamodb is None:
        dynamodb = boto3.resource('dynamodb', region_name=region_name)

    table = dynamodb.Table(table_name)
    unique_ids = set()

    # Start the scan operation
    response = table.scan()

    # Extract unique IDs from each item
    for item in response.get('Items', []):
        unique_id = item.get('videoId')
        if unique_id:
            unique_ids.add(unique_id)

    # Continue scanning if more items are available
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        for item in response.get('Items', []):
            unique_id = item.get('videoId')
            if unique_id:
                unique_ids.add(unique_id)

    # Return the list of unique IDs
    return list(unique_ids)


def main():
    start_time = start_timer()
    # Load the .env file
    load_dotenv()
    
    # text file of youtube search terms to cycle through
    file_path = 'ambient_search_terms.txt'
    
    # Get environment variables
    options = get_env_variables()
    search_cache_table_value = options['SEARCH_CACHE_TABLE']

    # Existing VideoId's in the database
    global videoId_list_in_dynamodb
    
    # Counter keeping track of number of times a database insertion has been made in the search results table
    search_result_db_insertions = 0
    
    # Only proceed if options were successfully retrieved
    if options:
        dynamodb = open_aws_dynamodb_session(options)
        
        # Only proceed if DynamoDB was successfully configured
        if dynamodb:
    
            # use default values to do a search, using environment variable defaults
            full_cache_table_value = first_time_check_cache(options, search_cache_table_value, dynamodb)
            long_dict = json.loads(full_cache_table_value['Item']['CacheKey'])
            
            # initialize cache cycler
            cycler = SearchOptionsCycler(file_path)
            
            # start with cycling through order as the search option values to rotate
            cycler.set_cycling_attribute('VIDEO_DURATION') #ORDER
            # cycle for the first time
            youtube_cycled_options_dict = cycler.get_next_options()
    
            # combine the full search terms from environment variables updated with just the new values that got cycled
            full_search_term_cycled_dict = merge_dicts_return_larger(long_dict, youtube_cycled_options_dict)
            try:
                # keep cycling through the entire list of search terms, varying search parameters until the Youtube API limit 
                while True:
                    # while cache hit, cycle through youtube search options
                    while check_cache(dynamodb, search_cache_table_value, full_search_term_cycled_dict):
                        # delay 
                        time.sleep(2)
                        # generate new cycled options, which is a subset of what gets sent to the youtube api
                        youtube_cycled_options_dict = cycler.get_next_options()
                        # combine the full search terms from environment variables updated with just the new values that got cycled
                        full_search_term_cycled_dict = merge_dicts_return_larger(long_dict, youtube_cycled_options_dict)
                    
                    # delay 
                    time.sleep(0.8)
                    # if not a cache hit, store new search terms
                    update_cache(dynamodb, search_cache_table_value, full_search_term_cycled_dict)
                    video_list = youtube_search_all_videos(options, dynamodb)
                    # print(all_videos)
                    # # Only proceed if videos were successfully retrieved
                    for single_video_dict in video_list:
                        flattened_single_video_dict = flatten_dict(single_video_dict)
                        # print(single_video_dict['id']['videoId'])
                        if single_video_dict['id']['videoId'] not in videoId_list_in_dynamodb:
                            print(json.dumps(flattened_single_video_dict, indent=4))
                            time.sleep(1.8)
                            send_to_dynamodb(options, dynamodb, flattened_single_video_dict)
                            # Counter keeping track of number of times a database insertion has been made in the search results table
                            search_result_db_insertions += 1
                        else:
                            print(f"VideoId {single_video_dict['id']['videoId']} is already in the database")
                        if search_result_db_insertions >= 50:
                            # Write the updated list back to the file
                            with open('storage_videoId.py', 'w') as file:
                                file.write(f'videoId_list_in_dynamodb = {videoId_list_in_dynamodb}\n')
                    if HttpError:
                        print("---------------------------------Youtube API Quota Reached---------------------------------\n")
                        print("-----------------------------------Program Discontinued-----------------------------------\n")
                        break
            except HttpError as e:
                print(f"An HTTP error occurred: {e.resp.status} {e.content} at {current_timestamp()}\n")
        else:
            print(f"Failed to configure boto3 from environment variables at {current_timestamp()}. Exiting...\n")
    else:
        print(f"Failed to retrieve environment variables at {current_timestamp()} Exiting...\n")
    total_runtime = end_timer(start_time)
    print(f"Total runtime of the program: {total_runtime} seconds")
    
if __name__ == "__main__":
    main()
