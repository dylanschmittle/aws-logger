from WatchCloudLogs import WatchCloudLogs


def lambda_handler(event, context):

    uri = "mongodb+srv://dylan:lVA51KGhSXxoAgW1@cluster0-fipww.gcp.mongodb.net/test?retryWrites=true&w=majority"
    uri2 = "mongodb://candygramformongo:874eavNDFKJDSt5eo8m4w@ec2-54-237-211-51.compute-1.amazonaws.com:27017/test?retryWrites=true&w=majority"
    s3 = "mongo-db-overflow-log-failover"
    testlog = WatchCloudLogs(uri, s3)
    testlog2 = WatchCloudLogs(uri2, s3)
    document2 = testlog2.fetch()
    document = testlog.fetch()
    print(document)
    print(document2)
    # print("**Sending To DB")
    response = testlog.put_mongo()
    response2 = testlog2.put_mongo()
    print(response)
    print(response2)

    return {'statusCode': 200, 'body': "Win"}
