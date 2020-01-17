
from flask import current_app
import requests

from authoraffsrv.client import client

def get_solr_data(bibcodes, cutoff_year, start=0, sort='date desc'):
    data = 'bibcode\n' + '\n'.join(bibcodes)

    rows = min(current_app.config['AUTHOR_AFFILATION_SERVICE_MAX_RECORDS_SOLR'], len(bibcodes))

    query = 'year:' + str(cutoff_year) + '-3000'

    fields = 'author,aff,pubdate'

    params = {
        'q': query,
        'wt': 'json',
        'rows': rows,
        'start': start,
        'sort': sort,
        'fl': fields,
        'fq': '{!bitset}'
    }

    headers = {
        'Authorization': 'Bearer '+current_app.config['AUTHOR_AFFILIATION_SERVICE_ADSWS_API_TOKEN'],
        'Content-Type': 'big-query/csv',
    }

    try:
        response = client().post(
            url=current_app.config['AUTHOR_AFFILIATION_SOLRQUERY_URL'],
            params=params,
            data=data,
            headers=headers
        )
        if (response.status_code == 200):
            # make sure solr found the documents
            from_solr = response.json()
            if (from_solr.get('response')):
                num_docs = from_solr['response'].get('numFound', 0)
                if num_docs > 0:
                    return from_solr
        return None
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        current_app.logger.error('Solr exception. Terminated request.')
        current_app.logger.error(e)
        return None

