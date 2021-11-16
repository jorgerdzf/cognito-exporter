import boto3
import json
import datetime
import time
import sys
import argparse
import aiohttp
import asyncio
from colorama import Fore

#Globals
USER_POOL_ID = ''
LIMIT = 60
MAX_NUMBER_RECORDS = 0 #0 mean all of them
USER_PROPERTIES = ['email'] 
CSV_FILE_NAME = 'CognitoConfirmedButMyIRInexistentUsers.csv'
DEV_ENDPOINT = 'https://joibhsn5vk.execute-api.us-west-2.amazonaws.com/Dev/users'
QA_ENDPOINT = 'https://104h8iper6.execute-api.us-west-2.amazonaws.com/QA/users'
STAGING_ENDPOINT = 'https://42v32piz50.execute-api.us-west-2.amazonaws.com/Staging/users'
DEMO_ENDPOINT = 'https://ezi7bf22qf.execute-api.us-west-2.amazonaws.com/Demo/users'
PROD_ENDPOINT = 'https://zwdtvvxky4.execute-api.us-west-2.amazonaws.com/Prod/users'
API_KEY = ''
API_ENDPOINT = ''

#Params to be received
# MyIR User Pool as --user-pool-id values: us-west-2_PoolID
# Environment as -env values: dev, qa2, staging, demo or prod

print(Fore.WHITE + "Process INIT: Parsing provided parameters")
parser = argparse.ArgumentParser(description='Cognito User Pool export records to CSV file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--user-pool-id', type=str, help="The user pool ID", required=True)
parser.add_argument('--env-api-key', type=str, help="The environment api key to consume GetUsers Endpoint", required=True)
parser.add_argument('-env', type=str, help="The enviroment to use the url", required=True)
args = parser.parse_args()

if args.user_pool_id:
    USER_POOL_ID = args.user_pool_id
if args.env_api_key:
    API_KEY = args.env_api_key
if args.env and args.env == 'dev':
        API_ENDPOINT = DEV_ENDPOINT
if args.env and args.env == 'qa':
        API_ENDPOINT = QA_ENDPOINT
if args.env and args.env == 'staging':
        API_ENDPOINT = STAGING_ENDPOINT
if args.env and args.env == 'demo':
        API_ENDPOINT = DEMO_ENDPOINT
if args.env and args.env == 'prod':
        API_ENDPOINT = PROD_ENDPOINT

print(Fore.WHITE + "Using " + API_KEY + " with: " + API_ENDPOINT)

#Functions
def datetimeconverter(o):
    if isinstance(o, datetime.datetime):
        return str(o)

def get_list_cognito_users(cognito_idp_cliend, next_pagination_token):  
    print(Fore.GREEN + "Getting users from Cognito")
    return cognito_idp_cliend.list_users(
        UserPoolId=USER_POOL_ID,
        Limit=LIMIT,
        Filter='cognito:user_status = "CONFIRMED"'
    ) if next_pagination_token == "" else cognito_idp_cliend.list_users(
        UserPoolId=USER_POOL_ID,
        Limit=LIMIT,
        PaginationToken=next_pagination_token,
        Filter='cognito:user_status = "CONFIRMED"'
    )

async def checkIfUserExists(email):
    print(Fore.YELLOW + 'Searching for: ' + email + ' in MyIR')
    #Search for the user in MyIR using the AdminTool
    query = {
        'firstName':'',
        'lastName':'',
        'email':email,
        'dob':'',
        'state':''
    }
    custom_headers = {
        'X-API-KEY': API_KEY
    }
    async with aiohttp.ClientSession(headers=custom_headers) as session:
        async with session.get(API_ENDPOINT, params=query) as response:
            #await response.text()
            
            if response.status == 200:
                print(Fore.GREEN + "This user does exists in MyIR")
                return True
            else:
                print(Fore.RED + "This user do not exists in MyIR")
                return False

