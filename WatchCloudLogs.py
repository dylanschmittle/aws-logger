import EzAws
import boto3
import json
import logging
import time

from botocore.exceptions import ClientError

from pymongo import MongoClient


class WatchCloudLogs():
    """Summary
    Docker Use Instructions: (https://hub.docker.com/_/mongo)
        $ docker run --name db -d mongo:latest
        $ docker run -it --network net --rm mongo mongo --host db test
    TODO - Add async to functions that populate __document_que
        https://docs.python.org/3.6/library/asyncio.html
            1. conncetion to resources
            2. concurrent cwl aws api calls to populate __document_que
            3. squash __document_que
            4. concurrent output of __document_que to destinations
            5. concurrent log return response from destinations
    """
    def __init__(self, MONGO_URI=None, S3_BUCKET=None, MONGO_COLLECTION="awsLogs", LOG_GROUPS=['CI', 'Beta'], startTime=None, stopTime=None):
        """Summary
            Initialize The Connections that We Can make
            We make 3 connections: s3  cloudwatch  mongodb
        Args:
            MONGO_URI (TYPE): Description
            S3_BUCKET (TYPE): Description
            LOG_GROUPS (TYPE): Description
        """
        # Work with python internal logging class
        self._log = logging.getLogger()
        # #####################################################################
        # if(LOG_GROUPS = None)
        #     self.__logGroups = LOG_GROUPS
        # else
        #     self.__logGroups = ['CI', 'Beta']
        # #####################################################################
        # self.__logGroups = LOG_GROUPS if LOG_GROUPS is not None else ['CI', 'Beta']
        # #####################################################################
        self.__logGroups = LOG_GROUPS
        self.__bucket = S3_BUCKET
        self.__mongouri = MONGO_URI
        self.__collection_str = MONGO_COLLECTION
        self.__cwl_client = boto3.client('logs')
        self.__s3_client = boto3.client('s3')
        self.__document_que = []
        self.__connection = MongoClient(self.__mongouri)
        self.__db = self.__connection.testdb_testcollection
        self.__collection = self.__db[self.__collection_str]
        self.time_end = int(time.time()) * 1000
        self.time_start = ((int(time.time())) * 1000) - 120000
        self.hasFailed = False

    def change_uri(self, new_uri):
        temp_uri = str(self.__mongouri)
        self.__mongouri = new_uri

        try:
            self.__connection = MongoClient(self.__mongouri)
            self.__db = self.__connection.testdb_testcollection
            self.__collection = self.__db[self.__collection_str]
            # self.__connection.close()

        except Exception as e:
            # print(e)
            self.__init__(self, temp_uri, self.__bucket, self.__logGroups)
            # print(str(self.dumps(self)))
            return {'statusCode': 500, 'body': str(e)}

        return {'statusCode': 200, 'body': "Sucessful Connection Established"}

    def fetch(self):
        """Summary
            Fetch logs from the desired log groups
        Returns:
            TYPE: Description
        """
        # These two and nested asyncio
        # print(self.__logGroups)
        for x in self.__logGroups:
            print("Fetching Log Group: "+x)
            self.put_group(x)

        # Wait for the above and then squash
        # self.squash(self)

        # For DEBUG only, switch back to response style later
        # return {'statusCode': 200, 'body': "CI and Beta Fargate Logs Sent"}
        return self.__document_que

    def get_all(self):
        """Summary
            This will Grab all the logs for the default time interval and send
            them to the default destination
        Returns:
            TYPE: Description
        """
        return {'statusCode': 501, 'body': "Not Implemented"}

    def get_taged(self):
        """Summary
            TODO
        Returns:
            TYPE: Description
        """
        return {'statusCode': 501, 'body': "Not Implemented"}

    def put_cwl(self):
        """Summary
            TODO
        Returns:
            TYPE: Description
        """
        return {'statusCode': 501, 'body': "Not Implemented"}

    def put_s3(self, file_name,  object_name=None):
        """Summary
            TODO
        Args:
            file_name (TYPE): Description
            object_name (None, optional): Description
        Returns:
            TYPE: Description
        """
        self.__s3_client = boto3.client('s3')
        result = EzAws.upload_file(self, file_name, object_name=None)
        return {'statusCode': 200, 'body': result}

    def put_group(self, group):
        """Summary
            TODO
        Args:
            group (TYPE): Description
        Returns:
            TYPE: Description
        """
        response = self.__cwl_client.describe_log_streams(
            logGroupName=group,
            orderBy='LastEventTime',
            descending=True,
            limit=50,
        )
        # Iterate through response to get stream names
        result = []
        for x in response['logStreams']:
            # print(x)
            logStreamName = x['logStreamName']
            # print(logStreamName)
            result.append(self.put_stream(group, logStreamName))
        # TODO iterate results and determine response
        return {'statusCode': 200, 'body': str(group)+":Stream Names Consumed"}

    def put_serverless(self):
        """Summary.
            TODO
            Args:
            group (TYPE): Description
            stream (TYPE): Description
            Returns:
            TYPE: Description
        """
        response_serverless_ci = self.__cwl_client.describe_log_groups(
            logGroupNamePrefix='/aws/lambda/ci-'
        )
        for x in response_serverless_ci['logGroups']:
            print(x['logGroupName'])
        response_serverless_dev = self.__cwl_client.describe_log_groups(
            logGroupNamePrefix='/aws/lambda/dev-'
        )
        for x in response_serverless_dev['logGroups']:
            print(x['logGroupName'])
        response_serverless_prd = self.__cwl_client.describe_log_groups(
            logGroupNamePrefix='/aws/lambda/prd-'
        )
        for x in response_serverless_prd['logGroups']:
            print(x['logGroupName'])

        # response = self.__cwl_client.get_log_events(
        #     logGroupName=group,
        #     logStreamName=str(stream),
        #     startTime=self.time_start,
        #     endTime=self.time_end,
        # )
        # # print(response['events'])
        # for i in response['events']:
        #     print(stream.split("/", 1))
        #     add_stream_name_temp = {
        #         'environment': group,
        #         'container': stream.split("/", 1),
        #         'streamname': stream,
        #         'message': i['message'],
        #         'timestamp': i['timestamp'],
        #         'ingestionTime': i['ingestionTime'],
        #     }
        #     self.__document_que.append(add_stream_name_temp)
        #     print(add_stream_name_temp)

        return {
            'statusCode': 200,
            'body': "Serverless Log Messages Consumed"
            }

    def put_stream(self, group, stream):
        """Summary.
            TODO
        Args:
            group (TYPE): Description
            stream (TYPE): Description
        Returns:
            TYPE: Description
        """
        # print("put_stream("+stream+")")

        response = self.__cwl_client.get_log_events(
            logGroupName=group,
            logStreamName=str(stream),
            startTime=self.time_start,
            endTime=self.time_end,
        )
        # print(response['events'])
        for i in response['events']:
            # print(stream.split("/", 1)[0])
            add_stream_name_temp = {
                'environment': group,
                'container': stream.split("/", 1)[0],
                'streamname': stream,
                'message': i['message'],
                'timestamp': i['timestamp'],
                'ingestionTime': i['ingestionTime'],
            }
            self.__document_que.append(add_stream_name_temp)
            print(add_stream_name_temp)

        return {
            'statusCode': 200,
            'body': str(group)+str(stream)+":Log Messages Consumed"
            }

    def squash(self):
        """Summary
            Delete Empty Message Logs
            Sort objects in documents
            Delete Duplicate Logs by comparing neighboring objects
        Args:
            __document_que (TYPE): Description
        Returns:
            TYPE: Description
        """
        return {'statusCode': 501, 'body': "Not Implemented"}

    def put_mongo(self):
        # Can we insert the whole documnet as it stands?
        try:
            self.__collection.insert_many(self.__document_que)

        # If we cant, throw an error and dump document & self
        except Exception as e:
            print(e)
            #logging.error(e)
        # Can we insert the document piece by piece?
        else:
            for x in self.__document_que:
                self.__put(x)
            return {'statusCode': 200, 'body': "Single Insert Sucessful"}
        return {'statusCode': 200, 'body': "Que sent to Destination or s3"}

    def __put(self, i):
        """Summary.
        Try to put object[i] from __document_que into the data destination.
        If it fails, log it, tag it, and put it in a s3.
        Then delete object[i] from __document_que
        Arguments:
            i (int) -- Index of objcect in __document_que
        """
        t = time.time()
        try:
            self.__db.insert(self.__document_que[i])
        except ClientError as e:
            logging.error(e)
            print(t + " time ")
            print(json.dumps(self.__document_que[i]))
        # Case 1
        else:
            self.__upload_file(
                t + "-error",
                self.__bucket,
                self.__document_que[i]
                )
            print("HIT ERROR")
            return {
                'statusCode': 202,
                'body': "Exception : document sent to s3",
            }
        # Case 2
        finally:
            return {
                'statusCode': 200,
                'body': "document sent to destination",
            }
        # Case 3
        return {
            'statusCode': 500,
            'body': "Exception : No Destinations Available",
        }

    def dumps(self):
        """Summary
            Returns a Serialized JSON String of class variables
            TODO: Add in Post Connection Info currently commented out
        Returns:
            TYPE: JSON formatted string
        """
        return json.dumps({
            # '__db': self.__db,
            # '__collection': self.__collection,
            # '__cwl_client': self.__cwl_client,
            # '__connection': self.__connection,
            '__bucket': self.__bucket,
            '__mongouri': self.__mongouri,
            '__logGroups': self.__logGroups,
            '__collection_str': self.__collection_str,
            '__document_que': self.__document_que,
            'time_end': self.time_end,
            'hasFailed': self.hasFailed,
            'time_start': self.time_start,
        })

    def log_self(self, e=Exception):
        e_log = {
            'vars': self.dumps(self),
            'exception': e.dumps,
        }
        return e_log

