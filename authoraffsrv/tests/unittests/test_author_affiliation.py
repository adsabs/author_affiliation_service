# -*- coding: utf-8 -*-

import sys
import os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(PROJECT_HOME)

import datetime
import json

from flask_testing import TestCase
import unittest

import authoraffsrv.app as app
from authoraffsrv.tests.unittests.stubdata import solrdata, formatted, export
from authoraffsrv.views import Formatter, Export, EXPORT_FORMATS

class TestAuthorAffiliation(TestCase):
    def create_app(self):
        #Start the wsgi application
        return app.create_app()

    def test_formatted_data(self):
        # format the stubdata using the code
        formatted_data = Formatter(solrdata.data).get(0, datetime.datetime.now().year)
        # now compare it with an already formatted data that we know is correct
        assert(formatted_data == formatted.data)

    def test_solr_status_error(self):
        solr_data = {
           "responseHeader":{
              "status":400,
              }
           }
        formatted_data = Formatter(solr_data).get()
        assert(formatted_data == None)

    def test_export_csv(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data.replace('\n', '').replace('\r', '')).format(EXPORT_FORMATS[0])
        # now compare it with an already formatted data that we know is correct
        assert(exported_data == export.csv)

    def test_export_csv_div(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data.replace('\n', '').replace('\r', '')).format(EXPORT_FORMATS[1])
        # now compare it with an already formatted data that we know is correct
        assert(exported_data == export.csv_div)

    def test_export_excel(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data.replace('\n', '').replace('\r', '')).format(EXPORT_FORMATS[2])
        # now compare it with an already formatted data that we know is correct
        assert(len(exported_data) == 22016)

    def test_export_excel_div(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data.replace('\n', '').replace('\r', '')).format(EXPORT_FORMATS[3])
        # now compare it with an already formatted data that we know is correct
        assert(len(exported_data) == 26112)

    def test_export_text(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data.replace('\n', '').replace('\r', '')).format(EXPORT_FORMATS[4])
        # now compare it with an already formatted data that we know is correct
        assert(exported_data == export.text)

    def test_no_payload(self):
        """
        Ensure that if no payload is passed in, returns 400
        """
        r = self.client.post('/search')
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, 'error: no information received')


    def test_no_payload_param(self):
        """
        Ensure that if payload without all the needed params is passed in, returns 400
        """
        r = self.client.post('/search', data=json.dumps({'missingParamsPayload': ''}))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, 'error: no bibcodes found in payload (parameter name is "bibcodes")')

    def test_payload_param_error_max_author(self):
        """
        Ensure that if payload without all the needed params is passed in, returns 400
        """
        payload = {'bibcodes': ["1994AAS...185.4102A","1994AAS...185.4104E"], 'maxauthor':-1}
        r = self.client.post('/search', data=json.dumps(payload))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, 'error: parameter maxauthor should be 0 or a positive integer')


    def test_payload_param_error_cutoff_year(self):
        """
        Ensure that if payload without all the needed params is passed in, returns 400
        """
        payload = {'bibcodes': ["1994AAS...185.4102A", "1994AAS...185.4104E"], 'cutoffyear':1800}
        r = self.client.post('/search', data=json.dumps(payload))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, 'error: parameter cutoffyear should be a year >= 1900')


if __name__ == '__main__':
  unittest.main()