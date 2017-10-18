'''
Created on May 11, 2011
@author: Giovanni Di Milia
'''

import sys
import os

from os.path import dirname, abspath
basedir = dirname(abspath(__file__)) + '/'
sys.path.append(basedir)

import xlwt
import uuid
from operator import itemgetter

import settings
#import the webpy module
import web

#import the function to canonicalize the bibcodes
sys.path.append('/proj/ads/soft/python/lib/site-packages')
#from ads.ADSExports_libxml2 import ADSRecords
from ads.ADSFacets_libxml2 import ADSRecords

web.config.debug = False

#create a new global vars for the base url
globals_vars = {'base_url' : settings.BASE_RELATIVE}

#urls
urls = (
    '', 'index',
    '/', 'index',
    '/export','export',
    '/export/','export',
    '/.*', 'other'
)

#initialize the application
app = web.application(urls, globals())

class index(object):
    """Main class that renders the first page"""
    def __init__(self):
        """ Constructor"""
        pass
    def POST(self):
        """manager of the post requests"""
        #for the post requests I simply call the GET handler 
        return self.GET()
    def GET(self):
        """manager of the get requests"""
        #I define the render
        render = web.template.render(basedir + 'templates/', base='layout', globals=globals_vars)
        
        #get the get input to extract the query type
        params = web.input(bibcodes=None)
        
        if not params.bibcodes:
            return render.basic_form()
        else:
            #I extract the bibcodes
            bibcodes_str = params.bibcodes
            #I split the string
            bibcodes_list = bibcodes_str.splitlines()
            #for each element of the string I split on the comma
            tmpbibcodes_list = []
            for elem in bibcodes_list:
                tmpbibcodes_list = tmpbibcodes_list + elem.split(',')
            #then I overwrite the list
            bibcodes_list = tmpbibcodes_list
            bibcodes_list = [s.strip().encode('ascii') for s in bibcodes_list]
            
            #I extract the bibcodes
            def_mode='full' 
            def_type='XML'
            facets=['affiliations']
            adsexp = ADSRecords(def_mode, def_type, facets)
            for bibcode in bibcodes_list:
                try:
                    adsexp.addRecord(bibcode)
                except:
                    pass
            #I export the tree
            cdoc = adsexp.export()
            #print cdoc.serialize('UTF-8', 2)
            
            #dictionary with data to return
            auth_aff={}
            #I extract authors and affiliations
            ctxt = cdoc.xpathNewContext()
            records = ctxt.xpathEval('/records/record')
            for record in records:
                # I set the contextual note to the current one
                ctxt.setContextNode(record)
                #I extract the bibcode
                bibcode_node = ctxt.xpathEval('bibcode')
                try:
                    bibcode = bibcode_node[0].content
                    year = bibcode[0:4]
                except IndexError:
                    continue
                
                #I extract all the author nodes
                authors = ctxt.xpathEval('author')
                for author in authors:
                    ctxt.setContextNode(author)
                    #I extract the author name
                    auth_name_node = ctxt.xpathEval('name/western')
                    try:
                        auth_name = auth_name_node[0].content
                        #I create a dictionary with this author name to insert all the affiliations
                        try:
                            auth_aff[auth_name]
                        except KeyError:
                            auth_aff[auth_name] = {}
                    #in case there is no western name I skip it and I continue to the next one
                    except IndexError:
                        continue
                    #then I extract all the affliations for each name
                    affiliations = ctxt.xpathEval('affiliations/affiliation')
                    for affiliation in affiliations:
                        try:
                            auth_aff[auth_name][affiliation.content].append(year)
                        except KeyError:
                            auth_aff[auth_name][affiliation.content] = [year]
            
            # I free the objects
            ctxt.xpathFreeContext()
            cdoc.freeDoc()
                        
            #I unique each list of year for each affiliation
            auth_aff_new = {}
            for author in auth_aff:
                auth_aff_new[author] = {}
                for aff in auth_aff[author]:
                    auth_aff_new[author][aff] = dict(map(lambda i: (i,1),auth_aff[author][aff])).keys()
                    (auth_aff_new[author][aff]).sort(reverse=True)
            
            #then I change data structure to make the authors to point a sorted list of affiliations
            auth_aff_new_sorted = {}
            for author in auth_aff_new:
                #I extract the affiliations
                affs = auth_aff_new[author]
                #and I sort the dates connected
                for el in affs:
                    affs[el].sort(reverse=True)
                #i extract the affiliation and the dates as tuples
                items = affs.items()
                #and I sort them
                items.sort(key = itemgetter(1), reverse=True)
                #the I insert the new structure in the dictionary
                auth_aff_new_sorted[author] = items
            
            #methods I need in the template
            methods_pers = {'str' : str}
            
            return render.author_list(auth_aff_new_sorted, methods_pers)


