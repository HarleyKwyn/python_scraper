from lxml import html
import requests
import re
import yaml
import copy
from string import Template
from datetime import datetime, timedelta
from dateutil.rrule import * # Import rrule and coresponding date, day, time enums

urlTemplate = Template('http://www.recreation.gov/camping/${name}/r/campsiteDetails.do?contractCode=${contract_code}&parkId=${park_id}')
campsite = {
    'name': 'Point_Reyes_National_Seashore_Campground',
    'contract_code': 'NRSO',
    'site_id': 318005,
    'park_id': 72393
}
url = urlTemplate.substitute(campsite)
s = requests.Session()
s.get('http://www.recreation.gov')
s.get(url)

# TODO make this generalized for all sites
headers = {
    'Origin': 'http://www.recreation.gov',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer':'http://www.recreation.gov/camping/point-reyes-national-seashore-campground/r/campgroundDetails.do?contractCode=NRSO&parkId=72393',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'DNT': '1'
}
data = {
    'contractCode':'NRSO',
    'parkId':72393,
    'siteTypeFilter':'ALL',
    # availStatus:,
    'submitSiteForm':'true',
    'search':'site',
    'currentMaximumWindow':12,
    'arrivalDate':'08/19/2016',
    'departureDate':'08/25/2016'
}
print data
print headers
page = s.post('http://www.recreation.gov/campsiteSearch.do',headers=headers,data=data)
tree = html.fromstring(page.content)
sites_available_pattern = re.compile('^(\d+)')
sites_available_element = tree.cssselect('div.matchSummary')
if (len(sites_available_element) > 0):
    text = sites_available_element[0].text
    match = sites_available_pattern.match(text)
    site_count_string = match.group(0)
    site_count = int(site_count_string)
    print site_count
    # TODO: email teh peeps
else:
    print 'error checking site'
