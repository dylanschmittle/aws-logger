"""Summary
"""
import EzAws
import WatchCloudLogs
import json
import logging
import pymongo
import time

# These reports are generated from the raw data in the db
# Not saved because they can be generated again as a query
# So you can run new reports on older logs if needed

# Storage : MongoDB - JSON to BSON (Handeled by the DB) +
#  benefits from the internal optimization from BSON, and
#   the ease of consumption of json, the added time for t
#   he DB to go back and forth is payed back exponentially 
#   as query complexity and database size grow

# Add Delivery System By Email
# Add Graphiz/relational vizualer tool
# Add support for statitics analysis
# Something to vectorize/serialize/model data for ML

'''[summary] Report Api
	Report Class Interface
	2 Reasons to Make Reports
	- Marketing Data Awareness
	- Infrastructure Awareness
[description] Reports -> ( market && || infra ) -> Provider
'''

abstract class Report():

	@abstract
	def scope():
		"""Summary
		"""

	@abstract
	def data():
		"""Summary
		"""

	@abstract
	def relationship():
		"""Summary
		"""

	@abstract
	def diff():
		"""Summary
		"""

	@abstract
	def visualuze():
		"""Summary
		"""

	@abstract
	def relavnet():
		"""Summary
		"""

abstract class MarketingData(Report)

	@abstract
	def realized()

	@abstract
	def cusomter()

abstract class InfrastructureData(Report)

	@abstract
	def drift();

	@abstract
	def effeceted();


class AwsReports(Report):
	def scope(Arn, Role, Policies, tag, description):
		"""Summary

		Args:
		    Arn (TYPE): Description
		    Role (TYPE): Description
		    Policies (TYPE): Description
		    tag (TYPE): Description
		    description (TYPE): Description
		"""

class GoogleReports(Report):

	"""Summary
	"""
	def scope():
		"""Summary
		"""

class IamReports(awsReports):

    """Summary
    """


class VpcReports(awsReports):

    """Summary
    """


class EcsReports(awsReports):

    """Summary
    """