class export(object):
    """Method to export the content passed"""
    def __init__(self):
        """ Constructor"""
        pass
    
    def export_to_csv(self, alldata):
        """function that exports the data in CSV"""
        #then I create the final string
        csv_string = ''
        #first I extract the author names
        author_to_view = alldata.keys()
        author_to_view.sort()
        for auth in author_to_view:
            csv_string = csv_string + '"' + auth + '",'
            for aff in alldata[auth]:
                csv_string = csv_string + '"' + aff.replace('"', '\"') + '",'
            csv_string = csv_string + '\n'
        return csv_string
    
    def export_to_csv_div(self, alldata):
        """function that exports the data in CSV"""
        #then I create the final string
        csv_string = ''
        #first I extract the author names
        author_to_view = alldata.keys()
        author_to_view.sort()
        for auth in author_to_view:
            #I split the author name on the first comma
            auth_split = auth.split(',', 1)
            try:
                auth_split[1]
            except IndexError:
                auth_split.append('')
            csv_string = csv_string + '"' + auth_split[0] + '","' + auth_split[1] + '",'
            for aff in alldata[auth]:
                csv_string = csv_string + '"' + aff.replace('"', '\"') + '",'
            csv_string = csv_string + '\n'
        return csv_string
    
    def export_to_excel(self, alldata):
        """function to export the data in excel"""
        # Create workbook and worksheet
        wbk = xlwt.Workbook(encoding='UTF-8')
        sheet = wbk.add_sheet('ADS_Author-Affiliation')
        
        #counter of rows
        row = 0
        #first I extract the author names
        author_to_view = alldata.keys()
        author_to_view.sort()
        for auth in author_to_view:
            #I write the author name
            sheet.write(row, 0, auth)
            #then I write the affiliations
            col = 1
            for aff in alldata[auth]:
                sheet.write(row, col, aff)
                col +=1
            row+=1
        
        #I save the spreadsheet to a temporary file
        filename = settings.TMP_FOLDER + 'ADS_Author-Affiliation' + str(uuid.uuid4())
        wbk.save(filename)
        
        #I read the temporary file
        xls_file = open(filename)
        xls_str = xls_file.read()
        xls_file.close()
        #then I remove the file
        os.remove(filename)
        return xls_str
    
    def export_to_excel_div(self, alldata):
        """function to export the data in excel with the author name separated"""
        # Create workbook and worksheet
        wbk = xlwt.Workbook(encoding='UTF-8')
        sheet = wbk.add_sheet('ADS_Author-Affiliation')
        
        #counter of rows
        row = 0
        #first I extract the author names
        author_to_view = alldata.keys()
        author_to_view.sort()
        for auth in author_to_view:
            #I split the author name on the first comma
            auth_split = auth.split(',', 1)
            try:
                auth_split[1]
            except IndexError:
                auth_split.append('')
            #I write the author name
            sheet.write(row, 0, auth_split[0])
            sheet.write(row, 1, auth_split[1])
            #then I write the affiliations
            col = 2
            for aff in alldata[auth]:
                sheet.write(row, col, aff)
                col +=1
            row+=1
        
        #I save the spreadsheet to a temporary file
        filename = settings.TMP_FOLDER + 'ADS_Author-Affiliation' + str(uuid.uuid4())
        wbk.save(filename)
        
        #I read the temporary file
        xls_file = open(filename)
        xls_str = xls_file.read()
        xls_file.close()
        #then I remove the file
        os.remove(filename)
        return xls_str
    
    def export_to_text(self, alldata):
        """method that creates a text format"""
        #then I create the final string
        txt_string = ''
        #first I extract the author names
        author_to_view = alldata.keys()
        author_to_view.sort()
        for auth in author_to_view:
            txt_string = txt_string + auth + ' ('
            for aff in alldata[auth]:
                txt_string = txt_string + aff + '; '
            txt_string = txt_string + ')\n'
        return txt_string
    
    def GET(self):
        """manager of the get requests"""
        render = web.template.render(basedir + 'templates/', base='layout', globals=globals_vars)
        web.ctx.status = '405 Method Not Allowed'
        return render.get_not_allowed()
    
    def POST(self):
        """manager of the post requests"""
        #get the get input to extract the query type
        params = web.input(authors_number=None, export_type=None)
        
        #I check that everything is ok
        if params.authors_number==None or params.export_type==None:
            return 'Invalid parameters'
        
        #then I parse the parameters
        #I retrieve the total numbers of author I can expect
        authors_number = int(params.authors_number)
        #then I try to reconstruct the data passed
        alldata = {}
        for i in range(authors_number):
            #I use as counter i+1 because the authors start from 1 and not 0
            counter = i+1
            #first I try to extract the author i
            try:
                author = params['author_' + str(counter)]
                alldata[author] = []
            except KeyError:
                continue
            
            #if there is an author there should be also some affiliations
            #I extract the max number of affiliation for that author
            max_aff = int(params['author_'+ str(counter) + '_affiliations'])
            #then I try to extract the single affiliations
            for j in range(max_aff):
                counterj = j+1
                try:
                    affiliation = params['author_' + str(counter) +'_affiliation_' + str(counterj)]
                    alldata[author].append(affiliation)
                except KeyError:
                    continue
        
        if params.export_type == 'submit_csv':
            csv_string = self.export_to_csv(alldata)
            web.header('Content-type', 'text/csv; charset=UTF-8');
            web.header('Content-disposition', 'attachment;filename=ADS_Author-Affiliation.csv')    
            return csv_string
        elif params.export_type == 'submit_csv_div':
            csv_string = self.export_to_csv_div(alldata)
            web.header('Content-type', 'text/csv; charset=UTF-8');
            web.header('Content-disposition', 'attachment;filename=ADS_Author-Affiliation.csv')    
            return csv_string
        elif params.export_type == 'submit_excel':
            xls_str = self.export_to_excel(alldata)
            web.header('Content-type', 'text/xls; charset=UTF-8');
            web.header('Content-disposition', 'attachment;filename=ADS_Author-Affiliation.xls')    
            return xls_str
        elif params.export_type == 'submit_excel_div':
            xls_str = self.export_to_excel_div(alldata)
            web.header('Content-type', 'text/xls; charset=UTF-8');
            web.header('Content-disposition', 'attachment;filename=ADS_Author-Affiliation.xls')    
            return xls_str
        elif params.export_type == 'submit_txt':
            txt_str = self.export_to_text(alldata)
            web.header('Content-type', 'text/plain; charset=UTF-8');
            web.header('Content-disposition', 'attachment;filename=ADS_Author-Affiliation.txt')    
            return txt_str
        elif params.export_type == 'submit_txt_browser':
            txt_str = self.export_to_text(alldata)
            web.header('Content-type', 'text/plain; charset=UTF-8');
            #web.header('Content-disposition', 'attachment;filename=ADS_Author-Affiliation.txt')    
            return txt_str
        else:
            return 'Format not supported'

class other(object):
    def __init__(self):
        """ Constructor"""
        pass
    def POST(self):
        """manager of the post requests"""
        #for the post requests I simply call the GET handler 
        return self.GET()
    def GET(self):
        """manager of the get requests"""
        render = web.template.render(basedir + 'templates/', base='layout', globals=globals_vars)

        web.ctx.status = '404 Not Found'
        return render.not_found()

#if __name__ == "__main__": 
#    app.run()
    
#to enable wsgi
application = app.wsgifunc()
