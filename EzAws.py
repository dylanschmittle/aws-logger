"""Summary
"""
import boto3
import logging

from botocore.exceptions import ClientError


class EzAws():

    """This class is a wrapper for the AWS Python SDK
    """

    def upload_file(self, file_name, bucket, object_name=None):
        """ This Uploads A Object to a S3 bucket.
        Args:
            file_name (TYPE): Name for the file
            bucket (TYPE): Name of the bucket "my-s3-bucket-name"
            object_name (None, optional): It inherits file_name if blank
        Returns:
            TYPE: Description
        """
        if object_name is None:
            object_name = file_name

        s3_client = boto3.client('s3')

        try:
            response = s3_client.upload_file(file_name, bucket, object_name)

        except ClientError as e:
            logging.error(e)

        return response

    def 