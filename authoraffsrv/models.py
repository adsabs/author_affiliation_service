#!/usr/bin/env python

from flask import current_app
import requests

from adsmutils import setup_logging

import authoraffsrv
from authoraffsrv.client import client

global logger
logger = None

def get_solr_data(bibcodes, start=0, sort='date desc'):
    global logger
    if logger == None:
        logger = setup_logging('ads_author_affilation_service', current_app.config.get('LOG_LEVEL', 'INFO'))

    data = 'bibcode\n' + '\n'.join(bibcodes)

    rows = min(6000, len(bibcodes))

    fields = 'author,aff,year'

    params = {
        'q': '*:*',
        'wt': 'json',
        'rows': rows,
        'start': start,
        'sort': sort,
        'fl': fields,
        'fq': '{!bitset}'
    }

    headers = {'Authorization':'Bearer:'+current_app.config['AUTHOR_AFFILIATION_SERVICE_ADSWS_API_TOKEN']}

    try:
        response = client().post(
            url=current_app.config['AUTHOR_AFFILIATION_SOLRQUERY_URL'],
            params=params,
            data=data,
            headers=headers
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        logger.error('\nbailing')
        logger.error(e)