async def main():
    #File Management
    csv_new_line = {USER_PROPERTIES[i]: '' for i in range(len(USER_PROPERTIES))}

    try:
        print(Fore.GREEN + "Creating/Opening CSV file")
        csv_file = open(CSV_FILE_NAME, 'w')
        csv_file.write(",".join(csv_new_line.keys()) + '\n')
    except Exception as err:
        error_message = repr(err)
        print(Fore.RED + "\nERROR: Can not create file: " + CSV_FILE_NAME)
        print("\tError Reason: " + error_message)
        exit()    

    pagination_counter = 0
    exported_records_counter = 0
    pagination_token = ""
    next_pagination_token = ""

    print(Fore.GREEN + "Creating client instance")
    client = boto3.client('cognito-idp', 'us-west-2')

    while pagination_token is not None:
        csv_lines = []
        try:
            user_records = get_list_cognito_users(
                cognito_idp_cliend = client,
                next_pagination_token = pagination_token
            )
        except client.exceptions.TooManyRequestsException as err:
            error_message = err.response["Error"]["Message"]
            print("Error Reason: " + error_message)
            csv_file.close()
            exit()
        except client.exceptions.InvalidParameterException as err:
            error_message = err.response["Error"]["Message"]
            print("Error Reason: " + error_message)
            csv_file.close()
            exit()
        except client.exceptions.NotAuthorizedException as err:
            error_message = err.response["Error"]["Message"]
            print("Error Reason: " + error_message)
            csv_file.close()
            exit()
        except client.exceptions.InternalErrorException as err:
            error_message = err.response["Error"]["Message"]
            print("Error Reason: " + error_message)
            csv_file.close()
            exit()
        except BaseException as error:
            print('An exception occurred: {}'.format(error))
            csv_file.close()
            exit()     
        except:
            print(Fore.RED + "Something not catched occurred, good luck with that")
            csv_file.close()
            exit()

        if set(["PaginationToken","NextToken"]).intersection(set(user_records)):
            pagination_token = user_records['PaginationToken'] if "PaginationToken" in user_records else user_records['NextToken']
        else:
            pagination_token = None

        for user in user_records['Users']:
            csv_line = csv_new_line.copy()
            created_date_str = str(user['UserCreateDate'])
            created_date = datetime.datetime.strptime(created_date_str[0:10], '%Y-%m-%d')

            migration_date_1 = datetime.datetime(2021, 11, 9)
            migration_date_2 = datetime.datetime(2021, 10, 5)
            migration_date_3 = datetime.datetime(2021, 10, 12)
            migration_date_4 = datetime.datetime(2021, 10, 19)
            migration_date_5 = datetime.datetime(2021, 10, 26)
            migration_date_6 = datetime.datetime(2021, 7, 21)
            migration_date_7 = datetime.datetime(2021, 7, 22)

            if ((created_date == migration_date_1) or 
                (created_date == migration_date_2) or 
                (created_date == migration_date_3) or 
                (created_date == migration_date_4) or 
                (created_date == migration_date_5) or 
                (created_date == migration_date_6) or 
                (created_date == migration_date_7)):
                    
                    email_to_search = user['Username']
                    userExists = await checkIfUserExists(email_to_search)

                    if userExists == False:
                        print(Fore.WHITE + 'The user do not exist in MyIR, so we save it into the CSV file')
                        for requ_attr in USER_PROPERTIES:
                            csv_line[requ_attr] = ''
                            for usr_attr in user['Attributes']:
                                if usr_attr['Name'] == requ_attr:
                                    csv_line[requ_attr] = str(usr_attr['Value'])
                        
                        csv_lines.append(",".join(csv_line.values()) + '\n')
            
        csv_file.writelines(csv_lines)

        print("Process Current Status:")
        pagination_counter += 1
        exported_records_counter += len(csv_lines)
        print(Fore.YELLOW + "Page: #{} \n Total Exported Records: #{} \n".format(str(pagination_counter), str(exported_records_counter)))

        if MAX_NUMBER_RECORDS and exported_records_counter >= MAX_NUMBER_RECORDS:
            print(Fore.GREEN + "INFO: Max Number of Exported Reached")
            break    

        if pagination_token is None:
            print(Fore.GREEN + "INFO: End of Cognito User Pool reached")

        print("Cool Down before next batch of Cognito Users")
        time.sleep(0.25)

    print("Closing File.")
    csv_file.close()

asyncio.run(main())