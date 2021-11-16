#  Export Amazon Cognito User Pool records into CSV

This project allows to:
- Export user records to CSV file from [Amazon Cognito User Pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html)
- Verify if all the users from a user pool exists in another database and export it into a CSV those inexistent.
- Bulk delete users from cognito from a CSV file

## Instalation Requirements

In order to use this script you should have Python 3 installed on your platform
- (if using windows) Download latest version: https://www.python.org/downloads/
- (if using Linux) Pythong already comes with most of the linux distributions, so you only need to install pip.
    - In case of having an old version, please check this guide to update: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/migrationpy3.html#guide-migration-py3
- Install Boto3 by running `pip install boto3`
- Install aiohttp by running `pip install aiohttp`
- Install asyncio by running `pip install asyncio`

## Configuration

Before using Boto3, you need to set up authentication credentials for your AWS account using either the IAM Console or the AWS CLI.

If you have the AWS CLI installed, then you can use the aws configure command to configure your credentials file:

 - `$ aws configure`

    -  Please, be sure you configure the DEFAULT profile with the key and secret key for the account with access to the pool you want to
    work with (Boto3 uses default profile to have access to the aws console/account):
        - [default]
        - aws_access_key_id = YOUR_ACCESS_KEY
        - aws_secret_access_key = YOUR_SECRET_KEY

## A) Run Export

- `$ python3 CognitoUserToCSV.py  --user-pool-id 'us-west-2_PoolID' -attr sub email`
- Wait until you see output `INFO: End of Cognito User Pool reached`
- Find file `CognitoUsers.csv` that contains all exported users.

### Script Arguments

- `--user-pool-id` [__Required__] - The user pool ID for the user pool on which the export should be performed
- `-attr` or `--export-attributes` [__Required__] - List of Attributes that will be saved into the CSV file

## B) Run Verification Cognito VS External Database

- `$ python3 CognitoMyIRUserCompare.py --user-pool-id us-west-2_PoolID --env-api-key TheCorrespondingAPIKey -env demo`
- Wait until you see output `INFO: End of Cognito User Pool reached`
- Find file `CognitoConfirmedButMyIRInexistentUsers.csv` that contains all the cognito confirmed but inexistent users in MyIR.

### Script Arguments

- `--user-pool-id` [__Required__] - The user pool ID for the user pool on which the export should be performed
- `--env-api-key` [__Required__] - The api authorization key for the corresponding environment
- `-env` [__Required__] - The environment to be used (dev, qa, staging, demo, prod), a list of all the endpoints already exist within the script.

## C) Run Bulk Delete

- `$ python3 CognitoCSVBulkDelete.py  --user-pool-id us-west-2_PoolID --file-name CognitoConfirmedButMyIRInexistentUsers.csv`
- Wait until you see output `INFO: Processed n Lines`

### Script Arguments

- `--user-pool-id` [__Required__] - The user pool ID for the user pool on which the export should be performed
- `--file-name` [__Required__] - The CSV file from where the usernames will be taken to perform the delete action in cognito
