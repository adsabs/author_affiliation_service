# -*- coding: utf-8 -*-

import sys
import os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(PROJECT_HOME)

import datetime

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
        formatted_data = Formatter(solrdata.data).get(0, datetime.datetime.now().year - 10)
        # now compare it with an already formatted data that we know is correct
        assert(formatted_data == formatted.data)

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

    def test_export_text(self):
        # format the stubdata using the code
        exported_data = Export(export.form_data.replace('\n', '').replace('\r', '')).format(EXPORT_FORMATS[4])
        # now compare it with an already formatted data that we know is correct
        assert(exported_data == export.text)

if __name__ == '__main__':
  unittest.main()