"""Simple Testing Method

Tests:
    Initizile
    Change DB
    Get Single Strean
    Get all a Log Group's Streams
    Get Multiple Groups
    Error Handle Connection Issues
    Internal Error Log w/ Python
    Send To s3
    Squashing Duplicates
"""

# Assume Lambda Has Permissions and Access to Resources, or local CLI
# tool is configured and has Permissions

uri = "mongodb+srv://dylan:lVA51KGhSXxoAgW1@cluster0-fipww.gcp.mongodb.net/test?retryWrites=true&w=majority"
uri_badcreds = "mongodb+srv://dyln:lVA66666hSXxoAgW1@cluster0-fipww.gcp.mongodb.net/test?retryWrites=true&w=majority"
uri_fake = "mongodb+srv://lan:lVA51KGAgW1@cluster0-fipww.gcp.mo.net/test?retryWrites=true&w=majority"
uri_invalid = "mongoERRdb+srv://user:lVA5zzhSXxoAgW1@fake.mongodb.net/fake?out"
s3 = "mongo-db-overflow-log-backup"
s3_dne = "mongo-db-nonexistant-s3"

# print("===========START __init__ & dumps TEST========")
# print("(1) Constructor Passed URI and s3")
testlog = WatchCloudLogs(uri, s3)
# variabledict = testlog.dumps()
# print(variabledict)
testlog.put_stream_serverless()

# testlogInvalid = WatchCloudLogs()
# variabledictInvalid = testlogInvalid.dumps()
# print("(2) Default Constructor")
# print(variabledictInvalid)
# print("===========END TEST=======================")

# print("===========START MONGO URI TEST===========")
# print("(1) Invalid URI")
# response = testlog.change_uri(uri_invalid)
# print(response)
# print("(2) Invalid DNS")
# response = testlog.change_uri(uri_fake)
# print(response)
# print("(3) Invalid Creds")
# response = testlog.change_uri(uri_badcreds)
# print(response)
# print("(4) Valid Creds")
# response = testlog.change_uri(uri)
# print(response)
# print("==========END MONGO URI TEST==============")

# print("========START DEFAULT STREAM TEST==========")
# testlog = WatchCloudLogs(uri, s3)
# document = testlog.fetch()
# # print(document)
# print("**Sending To DB")
# response = testlog.put_mongo()
# print(response)

# print("========END DEFAULT STREAM TEST============")
