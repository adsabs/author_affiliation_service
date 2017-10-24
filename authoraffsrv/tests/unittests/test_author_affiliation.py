# -*- coding: utf-8 -*-

import sys
import os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(PROJECT_HOME)

import unittest
import authoraffsrv.app as app

class TestAuthorAffiliation(unittest.TestCase):
    def setUp(self):
        self.app = app.create_app().test_client()

    def test_route(self):
        """
        Tests for the existence of a /authoraff route, and that it returns
        properly formatted JSON data
        """
        payload = {'bibcode': ["1994AAS...185.4102A","1994AAS...185.4104E","1992SPIE.1657..535A","1989LNP...329..191A","2007AAS...211.4730K"]}
        r= self.app.post('/authoraff', data=dict(payload), headers={'User-Agent': 'ADS Script Request Agent'})
        self.assertEqual(r.status_code, 200)

if __name__ == '__main__':
  unittest.main()