# ADSAuthorAffiliationService
A service for creating author/affiliation spreadsheets

#### Make a request:

`curl -H "Content-Type: application/json" -X POST -d <payload> <endpoint>`


* where `<endpoint>` is /authoraff,
* and `<payload>` should contain list of comma separated bibcodes, 
and two optional parameters, maxauthor (num of authors to consider 
for each article, default is 0, to include all) and cutoffyear 
(only include articles with publication year included and after 
this, default is 10 years)
