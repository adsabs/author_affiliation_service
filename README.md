[![Build Status](https://travis-ci.org/adsabs/author_affiliation_service.svg)](https://travis-ci.org/adsabs/author_affiliation_service)
[![Coverage Status](https://coveralls.io/repos/adsabs/author_affiliation_service/badge.svg)](https://coveralls.io/r/adsabs/author_affiliation_service)


# ADS Author Affiliation Service

## Short Summary

This microservice creates author/affiliation spreadsheets. This is a two-step process. 

In the first step a list of bibcodes along with two optional parameters are submitted to endpoint /search. The two optional parameters are: number-of-authors to return for each record, and number-of-years, from current year, to include in the query. If the optional parameters are omitted, the default for number-of-authors is to include all authors, and for number-of-years to include the recent 4 years. Note that to have all years included simply set the parameter number-of-years to the current year (ie, 2018).

Note that because of number-of-years threshold, not all the submitted bibcodes would be considered. For example, if 200 bibcodes are submitted, and number-of-years is set to include the current year only, then only those records that were published this year are considered, which might include a small number of the original 200 bibcodes.

Also note that number of unique authors returned depends on how many of the articles have a common first number-of-authors author. For example, if all the articles were authored by the same author at the same affiliation and number-of-authors is set to 1, only one author/affiliation is returned. The same author having multiple affiliations would result in multiple returned records.

In the second step a list of selected author/affiliation/publication date is submitted to endpoint /export be formatted by one of the 6 available spreadsheet formats.



## Setup (recommended)

    $ virtualenv python
    $ source python/bin/activate
    $ pip install -r requirements.txt
    $ pip install -r dev-requirements.txt
    $ vim local_config.py # edit, edit



## Testing

On your desktop run:

    $ py.test



## API

#### Make a request:

    curl -H "Authorization: Bearer <your API token>" -H "Content-Type: application/json" -X POST -d <payload> <endpoint>

### Step 1: Get Data

To get data the
* `<endpoint>` is `https://api.adsabs.harvard.edu/v1/author-affiliation/search`, and
* `<payload>` should contain a JSON code of a list of comma separated 
bibcodes, and two optional parameters, maxauthor (num of authors to consider 
for each article, default is 0, to include all) and numyears 
(only include articles with publication year in the past numyears years, default is past 4 years)


For example to return *all* authors and their affiliations for the past *4 years* of the two articles with bibcodes 2017arXiv170909566R, 2016SPIE.9910E..0AM, you would do   

    curl -H "Authorization: Bearer <your API token>" -H "Content-Type: application/json" -X POST -d '{"bibcode":["2017arXiv170909566R","2016SPIE.9910E..0AM"],"maxauthor":0, "numyears":4}' https://api.adsabs.harvard.edu/v1/author-affiliation/search


### Step 2: Format Data

To format data the
* `<endpoint>` is `https://api.adsabs.harvard.edu/v1/author-affiliation/export`, and
* `<payload>` should contain a JSON code of a list of comma separated three-value fields 
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

For example to output a spreadsheet using the *text* format, for the two publications of *Accomazzi, A.*, you would do

    curl -H "Authorization: Bearer <your API token>" -H "Content-Type: application/json" -X POST -d '{"selected":["Accomazzi, A.|Harvard-Smithsonian Center for Astrophysics, Cambridge, USA|2015/04", "Accomazzi, A.|SAO/NASA Astrophysics Data System, USA|2015/04"], "format":"Lastname, Firstname(Affiliation)Last Active Date[text]"}' https://api.adsabs.harvard.edu/v1/author-affiliation/export`
    


## Maintainers

Golnaz, Tim
