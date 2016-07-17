from lxml import html
from urlparse import urlparse, parse_qs
import requests
import re
import yaml
import copy
from notifications import Notifications
from string import Template
from datetime import datetime, timedelta
from dateutil.rrule import * # Import rrule and coresponding date, day, time enums
import time, threading
def foo():
    print(time.ctime())
    threading.Timer(10, foo).start()
'''
build api that will accept request with
- email address
- Arrival date
- length of stay
'''

class SiteScraper(object):
    urlTemplate = Template('http://www.recreation.gov/camping/${name}/r/campsiteDetails.do?contractCode=${contract_code}&parkId=${park_id}')
    sites_available_pattern = re.compile('^(\d+)')
    sites_available_css_path = 'div.matchSummary'
    book_site_link_css_path = 'a.book.now'
    date_string_format = '%m/%d/%Y'
    data = {
        # 'contractCode':'NRSO',
        # 'parkId':72393,
        'siteTypeFilter':'ALL',
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

    def __init__(self, site, user_preferences):
        self.contact_methods = user_preferences['contact_methods']
        self.dates = user_preferences['arrival_dates']
        self.length_of_stay = user_preferences['length_of_stay']
        self.site = site
        self.url = self.urlTemplate.substitute(site)
        self.headers['Referer'] = self.url
        self.init_cookies()
        self.data['parkId'] = site['park_id']
        self.data['contractCode'] = site['contract_code']
        self.notifications = Notifications()
    #
    # def init_dates(self):
    #     datetime.now()
    #     weekends = rrule(DAILY, until=self.season_end_date, byweekday=(FR), bysetpos=1, dtstart=datetime.now())
    #     dates = list()
    #     for date in weekends:
    #         date_string_format = '%m/%d/%Y'
    #         sunday = date + timedelta(days=self.length_of_stay)
    #         friday_string = datetime.strftime(date, date_string_format)
    #         sunday_string = datetime.strftime(sunday, date_string_format)
    #         dates.append((friday_string, sunday_string))
    #     return dates
    def clean_up_dates():
        valid_dates = list();
        for date in self.dates:
            if datetime.strptime(date, self.date_string_format) > datetime.now():
                list.append(date)
        self.dates = valid_dates

    def run(self):
        data = self.build_form_data_for_site()
        print 'built formdata for ' + self.site['name']
        for formdata in data:
            self.check_site(formdata)
        self.notifications.close_smtp_connection()
        self.clean_up_dates()
        if len(self.dates) > 0:
            five_minutes = 300000
            threading.Timer(3000, self.run).start()
    def build_form_data_for_site(self):
        date_string_format = self.date_string_format = '%m/%d/%Y'
        all_data = list()
        # for each site type
        for site_type in self.site['site_types']:
            form_data = copy.deepcopy(self.data)
            form_data['lookingFor'] = site_type
            # for each date
            for date in self.dates:
                form_data['arrivalDate'] = date
                departureDate = datetime.strptime(date, date_string_format) + timedelta(days=self.length_of_stay)
                form_data['departureDate'] = datetime.strftime(departureDate, date_string_format)
                # if it has loops
                if 'loops' in self.site:
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
        print 'checking date ' + formdata['arrivalDate']
        # Arrival date
        arvdate = formdata['arrivalDate']
        s = self.session
        page = s.post('http://www.recreation.gov/campsiteSearch.do', headers=self.headers, data=formdata)
        tree = html.fromstring(page.content)
        sites_available_element = tree.cssselect(self.sites_available_css_path)
        if (len(sites_available_element) > 0):
            text = sites_available_element[0].text
            match = self.sites_available_pattern.match(text)
            site_count_string = match.group(0)
            site_count = int(site_count_string)
            if site_count > 0:
                links = tree.cssselect(self.book_site_link_css_path)
                print 'found', len(links), 'links'
                for link in links:
                    href = link.attrib['href']
                    if 'See Details' in link.text:
                        print href
                        parsed_url = urlparse(href)
                        query_params =parse_qs(parsed_url.query)
                        print query_params
                        if 'siteId' in query_params:
                            # site_id = query_params['siteId'][0]
                            link_with_arv_date = 'http://www.recreation.gov/campsiteDetails.do?' + \
                                 parsed_url.query + \
                                '&arvdate=' + arvdate + \
                                '&lengthOfStay=' + str(self.length_of_stay)
                            print link_with_arv_date
                            # TODO: Attach arvdate (format mm/dd/yyyy) and stay (int) parameters
                            output = 'Found {site_count} available sites for {site_name} {url}'.format(site_count=site_count, site_name=self.site['name'], url =link_with_arv_date)
                            subject = 'We found a campsite for {0}'.format(arvdate)
                            if 'email_address' in self.contact_methods:
                                self.notifications.send_email(self.contact_methods['email_address'],subject , output)
                            # if 'phone_number' in self.contact_methods:
                                # self.notifications.send_text(self.contact_methods['phone_number'], subject, link_with_arv_date)
                            print output
                            break
                    else:
                        print link.text
                        break
        else:
            print 'error checking site'


with open('./sites.yml') as sites_file:
    sites = yaml.load(sites_file)
    campsites = sites['campsites']
    contact_methods = {
        'email_address' : 'self@kwyn.io',
        'phone_number': '408 621 2997'
    }
    user_preferences = {
        'contact_methods' : contact_methods,
        'arrival_dates' : ['08/20/2016', '09/20/2016'],
        'length_of_stay' : 2
    }
    # TODO: write function to trim arrival date < the DateTime.today()
    # Also write something to remove user from queue and e-mail saying sorry no sites found for your desired date
    scrapers = list()
    for site in campsites:
        print 'building scraper for site'
        scrapers.append(SiteScraper(site=campsites[site], user_preferences=user_preferences))
    for scraper in scrapers:
        # TODO: run parallel scrapers
        print 'running scraper', scraper.site['name']
        scraper.run()
