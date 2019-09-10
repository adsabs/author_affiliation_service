# -*- coding: utf-8 -*-

from flask import current_app, request, Blueprint, Response, redirect
from flask_discoverer import advertise
from flask import Response

import os
import sys
from os.path import dirname, abspath
basedir = dirname(abspath(__file__)) + '/'
sys.path.append(basedir)
import datetime
import re
import json
import xlwt
import uuid

from authoraffsrv.utils import get_solr_data


bp = Blueprint('ads_author_affilation_service', __name__)


EXPORT_FORMATS = [
    "| Lastname, Firstname | Affiliation | Last Active Date | [csv]",
    "| Lastname | Firstname | Affiliation | Last Active Date | [csv]",
    "| Lastname, Firstname | Affiliation | Last Active Date | [excel]",
    "| Lastname | Firstname | Affiliation | Last Active Date | [excel]",
    "Lastname, Firstname(Affiliation)Last Active Date[text]",
    "Lastname, Firstname(Affiliation)Last Active Date[browser]"
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

    def __init__(self, selected_authors):
        """

        :param selected: selected data
        """
        self.selected_authors = {}
        if len(selected_authors) > 0:
            for selected_author in selected_authors:
                values = selected_author.split('|')
                if (len(values) == 3):
                    self.selected_authors.setdefault(values[0], []).append(values[1] + '|' + values[2])

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
            for value in self.selected_authors[author]:
                [affiliation, last_active] = value.split('|')
                csv_string = csv_string + '"' + affiliation.replace('"', '\"') + '","' + last_active + '",'
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
            for value in self.selected_authors[author]:
                [affiliation, last_active] = value.split('|')
                csv_string = csv_string + '"' + affiliation.replace('"', '\"') + '","' + last_active + '",'
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
            for value in self.selected_authors[author]:
                [affiliation, last_active] = value.split('|')
                sheet.write(row, col, affiliation)
                sheet.write(row, col+1, last_active)
                col += 2
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
            for value in self.selected_authors[author]:
                [affiliation, last_active] = value.split('|')
                sheet.write(row, col, affiliation)
                sheet.write(row, col+1, last_active)
                col += 2
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
            for value in self.selected_authors[author]:
                [affiliation, last_active] = value.split('|')
                txt_string = txt_string + affiliation + '; ' + last_active + '; '
            txt_string = txt_string + ')\n'
        return txt_string


    def __return_response(self, response, content_type, content_disposition, status):
        """

        :param response:
        :param content_type:
        :param content_disposition:
        :param status:
        :return:
        """
        if status == 200:
            r = Response(response=response, status=status)
            r.headers['content-type'] = content_type
            r.headers['content-disposition'] = content_disposition
            r.headers['content-length'] = len(response)
            current_app.logger.info('returning results with status code 200')
            current_app.logger.info('the file size transferred is {length} KB'.format(length=len(response)))
        else:
            r = Response(response=json.dumps(response), status=status)
            r.headers['content-type'] = 'application/json'
            current_app.logger.error('{} status code = {}'.format(json.dumps(response), status))

        return r


    def format(self, export_format):
        """
        used for unit test
        :param export_format:
        :return:
        """
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
        return self.__return_response({'error': 'unrecognizable export format specified'}, 400)


    def get(self, export_format):
        """

        :param export_format:
        :return:
        """
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
                                   'application/vnd.ms-excel',
                                   'attachment;filename=ADS_Author-Affiliation.xls',
                                   200 if len(content) > 0 else 400)
        if export_format == EXPORT_FORMATS[3]:
            content = self.__export_to_excel_div()
            return self.__return_response(content,
                                   'application/vnd.ms-excel',
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
        return self.__return_response({'error': 'unrecognizable export format specified'}, 'application/json', '', 400)



class Formatter:
    """
    class to get the data from solr and format it for the form.
    """

    status = -1
    from_solr = {}

    def __init__(self, from_solr):
        """

        :param from_solr:
        """
        self.from_solr = from_solr
        if (self.from_solr.get('responseHeader')):
            self.status = self.from_solr['responseHeader'].get('status', self.status)


    def get_status(self):
        """

        :return:
        """
        return self.status


    def get_num_docs(self):
        """

        :return:
        """
        if (self.status == 0):
            if (self.from_solr.get('response')):
                return self.from_solr['response'].get('numFound', 0)
        return 0


    def __get_list(self, num_authors, cutoff_year):
        """
        get unique list of author affiliation
        :param num_authors: max number of authors to fetch for each article
        :param cut_offyear: do not include the year if it is less than this
        """
        if (self.status == 0):
            author_aff = []
            for index in range(self.get_num_docs()):
                a_doc = self.from_solr['response'].get('docs')[index]
                if 'author' in a_doc and 'aff' in a_doc and 'pubdate' in a_doc:
                    if (int(a_doc['pubdate'][:4]) >= cutoff_year):
                        author_list = a_doc['author']
                        aff_list = a_doc['aff']
                        if (num_authors != 0):
                            author_list = author_list[:num_authors]
                            aff_list = aff_list[:num_authors]
                        for author, aff in zip(author_list, aff_list):
                            idx = [idx for idx, elem in enumerate(author_aff) if elem[0] == author and elem[1] == aff]
                            if len(idx) > 0:
                                author_aff[idx[0]][2].update([a_doc['pubdate'][:4]])
                                author_aff[idx[0]][3] = a_doc['pubdate'] if a_doc['pubdate'] > author_aff[idx[0]][3] else author_aff[idx[0]][3]
                            else:
                                author_aff.append([author, aff, set([a_doc['pubdate'][:4]]), a_doc['pubdate']])
            return sorted(author_aff, key=lambda x: x[0])
        return None


    def __get_true_last_active_date(self, last_active_date):
        """

        :param last_active_date:
        :return: last active date without any 0 in month and date fields
        """
        parts = last_active_date.split('-')
        true_date = ''
        for part in parts:
            if (int(part) != 0):
                if (len(true_date) > 0):
                    true_date += '/'
                true_date += part
        return true_date


    def __to_json(self, the_list):
        """

        :param the_list:
        :return:
        """
        data = []
        for elem in the_list:
            affiliations = {}
            affiliations['name'] = elem[1]
            affiliations['years'] = sorted(elem[2], reverse=True)
            affiliations['lastActiveDate'] = self.__get_true_last_active_date(elem[3])

            item = {}
            item['authorName'] = elem[0]
            item['affiliations'] = affiliations

            data.append(item)

        the_json = {}
        the_json['data'] = data
        return json.dumps(the_json)


    def get(self, num_authors=0, cutoff_year=10):
        """

        :param num_authors:
        :param cutoff_year:
        :return:
        """
        the_list = self.__get_list(num_authors, cutoff_year)
        if the_list:
            return self.__to_json(the_list)
        return None


def return_response(response, status):
    """

    :param response:
    :param status:
    :return:
    """
    r = Response(response=json.dumps(response), status=status)
    r.headers['content-type'] = 'application/json'

    if status == 200:
        current_app.logger.debug('returning results with status code 200')
    else:
        current_app.logger.error('{} status code = {}'.format(json.dumps(response), status))

    return r


def is_number(s):
    """

    :param s:
    :return:
    """
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
    """

    :return:
    """
    try:
        payload = request.get_json(force=True)  # post data in json
    except:
        payload = dict(request.form)  # post data in form encoding

    if not payload:
        return return_response({'error': 'no information received'}, 400)
    elif 'bibcode' not in payload:
        return return_response({'error': 'no bibcode found in payload (parameter name is `bibcode`)'}, 400)

    bibcodes = payload['bibcode']
    if (len(''.join(bibcodes)) == 0):
        return return_response({'error': 'no bibcode submitted'}, 400)

    # default number of authors is to include all
    num_authors = 0
    try:
        if 'maxauthor' in payload:
            if type(payload['maxauthor']) is list:
                maxauthor = payload['maxauthor'][0]
            else:
                maxauthor = payload['maxauthor']
            if is_number(maxauthor) and int(maxauthor) >= 0:
                num_authors = int(maxauthor)
            else:
                return return_response({'error': 'parameter maxauthor should be a positive integer >= 0'}, 400)
    except (ValueError,KeyError):
        current_app.logger.debug('optional parameter maxauthor not passed in')

    # default is to include all years, lower limit is 1000, upper limit is 3000, and it is in utils
    cutoff_year = 1000
    try:
        if 'numyears' in payload:
            if type(payload['numyears']) is list:
                numyears = payload['numyears'][0]
            else:
                numyears = payload['numyears']
            if is_number(numyears) and int(numyears) >= 0:
                if int(numyears) == 0:
                    cutoff_year = 1000
                else:
                    cutoff_year = datetime.datetime.now().year - int(numyears)
            else:
                return return_response({'error': 'parameter numyears should be positive integer > 0'}, 400)
    except (ValueError,KeyError):
        current_app.logger.debug('optional parameter numyears not passed in')

    current_app.logger.info('received request with bibcodes={bibcodes} and using max number author={num_authors} and cutoff year={cutoff_year}'.format(
            bibcodes=bibcodes,
            num_authors=num_authors,
            cutoff_year=cutoff_year))

    from_solr = get_solr_data(bibcodes=bibcodes, cutoff_year=cutoff_year)
    if from_solr is not None:
        result = Formatter(from_solr).get(num_authors, cutoff_year)
        if result is not None:
            return return_response(result, 200)
    return return_response({'error': 'no result from solr'}, 404)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/export', methods=['POST'])
def export():
    """

    :return:
    """
    try:
        payload = request.get_json(force=True)  # post data in json
    except:
        payload = dict(request.form)  # post data in form encoding

    if not payload:
        return return_response({'error': 'no information received'}, 400)

    if 'selected' in payload:
        selected = payload['selected']
        if (len(''.join(selected)) == 0):
            return return_response({'error': 'no selection submitted'}, 400)
    else:
        return return_response({'error': 'no selection found in payload (parameter name is `selected`)'}, 400)

    if 'format' in payload:
        format = ''.join(payload['format'])
    else:
        return return_response({'error': 'no export format specified in payload (parameter name is `format`)'}, 400)

    current_app.logger.info('received request to export with selected={selected}'.format(selected=selected))
    return Export(selected).get(format)

