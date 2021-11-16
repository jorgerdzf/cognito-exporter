import csv
import argparse
import boto3
import botocore.exceptions
import time
from colorama import Fore

#Globals
USER_POOL_ID = ''
FILE_NAME = ''

#Params to be received
# MyIR User Pool as --user-pool-id values: us-west-2_PoolID
# File Name as --file-name
print(Fore.WHITE + "Process INIT: Parsing provided parameters")
parser = argparse.ArgumentParser(description='Cognito User Pool export records to CSV file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--user-pool-id', type=str, help="The user pool ID", required=True)
parser.add_argument('--file-name', type=str, help="The file name where the usernames to delete will be obtained", required=True)
args = parser.parse_args()

if args.user_pool_id:
    USER_POOL_ID = args.user_pool_id
if args.file_name:
    FILE_NAME = args.file_name

print(Fore.WHITE + "Creating client instance")
client = boto3.client('cognito-idp', 'us-west-2')
    
def deleteUserFromCognito(client, username):
    return client.admin_delete_user(
        UserPoolId=USER_POOL_ID,
        Username=username
    )

with open(FILE_NAME) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        try:
            if line_count == 0:
                line_count += 1
            else:
                username = row[0]
                print(Fore.YELLOW + f'\t{username} will be deleted from Cognito.')
                deleteUserFromCognito(client, username)
                print(Fore.YELLOW + f'\tThe user has been deleted from Cognito')
                print(Fore.CYAN + f'\tCool Down before next batch of Cognito Users')
                time.sleep(0.20)
                line_count += 1
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'UserNotFoundException':
                print(Fore.RED + f'\tERROR: This user do not exists in cognito, moving to the next one.')
                line_count += 1
            else:
                raise error
            
    print(Fore.GREEN + f'INFO: Deletion Complete. Processed {line_count-1} record(s).')
