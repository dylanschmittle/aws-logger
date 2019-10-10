## MongoDB Setup

Dzone PDF (Composing a Sharded MongoDB Cluster on Docker Containers - DZone Database.pdf)

- Create Cluster and Link Each Shard
> 
```
docker-compose -f mongo-sharded-set.yml up
sh setup-shard.sh
```

- Create a Linked Collection
> 
```
sh create-test-db.sh
```

## WatchCloudLogs Python Class
- Basic Use
> 
```

uri = "mongodb+srv://$USER:$PASS@$DNS/$OPTIONS"
s3 = "$BUCKET_NAME"
testlog = WatchCloudLogs(uri, s3)
# We can Access what is would be submitted here
document = testlog.fetch()
# We can get basic REST response of the submission to the mongo DB
response = testlog.put_mongo()
print(response)

```

## Resources

- MongoDB : [Docs](https://docs.mongodb.com/manual/) -  [Python Tutorial](https://docs.mongodb.com/manual/tutorial/getting-started/)  -  [Freetier](https://docs.mongodb.com/manual/tutorial/atlas-free-tier-setup/#create-free-tier-manual)

- AWS : [Api](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html?id=docs_gateway) - [Cloudwatch](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html) - [Paginators](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#paginators)

### API Cheatsheet

#### Direct Export From Cloudwatch Logs to S3

- Toggle Export Encryption (5 Min Delay)
```
response = client.associate_kms_key(logGroupName='string', kmsKeyId='string')
response = client.disassociate_kms_key(logGroupName='string')
```
- Create a Task For Bulk Export
```
response = client.create_export_task( # ONLY AES-256 is Supported
    taskName='string',
    logGroupName='string',
    logStreamNamePrefix='string',
    fromTime=123,
    to=123,
    destination='string',
    destinationPrefix='string'
)
```
- Cancel a Running Task
```
response = client.cancel_export_task(taskId='string') # Cancels a task in the PENDING or RUNNING state.
```

#### Query
```
response = client.start_query(
    logGroupName='string',
    logGroupNames=[
        'string',],
    startTime=123,
    endTime=123,
    queryString='string',
    limit=123)
response = client.describe_queries(
    logGroupName='string',
    status='Scheduled'|'Running'|'Complete'|'Failed'|'Cancelled',
    maxResults=123,
    nextToken='string')
response = client.stop_query(queryId='string')
response = client.get_query_results(queryId='string')
```

#### Obtaining Stream and Log Group Info

- describe_destinations()
- describe_export_tasks()
- describe_log_groups()
- describe_log_streams()
- describe_metric_filters()
- describe_resource_policies()
- describe_subscription_filters()
- filter_log_events()
- put_log_events()
- get_log_events()
- get_log_group_fields()
- get_log_record()
- get_paginator()
- get_query_results()
- get_waiter()


#### Create Log Groups and Streams
- Optional: tag, kmsKeyId
```
response = client.create_log_group(
    logGroupName='string',
    kmsKeyId='string',
    tags={
        'string': 'string'
    }
)
response = client.create_log_stream(
    logGroupName='string',
    logStreamName='string'
)
```
- delete_log_group()
- delete_log_stream()

#### Metrics, Resources, Rentension Policy
- test_metric_filter()
- delete_metric_filter()
- delete_resource_policy()
- delete_retention_policy()
- put_metric_filter()
- put_resource_policy()
- put_retention_policy()

#### Integrate Kinesis
- put_destination()
- put_destination_policy()
- put_subscription_filter()
- delete_subscription_filter()
- delete_destination()

#### Log Groups and Tags

- Consume Logs with the tag 'log'=True
list_tags_log_group()
- Set Tag on Logs Being Consumed  'last-stream'=${date}
- tag_log_group()
- untag_log_group()

#### ???
```
generate_presigned_url(ClientMethod, Params=None, ExpiresIn=3600, HttpMethod=None)

#Generate a presigned url given a client, its method, and arguments
#Parameters:
#  ClientMethod (string) -- The client method to presign for
#  Params (dict) -- The parameters normally passed to ClientMethod.
#  ExpiresIn (int) -- The number of seconds the presigned url is valid for. By default it expires in an hour (3600 seconds)
#  HttpMethod (string) -- The http method to use on the generated url. By default, the http method is whatever is used in the method's model.
#Returns:
#  The presigned url
```
#### Paginator Functions
```
CloudWatchLogs.Paginator.DescribeDestinations
CloudWatchLogs.Paginator.DescribeExportTasks
CloudWatchLogs.Paginator.DescribeLogGroups
CloudWatchLogs.Paginator.DescribeLogStreams
CloudWatchLogs.Paginator.DescribeMetricFilters
CloudWatchLogs.Paginator.DescribeQueries
CloudWatchLogs.Paginator.DescribeResourcePolicies
CloudWatchLogs.Paginator.DescribeSubscriptionFilters
CloudWatchLogs.Paginator.FilterLogEvents
```


