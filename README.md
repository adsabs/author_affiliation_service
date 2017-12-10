[![Build Status](https://travis-ci.org/adsabs/author_affiliation_service.svg?branch=master)](https://travis-ci.org/adsabs/author_affiliation_service)
[![Coverage Status](https://coveralls.io/repos/adsabs/author_affiliation_service/badge.svg?branch=master)](https://coveralls.io/r/adsabs/author_affiliation_service?branch=master)

# Author Affiliation Service
A service for creating author/affiliation spreadsheets

#### Make a request:

`curl -H "Content-Type: application/json" -X POST -d <payload> <endpoint>`

##### Step 1: get data to display to user

* where `<endpoint>` is /search,
* and `<payload>` should contain a JSON code of a list of comma separated 
bibcodes, and two optional parameters, maxauthor (num of authors to consider 
for each article, default is 0, to include all) and numyears 
(only include articles with publication year in the past numyears years, default is past 4 years)

For example

`curl -H "Content-Type: application/json" -X POST -d '{"bibcode":["2017arXiv170909566R","2016SPIE.9910E..0AM"],"maxauthor":0, "cutoffyear":4}' http://localhost:5000/search`

##### Step 2: send selected data by user to spreadsheet

* where `<endpoint>` is /export,
* and `<payload>` should contain a JSON code of a list of comma separated three-value fields 
of author, affiliation, and last active date, separated by a '|', and export format that 
is one of the followings:
`

    "| Lastname, Firstname | Affiliation | Last Active Date | [csv]"
    
    "| Lastname | Firstname | Affiliation | Last Active Date | [csv]"
    
    "| Lastname, Firstname | Affiliation | Last Active Date | [excel]"
    
    "| Lastname | Firstname | Affiliation | Last Active Date | [excel]"
    
    "Lastname, Firstname(Affiliation)Last Active Date[text]"
    
    "Lastname, Firstname(Affiliation)Last Active Date[browser]"
`

For example

`curl -H "Content-Type: application/json" -X POST -d '{"selected":"Accomazzi, A.|Harvard-Smithsonian Center for Astrophysics, Cambridge, USA|2015/04", "Accomazzi, A.|SAO/NASA Astrophysics Data System, USA|2015/04", "format":"Lastname, Firstname(Affiliation)Last Active Date[text]"}' http://localhost:5000/export`
