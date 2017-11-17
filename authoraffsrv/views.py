#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import inspect

from flask import current_app, request, Blueprint, Response, redirect
from flask import Flask, render_template, send_file
from flask_discoverer import advertise
from flask import Response

import requests
from collections import OrderedDict
import datetime
import re
import json
import xlwt
import uuid

from authoraffsrv.utils import get_solr_data


bp = Blueprint('ads_author_affilation_service', __name__)


EXPORT_FORMATS = [
    "| Lastname, Firstname | Affiliation | [csv]",
    "| Lastname | Firstname | Affiliation | [csv]",
    "| Lastname, Firstname | Affiliation | [excel]",
    "| Lastname | Firstname | Affiliation | [excel]",
    "Lastname, Firstname(Affiliation)[text]",
    "Lastname, Firstname(Affiliation)[browser]"
]


class Export(object):
    """
    Method to export the content selected on the form

    This class came from Classic and is used here with
    limited modification

    Created on May 11, 2011
    @author: Giovanni Di Milia
    """

    # temporary folder for excel files
    TMP_EXCEL_FOLDER = '/tmp/'

    # export file name
    EXPORT_FILENAME = 'ADS_Author-Affiliation'

    REGEX_SELECTED_ITEM = re.compile(r'id_(.+?)_aff_(.+?)?\s\(')

    def __init__(self, from_form):
        """
        parse data from form and put it in a dict
        :param from_form: data from form
        """
        self.selected_authors = {}
        if len(from_form) > 0:
            items = from_form.split('||')
            for item in items:
                match = self.REGEX_SELECTED_ITEM.match(item)
                if match:
                    self.__add_selected_author(match.group(1), match.group(2))


    def __add_selected_author(self, author, affiliation):
        if affiliation == None:
            affiliation = ''
        self.selected_authors.setdefault(author, []).append(affiliation)


    def __export_to_csv(self):
        """
        function that exports the data to CSV
        :return:
        """
        csv_string = ''
        authors = self.selected_authors.keys()
        authors.sort()
        for author in authors:
            csv_string = csv_string + '"' + author + '",'
            for affiliation in self.selected_authors[author]:
                csv_string = csv_string + '"' + affiliation.replace('"', '\"') + '",'
            csv_string = csv_string + '\n'
        return csv_string

    def __export_to_csv_div(self):
        """
        function that exports the data to CSV
        :return:
        """
        csv_string = ''
        authors = self.selected_authors.keys()
        authors.sort()
        for author in authors:
            author_split = author.split(',', 1)
            try:
                author_split[1]
            except IndexError:
                author_split.append('')
            csv_string = csv_string + '"' + author_split[0] + '","' + author_split[1] + '",'
            for affiliation in self.selected_authors[author]:
                csv_string = csv_string + '"' + affiliation.replace('"', '\"') + '",'
            csv_string = csv_string + '\n'
        return csv_string


    def __export_to_excel(self):
        """
        function to export the data to excel
        :return:
        """
        # Create workbook and worksheet
        wbk = xlwt.Workbook(encoding='UTF-8')
        sheet = wbk.add_sheet(self.EXPORT_FILENAME)

        row = 0
        authors = self.selected_authors.keys()
        authors.sort()
        for author in authors:
            sheet.write(row, 0, author)
            col = 1
            for affiliation in self.selected_authors[author]:
                sheet.write(row, col, affiliation)
                col += 1
            row += 1

        # save the spreadsheet to a temporary file
        filename = self.TMP_EXCEL_FOLDER + self.EXPORT_FILENAME + str(uuid.uuid4())
        wbk.save(filename)
        # now read it
        xls_file = open(filename)
        xls_str = xls_file.read()
        xls_file.close()
        # finally remove it
        os.remove(filename)
        return xls_str

    def __export_to_excel_div(self):
        """
        function to export the data to excel with the author name separated
        :return:
        """
        # Create workbook and worksheet
        wbk = xlwt.Workbook(encoding='UTF-8')
        sheet = wbk.add_sheet(self.EXPORT_FILENAME)

        row = 0
        authors = self.selected_authors.keys()
        authors.sort()
        for author in authors:
            # split the author name on the first comma
            author_split = author.split(',', 1)
            try:
                author_split[1]
            except IndexError:
                author_split.append('')
            # write the author name
            sheet.write(row, 0, author_split[0])
            sheet.write(row, 1, author_split[1])
            # write the affiliations
            col = 2
            for affiliation in self.selected_authors[author]:
                sheet.write(row, col, affiliation)
                col += 1
            row += 1

        # save the spreadsheet to a temporary file
        filename = self.TMP_EXCEL_FOLDER + self.EXPORT_FILENAME + str(uuid.uuid4())
        wbk.save(filename)
        # now read it
        xls_file = open(filename)
        xls_str = xls_file.read()
        xls_file.close()
        # finally remove it
        os.remove(filename)
        return xls_str


    def __export_to_text(self):
        """
        method that creates a text format
        :return:
        """
        txt_string = ''
        authors = self.selected_authors.keys()
        authors.sort()
        for author in authors:
            txt_string = txt_string + author + ' ('
            for affiliation in self.selected_authors[author]:
                txt_string = txt_string + affiliation + '; '
            txt_string = txt_string + ')\n'
        return txt_string


    def __return_response(self, response, content_type, content_disposition, status):

        r = Response(response=response, status=status)

        if status == 200:
            r.headers['content-type'] = content_type
            r.headers['content-disposition'] = content_disposition
            current_app.logger.debug('returning results with status code 200')
        else:
            r.headers['content-type'] = 'text/plain'
            current_app.logger.error('{} status code = {}'.format(response, status))

        return r


    def format(self, export_format):
        if export_format == EXPORT_FORMATS[0]:
            return self.__export_to_csv()
        if export_format == EXPORT_FORMATS[1]:
            return self.__export_to_csv_div()
        if export_format == EXPORT_FORMATS[2]:
            return self.__export_to_excel()
        if export_format == EXPORT_FORMATS[3]:
            return self.__export_to_excel_div()
        if export_format == EXPORT_FORMATS[4]:
            return self.__export_to_text()
        if export_format == EXPORT_FORMATS[5]:
            return self.__export_to_text()
        return ''


    def get(self, export_format):
        if export_format == EXPORT_FORMATS[0]:
            content = self.__export_to_csv()
            return self.__return_response(content,
                                   'text/csv; charset=UTF-8',
                                   'attachment;filename=ADS_Author-Affiliation.csv',
                                   200 if len(content) > 0 else 400)
        if export_format == EXPORT_FORMATS[1]:
            content = self.__export_to_csv_div()
            return self.__return_response(content,
                                   'text/csv; charset=UTF-8',
                                   'attachment;filename=ADS_Author-Affiliation.csv',
                                   200 if len(content) > 0 else 400)
        if export_format == EXPORT_FORMATS[2]:
            content = self.__export_to_excel()
            return self.__return_response(content,
                                   'text/xls; charset=UTF-8',
                                   'attachment;filename=ADS_Author-Affiliation.xls',
                                   200 if len(content) > 0 else 400)
        if export_format == EXPORT_FORMATS[3]:
            content = self.__export_to_excel_div()
            return self.__return_response(content,
                                   'text/xls; charset=UTF-8',
                                   'attachment;filename=ADS_Author-Affiliation.xls',
                                   200 if len(content) > 0 else 400)
        if export_format == EXPORT_FORMATS[4]:
            content = self.__export_to_text()
            return self.__return_response(content,
                                   'text/plain; charset=UTF-8',
                                   'attachment;filename=ADS_Author-Affiliation.txt',
                                   200 if len(content) > 0 else 400)
        if export_format == EXPORT_FORMATS[5]:
            content = self.__export_to_text()
            return self.__return_response(content,
                                   'text/plain; charset=UTF-8',
                                   '', #''Content-disposition', 'attachment;filename=ADS_Author-Affiliation.txt'
                                   200 if len(content) > 0 else 400)
        return self.__return_response('', '', '', 400)



