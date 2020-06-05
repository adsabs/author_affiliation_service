
LOG_STDOUT = True

AUTHOR_AFFILIATION_SOLRQUERY_URL = "http://api.adsabs.harvard.edu/v1/search/bigquery"

AUTHOR_AFFILATION_SERVICE_MAX_RECORDS_SOLR = 1000

# must be here for adsmutils to override it using env vars
# but if left empty (resolving to False) it won't be used
SERVICE_TOKEN = None
