from lxml import html
import requests
import re
import yaml
import copy
from string import Template
from datetime import datetime, timedelta
from dateutil.rrule import * # Import rrule and coresponding date, day, time enums

class SiteScraper(object):
    urlTemplate = Template('http://www.recreation.gov/camping/${name}/r/campsiteDetails.do?contractCode=${contract_code}&parkId=${park_id}')
    sites_available_pattern = re.compile('^(\d+)')
    sites_available_css_path = 'div.matchSummary'
    book_site_link_css_path = 'a.book.now'
    data = {
        # 'contractCode':'NRSO',
        # 'parkId':72393,
        # 'siteTypeFilter':'ALL',
        'submitSiteForm':'true',
        'search':'site',
        'currentMaximumWindow':12,
        # 'arrivalDate':'Mon Jun 13 2016',
        # 'departureDate':'Wed Jun 15 2016'
    }
    season_end_date=datetime.strptime('Oct 31 2016', '%b %d %Y')
    headers = {
        'Origin': 'http://www.recreation.gov',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'DNT': '1',
    }
    def __init__(self, site):
        self.site = site
        self.url = self.urlTemplate.substitute(site)
        self.headers['Referer'] = self.url
        self.init_cookies()
        self.data['parkId'] = site['park_id']
        self.data['contractCode'] = site['contract_code']
        self.dates = self.init_dates()
    def init_dates(self):
        datetime.now()
        weekends = rrule(DAILY, until=self.season_end_date, byweekday=(FR), bysetpos=1, dtstart=datetime.now())
        dates = list()
        for date in weekends:
            date_string_format = '%m/%d/%Y'
            sunday = date + timedelta(days=2)
            friday_string = datetime.strftime(date, date_string_format)
            sunday_string = datetime.strftime(sunday, date_string_format)
            dates.append((friday_string, sunday_string))
        return dates
    def run(self):
        data = self.build_form_data_for_site()
        for formdata in data:
            self.check_site(formdata)
    def build_form_data_for_site(self):
        all_data = list()
        # for each site type
        for site_type in self.site['site_types']:
            form_data = copy.deepcopy(self.data)
            form_data['siteTypeFilter'] = site_type
            # for each date
            for date_set in self.dates:
                # if it has loops
                form_data['arrivalDate'] = date_set[0]
                form_data['departureDate'] = date_set[1]
                if len(self.site['loops']) > 0:
                    for loop in self.site['loops']:
                        form_data['loop'] = loop
                        all_data.append(copy.deepcopy(form_data))
                # else add the current form_data
                else:
                    all_data.append(copy.deepcopy(form_data))
        return all_data;
    def init_cookies(self):
        self.session = requests.Session()
        self.session.get('http://www.recreation.gov')
        # TODO: Health check here?
    def check_site(self, formdata):
        s = self.session
        page = s.post('http://www.recreation.gov/campsiteSearch.do', headers=self.headers, data=formdata)
        tree = html.fromstring(page.content)
        # print  page.content
        sites_available_element = tree.cssselect(self.sites_available_css_path)
        if (len(sites_available_element) > 0):
            text = sites_available_element[0].text
            match = self.sites_available_pattern.match(text)
            site_count_string = match.group(0)
            site_count = int(site_count_string)
            output = Template('Found ${site_count} available sites for ${site_name} ${url}')
            print output.substitute(site_count=site_count, site_name=self.site['name'], url=self.url)
            # TODO: email teh peeps
        else:
            page.content
            print 'error checking site'
    # def email(self, user):

with open('./sites.yml') as sites_file:
    sites = yaml.load(sites_file)
    print sites
    point_reyes = SiteScraper(sites['campsites']['point_reyes'])
    point_reyes.run()
