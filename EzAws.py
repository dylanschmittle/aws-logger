import boto3
import json
import logging
import time

#AWS Wrapper Class 
class EzAws:
    s3bucket = S3_BUCKET
    def upload_file(self, file_name, __bucket, object_name=None):
        if object_name is None:
            object_name = file_name
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return(False)
        return(True)