class Formatter:
    """
    class to get the data from solr and format it for the form.
    """

    status = -1
    from_solr = {}

    def __init__(self, from_solr):
        self.from_solr = from_solr
        if (self.from_solr.get('responseHeader')):
            self.status = self.from_solr['responseHeader'].get('status', self.status)


    def get_status(self):
        return self.status


    def get_num_docs(self):
        if (self.status == 0):
            if (self.from_solr.get('response')):
                return self.from_solr['response'].get('numFound', 0)
        return 0


    def __union(self, a, b, cutoff_year):
        """
        :param a: first list
        :param b: second list
        :param cutoff_year: do not include a record if its year is less than this
        :return: union of two lists
        """
        if len(a) == 0:
            for y in b:
                if int(y[2]) < cutoff_year:
                    b.remove(y)
            return b
        if len(b) == 0:
            for x in a:
                if int(x[2]) < cutoff_year:
                    a.remove(x)
            return a
        # find the records that exist in a and need to be updated by the year of a b element
        update_year = [y for y in b if any(x[0] == y[0] and x[1] == y[1] for x in a)]
        for y in update_year:
            for i, x in enumerate(a):
                if y[2] not in x[2] and int(y[2]) >= cutoff_year:
                    a[i] = (x[0], x[1], x[2] + ', ' + y[2])
        # the rest of b are the new elements that need to be added to a
        add_in = list(set(b) - set(update_year))
        for y in add_in:
            if int(y[2]) >= cutoff_year:
                a.append(y)
        return a


    def __get_list(self, max_author, cutoff_year):
        """
        get unique list of author affiliation
        :param max_author: max number of authors to fetch for each article
        :param cut_offyear: do not include the year if it is less than this
        """
        if (self.status == 0):
            author_aff = []
            for index in range(self.get_num_docs()):
                a_doc = self.from_solr['response'].get('docs')[index]
                year = a_doc['year'] if 'year' in a_doc else None
                if 'author' in a_doc and 'aff' in a_doc:
                    one_set = list((author, aff if aff != '-' else None, year) for author, aff in zip(a_doc['author'], a_doc['aff']))
                    if (max_author != 0):
                        one_set = one_set[:max_author+1]
                    author_aff = self.__union(author_aff, one_set, cutoff_year)
            return author_aff
        return None


    def __merge_aff(self, the_list):
        """
        for each author merge their affiliation and publication year, and then return a sorted dict
        :param the_list:
        """
        the_dict = {}
        for item in the_list:
            the_dict.setdefault(item[0], []).append(item[1] + ' (' + item[2] + ')' if item[1]  != None else '' + ' (' + item[2] + ')')
        return OrderedDict(sorted(the_dict.items()))


    def __to_json(self, the_dict):
        data = []
        for key, values in the_dict.iteritems():
            for value in values:
                name, years = value.split(' (', 1)

                affiliations = {}
                affiliations['name'] = name.rstrip()
                affiliations['years'] = years.rstrip(')').split(', ')

                item = {}
                item['authorName'] = key
                item['affiliations'] = affiliations

                data.append(item)

        the_json = {}
        the_json['data'] = data
        return json.dumps(the_json)


    def get(self, max_author=0, cutoff_year=10):
        the_list = self.__get_list(max_author, cutoff_year)
        if the_list:
            return self.__to_json(self.__merge_aff(the_list))
        return None


