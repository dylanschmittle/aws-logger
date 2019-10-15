#!/bin/python3
from WatchCloudLogs.py import WatchCloudLogs
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
testlog.put_serverless()
testlog.put_mongo()
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
