import json
import boto3
import json
import logging
import time
import LogLogger

from botocore.exceptions import ClientError

from pymongo import MongoClient


def lambda_handler(event, context):
    # if event is that mELK stack error logs are coming
    # through, filter and see what action should be taken
    # reboot, replicate, scale, etc
    # if event is timed event, throw the logs from the last
    # time till now at the mELK stack
    # Connections Are Opening
    conn = logLogger(MONGO_URI, S3_BUCKET, LOG_GROUPS)
    # Send ENV for Groups to grab into this call, iterate
    # through list of groups
    conn.put_streams(LOG_GROUPS)

    if(conn.hasFailed):
        return {
            'statusCode': 500,
            'body': LogLogger.dumps(logger),
            }

    return {
        'statusCode': 200,
        'body': json.dumps('Log logging sucessful'),
        }
