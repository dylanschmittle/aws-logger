import LogLogger
import json


def lambda_handler(event, context):
    # if event is that mELK stack error logs are coming
    # through, filter and see what action should be taken
    # reboot, replicate, scale, etc
    # if event is timed event, throw the logs from the last
    # time till now at the mELK stack
    # Connections Are Opening
    # groups = ["Ci", "Beta"]
    # mongo_uri = "#ENV IN LAMBDA"
    # s3_name = "#ENV IN LAMBDA"
    # conn = LogLogger(mongo_uri, s3_name, groups)
    # # Send ENV for Groups to grab into this call, iterate
    # # through list of groups
    # document = conn.fetch()
    # print(json.dumps(document))
    # transfer = conn.put_mongo()
    # print(json.dumps(transfer))
    # s3transfer = conn.put_s3()
    # print(json.dumps(s3transfer))

    # if(conn.hasFailed):
    #     return {
    #         'statusCode': 500,
    #         'body': conn.dumps()
    #         }

    # return {
    #     'statusCode': 200,
    #     'body': 'Log logging sucessful'
    #     }
    uri = "mongodb+srv://dylan:lVA51KGhSXxoAgW1@cluster0-fipww.gcp.mongodb.net/test?retryWrites=true&w=majority"
    s3 = "mongo-db-overflow-log-failover"
    testlog = WatchCloudLogs(uri, s3)
    document = testlog.fetch()
    # print(document)
    # print("**Sending To DB")
    response = testlog.put_mongo()
    # print(response)


    return {
        'statusCode': 200,
        'body': "Win"
    }
