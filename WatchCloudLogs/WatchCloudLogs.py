import EzAws
import boto3
import json
import logging
import time

from botocore.exceptions import ClientError

from pymongo import MongoClient


class WatchCloudLogs():
    """Summary
    Basic Use:
        newWatchCloudLogs = WatchCloudLogs(s3, uri)
        documentsInQue = newWatchCloudLogs.fetch()
        # print(documentsInQue)
        response = newWatchCloudLogs.put_mongo()
        # print(response)
    TODO - Add async to functions that populate __document_que
        https://docs.python.org/3.6/library/asyncio.html
            1. conncetion to resources
            2. concurrent cwl aws api calls to populate __document_que
            3. squash __document_que
            4. concurrent output of __document_que to destinations
            5. concurrent log return response from destinations
    """
    def __init__(self,
                 MONGO_URI=None,
                 S3_BUCKET=None,
                 MONGO_COLLECTION="awsLogs",
                 LOG_GROUPS=['CI', 'Beta'],
                 startTime=None,
                 stopTime=None):
        """Summary
            Initialize The Connections that We Can make
            We make 3 connections: s3  cloudwatch  mongodb
        Args:
            MONGO_URI (TYPE): Description
            S3_BUCKET (TYPE): Description
            LOG_GROUPS (TYPE): Description
        """
        # Work with python internal logging class
        # self._log = logging.getLogger()
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
            Fetch logs from the desired log groups, (CI and Beta Docker logs,
            as well as Serverless prd, dev, and ci prefixes)
        Returns:
            List(JSON-Objectts): All the logs in que that we will be pushing
            into a data consumer
        """
        # These two and nested asyncio
        # print(self.__logGroups)
        for x in self.__logGroups:
            print("Fetching Log Group: " + x)
            self.put_group(x)
        self.put_serverless(self)
        # Wait for the above and then squash
        # This is to possibly remove things we dont care to log
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

    def put_s3(self, file_name, object_name=None):
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
        return {
            'statusCode': 200,
            'body': str(group) + ":Stream Names Consumed"
        }

    def put_serverless(self):
        """Summary.
            TODO
            Args:
            group (TYPE): Description
            stream (TYPE): Description
            Returns:
            TYPE: Description
        """

        # CI Logs
        response_serverless_ci = self.__cwl_client.describe_log_groups(
            logGroupNamePrefix='/aws/lambda/ci-')
        for x in response_serverless_ci['logGroups']:
            self.put_group(x['logGroupName'])
            print(x['logGroupName'])

        # Dev Logs
        response_serverless_dev = self.__cwl_client.describe_log_groups(
            logGroupNamePrefix='/aws/lambda/dev-')
        for x in response_serverless_dev['logGroups']:
            self.put_group(x['logGroupName'])
            print(x['logGroupName'])

        # Production Logs
        response_serverless_prd = self.__cwl_client.describe_log_groups(
            logGroupNamePrefix='/aws/lambda/prd-')
        for x in response_serverless_prd['logGroups']:
            self.put_group(x['logGroupName'])
            print(x['logGroupName'])

        return {'statusCode': 200, 'body': "Serverless Log Messages Consumed"}

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
            'body': str(group) + str(stream) + ":Log Messages Consumed"
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
            # logging.error(e)
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
            self.__upload_file(t + "-error", self.__bucket,
                               self.__document_que[i])
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
