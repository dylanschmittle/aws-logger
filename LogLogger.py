"""Summary
"""
import boto3
import json
import json
import logging
import time
import JSONEncoder


class LogLogger():

    """Summary
    TODO - Add async to functions that populate __document_que
          1. conncetion to resources
          2. concurrent cwl aws api calls to populate __document_que
          3. squash __document_que
          4. concurrent output of __document_que to destinations
          5. concurrent log return response from destinations
        hasFailed (bool): Description
        time_end (TYPE): Description
        time_start (TYPE): Description
    """

    def __init__(self, MONGO_URI, S3_BUCKET, LOG_GROUPS):
        """Summary
        Initialize The Connections that We Can make
        We make 3 connections: s3  cloudwatch  mongodb
        Args:
            MONGO_URI (TYPE): Description
            S3_BUCKET (TYPE): Description
            LOG_GROUPS (TYPE): Description
        """
        self.__logGroups = LOG_GROUPS
        self.__bucket = S3_BUCKET
        self.__mongouri = MONGO_URI
        self.__client = boto3.client('logs')
        self.__s3_client = boto3.client('s3')
        self.__connection = MongoClient(mongouri)
        self.__db = connection.testdb_testcollection
        self.__data = db.data
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

    def start(self):
        """Summary
        Default Log fetch, grabs all the streams under the log groups Beta and CI
        Returns:
            TYPE: Description
        """
        self.put_group(self, "CI")
        self.put_group(self, "Beta")
        return {'statusCode': 200, 'body': "CI and Beta Fargate Logs Sent"}

    def start(self, LOG_GROUPS):
        """Summary
        This will send all the
        Args:
            LOG_GROUPS (TYPE): Description
        Returns:
            TYPE: Description
        """
        for group in logGroups:
            self.add_streams(self, group)
        return {
            'statusCode': 200,
            'body': str(logGroups)+" Logs Sent",
        }

    def get_all(self):
        """Summary
        This will Grab all the logs for the default time interval and send them to the default destination
        Returns:
            TYPE: Description
        """
        return {'statusCode': 501, 'body': "Not Implemented"}

    def get_all(self, destination):
        """Summary
        
        Args:
            destination (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        return {'statusCode': 501, 'body': "Not Implemented"}

    def get_taged(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return {'statusCode': 501, 'body': "Not Implemented"}

    def put_cwl(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return {'statusCode': 501, 'body': "Not Implemented"}

    def put_s3(self, file_name,  object_name=None):
        """Summary
        
        Args:
            file_name (TYPE): Description
            object_name (None, optional): Description
        
        Returns:
            TYPE: Description
        """
        result = ezAws.upload_file(self, file_name, object_name=None)
        return {'statusCode': 200, 'body': result}

    def put_group(self, group):
        """Summary
        TODO
        Args:
            group (TYPE): Description
        TODO
        Returns:
            TYPE: Description
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html        # Get streams
        response = client.describe_log_streams(
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
        TODO
        Returns:
            TYPE: Description
        """
        response = client.get_log_events(
            logGroupName=group,
            logStreamName=stream,
            startTime=time_start,
            endTime=time_end,
        )

        for i in response['events']:
            m = respose['events'][i]['message']
            t = respose['events'][i]['timestamp']
            f = "[Time]: "+t+" [Message]: "+m
            __document_que.append(f)

        return {
            'statusCode': 200,
            'body': str(group)+str(stream)+":Log Messages Consumed"
            }

    def squash(self):
        """Summary
        Delete Empty Message Logs
        Delete Duplicate Logs
        Args:
            __document_que (TYPE): Description
        TODO
        Returns:
            TYPE: Description
        """
        return {'statusCode': 501, 'body': "Not Implemented"}

    def put(self):
        # Can we insert the whole documnet as it stands?
        try:
            __db.insert_many(__document_que)
        # If we cant, throw an error and dump document & self
        except ClientError as e:
            print json.dumps(__document_que)
            logging.error(e)
        # Can we insert the document piece by piece?
        else:
            for x in __document_que:
                response[x]=self.__put(x)
            return response[0]
        finally:
            connection.close()
            #SNS email bomb "SHITS GOING DOWN NO S3 OR LOG DB AVAILABLE"
        return {'statusCode': 200, 'body': "Que sent to "destination}

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
            __db.insert(__document_que[i])
        except ClientError as e:
            logging.error(e)
            print t + " time \/n"
            print json.dumps(__document_que[i])
        # Case 1
        else:
            __upload_file(t + "-error", __bucket, __document_que[i])
            return {
                'statusCode': 202,
                'body': "Exception : document object ["i"] sent to s3",
            }
        # Case 2
        finally:
            del __document_que[i]
            return {
                'statusCode': 200,
                'body': "document object ["i"] sent to destination",
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