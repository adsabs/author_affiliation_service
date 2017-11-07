[![Build Status](https://travis-ci.org/adsabs/ADSAuthorAffiliationService.svg?branch=master)](https://travis-ci.org/adsabs/ADSAuthorAffiliationService)
[![Coverage Status](https://coveralls.io/repos/adsabs/ADSAuthorAffiliationService/badge.svg?branch=master)](https://coveralls.io/r/adsabs/ADSAuthorAffiliationService?branch=master)

# ADSAuthorAffiliationService
A service for creating author/affiliation spreadsheets

#### Make a request:

`curl -H "Content-Type: application/json" -X POST -d <payload> <endpoint>`


* where `<endpoint>` is /authoraff,
* and `<payload>` should contain a JSON code of a list of comma separated 
bibcodes, and two optional parameters, maxauthor (num of authors to consider 
for each article, default is 0, to include all) and cutoffyear 
(only include articles with publication year included and after 
this, default is 10 years)
