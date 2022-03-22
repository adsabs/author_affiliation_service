
from builtins import str
from flask import current_app, request
import requests
import re

re_valid_affiliation = re.compile(r'[A-Za-z]{3,}')
def get_solr_data(bibcodes, cutoff_year, start=0, sort='date desc'):
    data = 'bibcode\n' + '\n'.join(bibcodes)

    rows = min(current_app.config['AUTHOR_AFFILATION_SERVICE_MAX_RECORDS_SOLR'], len(bibcodes))

    query = 'year:' + str(cutoff_year) + '-3000'

    fields = 'author,aff,aff_canonical,pubdate'

    params = {
        'q': query,
        'wt': 'json',
        'rows': rows,
        'start': start,
        'sort': sort,
        'fl': fields,
        'fq': '{!bitset}'
    }

    authorization = current_app.config.get('SERVICE_TOKEN', None) or \
                    request.headers.get('X-Forwarded-Authorization', request.headers.get('Authorization', ''))

    headers = {
        'Authorization': authorization,
        'Content-Type': 'big-query/csv',
    }


    try:
        response = current_app.client.post(
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
                    for doc in from_solr['response']['docs']:
                        # if canonical affiliation is a valid affiliation, isn't just dashes use that, otherwise use aff
                        aff_canonical = doc.pop('aff_canonical', None)
                        if aff_canonical:
                            aff = [canonical if re_valid_affiliation.findall(canonical) else regular for regular, canonical in zip(doc.get('aff'), aff_canonical)]
                            doc.update({u'aff': aff})
                    return from_solr
        else:
            current_app.logger.warn('Non-standard status from solr detected: %s, \n%s' % (response.status_code, response.json()))
        return None
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        current_app.logger.error('Solr exception. Terminated request.')
        current_app.logger.error(e)
        return None