def __return_response(response, status):
    r = Response(response=response, status=status)

    if status == 200:
        r.headers['content-type'] = 'application/json'
        current_app.logger.debug('returning results with status code 200')
    else:
        r.headers['content-type'] = 'text/plain'
        current_app.logger.error('{} status code = {}'.format(response, status))

    return r


def __is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/search', methods=['POST'])
def search():
    try:
        payload = request.get_json(force=True)  # post data in json
    except:
        payload = dict(request.form)  # post data in form encoding

    if not payload:
        return __return_response('error: no information received', 400)
    elif 'bibcodes' not in payload:
        return __return_response('error: no bibcodes found in payload (parameter name is "bibcodes")', 400)

    bibcodes = payload['bibcodes']
    # default number of authors is to include all
    max_author = 0
    if 'maxauthor' in payload:
        maxauthor = payload['maxauthor']
        if (maxauthor < 0):
            return __return_response('error: parameter maxauthor should be 0 or a positive integer', 400)
        max_author = maxauthor
    # default cutoff is 10 years from today
    cutoff_year = datetime.datetime.now().year - 10
    if 'cutoffyear' in payload:
        cutoffyear = payload['cutoffyear']
        if (cutoffyear < 1900):
            return __return_response('error: parameter cutoffyear should be a year >= 1900', 400)
        cutoff_year = cutoffyear

    current_app.logger.info('received request with bibcodes={bibcodes} and using max number author={max_author} and cutoff year={cutoff_year}'.format(
    bibcodes=bibcodes,
    max_author=max_author,
    cutoff_year=cutoff_year))

    from_solr = get_solr_data(bibcodes=bibcodes)
    if from_solr is not None:
        result = Formatter(from_solr).get(max_author, cutoff_year)
        if result is not None:
            return __return_response(result, 200)
    return __return_response('error: no result from solr', 404)


# todo: modify after tim created his page
@bp.route('/export_selection_top', methods=['POST'])
def export_selection_top():
    jsonData = json.loads(request.form['selected_info_top'])
    return Export(jsonData['selected']).get(jsonData['format'])
@bp.route('/export_selection_bottom', methods=['POST'])
def export_selection_bottom():
    jsonData = json.loads(request.form['selected_info_bottom'])
    return Export(jsonData['selected']).get(jsonData['format'])
