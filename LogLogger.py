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
    def __init__(self, MONGO_URI, S3_BUCKET=None, LOG_GROUPS=['CI', 'Beta']):
        """Summary
        Initialize The Connections that We Can make
        We make 3 connections: s3  cloudwatch  mongodb
        Args:
            MONGO_URI (TYPE): Description
            S3_BUCKET (TYPE): Description
            LOG_GROUPS (TYPE): Description
        """
        self.wordList = wordList if wordList is not None else []
        self._log = logging.getLogger()
        self.__logGroups = LOG_GROUPS
        self.__bucket = S3_BUCKET
        self.__mongouri = MONGO_URI
        self.__mongouri2 = MONGO_URI_2
        self.__client = boto3.client('logs')

        self.__document_que = []
        self.hasFailed = False
        self.time_end = int(time.time()) * 1000
        self.time_start = ((int(time.time())) * 1000) - 120000

    def __init__(self, MONGO_URI, S3_BUCKET, LOG_GROUPS, startTime, stopTime):
        """Summary
            Overide time 2m interval default represented in ms
        Args:
            MONGO_URI (TYPE): Description
            S3_BUCKET (TYPE): Description
            LOG_GROUPS (TYPE): Description
            startTime (TYPE): Description
            stopTime (TYPE): Description
        """
        self.logLogger(self, MONGO_URI, S3_BUCKET, LOG_GROUPS)
        self.time_end = int(time.time()) * 1000
        self.time_start = ((int(time.time())) * 1000) - 120000

    @classmethod
    def change_uri(cls, new_uri)
    ```
    Try to connect to the new db uri
    ```
        try:
            cls.__mongouri = new_uri
            self.__connection = MongoClient(self.__mongouri)
            self.__db = self.__connection.testdb_testcollection
            self.__data = self.__db.__data
            self.__connection.close()
        except ClientError as e:

        return {'statusCode': 200, 'body': "Not Implemented"}
    def fetch(self):
        """Summary
            Fetch logs from the desired log groups
        Returns:
            TYPE: Description
        """
        # These two and nested asyncio
        for x in self.__logGroups:
            self.put_group(self, self.__logGroups[x])

        # Wait for the above and then squash
        self.squash(self)

        # For DEBUG only, switch back later
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
        response = self.__client.describe_log_streams(
            logGroupName=group,
            orderBy='LastEventTime',
            descending=True,
            limit=50,
        )
        # Iterate through response to get stream names
        result = {}
        for x in response['logStreams']:
            logStreamName = response['logStreams'][x]['logStreamName']
            result.append(self.put_stream(self, logStreamName))
        # TODO iterate results and determine response
        return {'statusCode': 200, 'body': str(group)+":Stream Names Consumed"}

    def put_stream(self, group, stream):
        """Summary.
            TODO
        Args:
            group (TYPE): Description
            stream (TYPE): Description
        Returns:
            TYPE: Description
        """
        response = self.__client.get_log_events(
            logGroupName=group,
            logStreamName=stream,
            startTime=self.time_start,
            endTime=self.time_end,
        )

        for i in response['events']:
            m = response['events'][i]['message']
            t = response['events'][i]['timestamp']
            f = "[Time]: "+t+" [Message]: "+m
            self.__document_que.append(f)

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

        self.__connection = MongoClient(self.__mongouri)
        self.__db = self.__connection.testdb_testcollection
        self.__data = self.__db.__data
        # Can we insert the whole documnet as it stands?
        try:
            self.__db.insert_many(self.__document_que)

        # If we cant, throw an error and dump document & self
        except ClientError as e:
            # print json.dumps(__document_que)
            logging.error(e)

        # Can we insert the document piece by piece?
        else:
            for x in self.__document_que:
                self.response[x] = self.__put(x)
            return self.response[0]

        finally:
            self.__connection.close()

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
            return {
                'statusCode': 202,
                'body': "Exception : document object ["+i+"] sent to s3",
            }
        # Case 2
        finally:
            del self.__document_que[i]
            return {
                'statusCode': 200,
                'body': "document object ["+i+"] sent to destination",
            }
        # Case 3
        return {
            'statusCode': 500,
            'body': "Exception : No Destinations Available",
        }

    def dumps(self):
        """Summary
            Returns a Serialized JSON String of class variables
        Returns:
            TYPE: JSON formatted string
        """
        return json.dumps({
            '__db': self.__db,
            '__data': self.__data,
            '__bucket': self.__bucket,
            '__client': self.__client,
            '__mongouri': self.__mongouri,
            '__logGroups': self.__logGroups,
            '__s3_client': self.__s3_client,
            '__connection': self.__connection,
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
