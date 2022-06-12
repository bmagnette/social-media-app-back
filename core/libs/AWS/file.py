import boto3
from botocore.exceptions import NoCredentialsError

ACCESS_KEY = 'AKIA5NJGMSZLE76YBHNL'
SECRET_KEY = '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'


def upload_to_aws(type, content, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        if type == 'file':
            s3.upload_file(content, bucket, s3_file)
        elif type == 'byte':
            s3.put_object(Body=content, Bucket=bucket, Key=s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False