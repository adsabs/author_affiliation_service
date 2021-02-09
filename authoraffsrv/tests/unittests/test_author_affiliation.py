# -*- coding: utf-8 -*-

import sys
import os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(PROJECT_HOME)

from flask_testing import TestCase
import unittest

import authoraffsrv.app as app
from authoraffsrv.tests.unittests.stubdata import solrdata, formatted, export
from authoraffsrv.views import Formatter, Export, EXPORT_FORMATS, is_number

class TestAuthorAffiliation(TestCase):
    def create_app(self):
        #Start the wsgi application
        return app.create_app()

    def test_formatted_data(self):
        # format the stubdata using the code
        formatted_data = Formatter(solrdata.data).get(0, 2017)
        # now compare it with an already formatted data that we know is correct
        self.assertEqual(formatted_data, formatted.data)

    def test_solr_status_error(self):
        solr_data = {
           "responseHeader":{
              "status":400,
              }
           }
        formatted_data = Formatter(solr_data).get()
        self.assertEqual(formatted_data, None)

    def test_export_csv_format(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).format(EXPORT_FORMATS[0])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual(exported_data, export.csv)

    def test_export_csv_div_format(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).format(EXPORT_FORMATS[1])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual(exported_data, export.csv_div)

    def test_export_excel_format(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).format(EXPORT_FORMATS[2])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual(len(exported_data), 5632)

    def test_export_excel_div_format(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).format(EXPORT_FORMATS[3])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual(len(exported_data), 5632)

    def test_export_text_format(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).format(EXPORT_FORMATS[4])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual(exported_data, export.text)

    def test_export_text_format2(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).format(EXPORT_FORMATS[5])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual(exported_data, export.text)

    def test_export_csv_get(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).get(EXPORT_FORMATS[0])
        # now check the status_code to be 200
        self.assertEqual (exported_data.status_code, 200)

    def test_export_csv_div_get(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).get(EXPORT_FORMATS[1])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual (exported_data.status_code, 200)

    def test_export_excel_get(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).get(EXPORT_FORMATS[2])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual (exported_data.status_code, 200)

    def test_export_excel_div_get(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).get(EXPORT_FORMATS[3])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual (exported_data.status_code, 200)

    def test_export_text_get(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).get(EXPORT_FORMATS[4])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual (exported_data.status_code, 200)

    def test_export_text_get2(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data).get(EXPORT_FORMATS[5])
        # now compare it with an already formatted data that we know is correct
        self.assertEqual (exported_data.status_code, 200)

    def test_search_no_payload(self):
        """
        Ensure that if no payload is passed in, returns 400
        """
        r = self.client.post('/search')
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, b'{"error": "no information received"}')

    def test_export_no_payload(self):
        """
        Ensure that if no payload is passed in, returns 400
        """
        r = self.client.post('/export')
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, b'{"error": "no information received"}')

    def test_search_no_payload_param(self):
        """
        Ensure that if payload without all the needed params is passed in, returns 400
        """
        r = self.client.post('/search', data=dict({'missingParamsPayload': ''}))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, b'{"error": "no bibcode found in payload (parameter name is `bibcode`)"}')

    def test_search_no_bibcode_payload(self):
        """
        Ensure that if payload without all the needed params is passed in, returns 400
        """
        r = self.client.post('/search', data=dict({'bibcode': ''}))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, b'{"error": "no bibcode submitted"}')

    def test_export_no_payload_param(self):
        """
        Ensure that if payload without all the needed params is passed in, returns 400
        """
        r = self.client.post('/export', data=dict({'missingParamsPayload': ''}))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, b'{"error": "no selection found in payload (parameter name is `selected`)"}')

    def test_payload_param_error_max_author(self):
        """
        Ensure that if payload without all the needed params is passed in, returns 400
        """
        payload = {'bibcode': ["1994AAS...185.4102A","1994AAS...185.4104E"], 'maxauthor':-1}
        r = self.client.post('/search', data=dict(payload))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, b'{"error": "parameter maxauthor should be a positive integer >= 0"}')


    def test_payload_param_error_cutoff_year(self):
        """
        Ensure that if payload without all the needed params is passed in, returns 400
        """
        payload = {'bibcode': ["1994AAS...185.4102A", "1994AAS...185.4104E"], 'numyears':-1}
        r = self.client.post('/search', data=dict(payload))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, b'{"error": "parameter numyears should be positive integer > 0"}')


    def test_payload_param_error_empty_selection(self):
        """
        Ensure that if payload without all the needed params is passed in, returns 400
        """
        payload = {'selected': '', 'format':''}
        r = self.client.post('/export', data=dict(payload))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, b'{"error": "no selection submitted"}')


    def test_payload_param_error_wrong_format(self):
        """
        Ensure that if payload without all the needed params is passed in, returns 400
        """
        payload = {'selected': ["Accomazzi, A.||2017/09"], 'format':''}
        r = self.client.post('/export', data=dict(payload))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, b'{"error": "unrecognizable export format specified"}')


    def test_payload_param_error_unrecognizable_format(self):
        """
        Ensure that if payload without a correct format params is passed in, returns 400
        """
        payload = {'selected': ["Accomazzi, A.||2017/09"], 'format':'something wrong'}
        r = self.client.post('/export', data=dict(payload))
        status = r.status_code
        response = r.data
        self.assertEqual(status, 400)
        self.assertEqual(response, b'{"error": "unrecognizable export format specified"}')

    def test_is_number(self):
        """
        Ensure is_number behaves properly
        """
        self.assertEqual(is_number('1'), True)
        self.assertEqual(is_number('-1'), True)
        self.assertEqual(is_number('notnumber'), False)

    def test_xml_status(self):
        solr_data = \
            {
               "responseHeader":{
                  "status":0,
                  "QTime":1,
                  "params":{
                     "sort":"date desc",
                     "fq":"{!bitset}",
                     "rows":"19",
                     "q":"*:*",
                     "start":"0",
                     "wt":"json",
                     "fl":"author,aff,pubdate"
                  }
               }
            }
        formatted_data = Formatter(solr_data)
        self.assertEqual(formatted_data.get_status(), 0)

    def test_xml_no_num_docs(self):
        solr_data = \
            {
               "responseHeader":{
                  "status":1,
                  "QTime":1,
                  "params":{
                     "sort":"date desc",
                     "fq":"{!bitset}",
                     "rows":"19",
                     "q":"*:*",
                     "start":"0",
                     "wt":"json",
                     "fl":"author,aff,pubdate"
                  }
               }
            }
        formatted_data = Formatter(solr_data)
        self.assertEqual(formatted_data.get_num_docs(), 0)

    def test_formatted_data_with_no_aff(self):
        """
        test the case with missing affiliation from solr record
        """
        # format the stubdata using the code
        formatted_data = Formatter(solrdata.data2).get(0, 2016)
        self.assertEqual(len(formatted_data), len(formatted.data))
        # now compare it with an already formatted data that we know is correct
        self.assertEqual(formatted_data, formatted.data2)


if __name__ == '__main__':
  unittest.main()