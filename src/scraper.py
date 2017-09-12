import urllib
import requests
import re
import copy
import logging
import config
from lxml import html
from urlparse import urlparse, parse_qs
from string import Template
from datetime import datetime, timedelta
from notifications import Notifications

epoch_start = datetime(1970,1,1);
message_template = """
Hi {name}, \n\n
We found you a campsite for {site_name} on {arvdate} for {nights} nights.
Quick, go get it before someone else does! \n\n
{url}

If you no longer need this job just follow this link:
https://camper.kwyn.io/jobs/{id}/delete
"""
class SiteScraper(object):
    urlTemplate = Template('https://www.recreation.gov/camping/${name}/r/campsiteDetails.do?contractCode=${contract_code}&parkId=${park_id}')
    sites_available_pattern = re.compile('^(\d+)')
    sites_available_css_path = 'div.matchSummary'
    book_site_link_css_path = 'a.book.now'
    date_string_format = '%m/%d/%Y'
    data = {
        'siteTypeFilter': 'ALL',
        'submitSiteForm': 'true',
        'search': 'site',
        'currentMaximumWindow': 12
    }
    headers = {
        'Origin': 'https://www.recreation.gov',
        'Referer': 'https://www.recreation.gov/campsiteSearch.do',
        # 'Host': 'www.recreation.gov',
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

    def __init__(self, site, job, update_job_last_notified, notifications):
        self.job = job
        self.update_job_last_notified = update_job_last_notified
        self.contact_methods = dict()
        if hasattr(job, "email"):
            self.contact_methods["email_address"] = job.email
        if hasattr(job, "phone"):
            self.contact_methods["phone_number"] = job.phone
        self.arrival_date = datetime.utcfromtimestamp(job.arrival_date)
        self.departure_date = datetime.utcfromtimestamp(job.departure_date)
        self.length_of_stay = (self.departure_date - self.arrival_date).days
        self.site = site
        self.name = job.name
        self.url = self.urlTemplate.substitute(site)
        self.init_cookies()
        self.data['parkId'] = site['park_id']
        self.data['contractCode'] = site['contract_code']
        self.notifications = notifications

    def run(self):
        data = self.build_form_data_for_site()
        for formdata in data:
            self.check_site(formdata, 0)
        self.notifications.close_smtp_connection()

    def build_form_data_for_site(self):
        date_string_format = self.date_string_format = '%m/%d/%Y'
        form_post_format = self.date_string_format = '%a %b %d %Y'
        all_data = list()
        # for each site type
        for site_type in self.site['site_types']:
            form_data = copy.deepcopy(self.data)
            if site_type != 'ALL':
                form_data['lookingFor'] = site_type
            form_data['submitSiteForm'] = 'true'
            form_data['arrivalDate'] = self.arrival_date.strftime(form_post_format)
            form_data['departureDate'] = datetime.strftime(self.departure_date, form_post_format)
            # if it has loops
            if 'loops' in self.site:
                for loop in self.site['loops']:
                    form_data['loop'] = loop
                    all_data.append(copy.deepcopy(form_data))
            # else add the current form_data
            else:
                all_data.append(copy.deepcopy(form_data))
        return all_data

    def init_cookies(self):
        self.session = requests.Session()
        self.session.get('http://www.recreation.gov')
        self.session.get(self.url)
        # TODO: Health check here?

    def check_site(self, formdata, try_count):
        arvdate = formdata['arrivalDate']
        logging.info(
            'Checking date {0} for {1} nights'.format(
                arvdate,
                self.length_of_stay
            )
        )
        # Arrival date
        s = self.session
        page = s.post(
            'https://www.recreation.gov/campsiteSearch.do',
            headers=self.headers,
            data=formdata
        )
        tree = html.fromstring(page.content)
        sites_available_element = tree.cssselect(self.sites_available_css_path)
        if (len(sites_available_element) > 0):
            text = sites_available_element[0].text
            match = self.sites_available_pattern.match(text)
            site_count_string = match.group(0)
            site_count = int(site_count_string)
            if site_count > 0:
                links = tree.cssselect(self.book_site_link_css_path)
                logging.info('Found {0} links'.format(len(links)))
                for link in links:
                    if 'Enter Date' in link.text:
                        logging.error('Failed on try {0}'.format(try_count))
                        logging.error('Site did not load correctly. form data {0}'.format(formdata))
                        self.check_site(formdata, try_count)
                        break
                    if 'See Details' in link.text:
                        href = link.attrib['href']
                        parsed_url = urlparse(href)
                        query_params = parse_qs(parsed_url.query)
                        if 'siteId' in query_params:
                            link_with_arv_date = 'http://www.recreation.gov/campsiteDetails.do?' + \
                                parsed_url.query + \
                                '&arvdate=' + urllib.quote(arvdate) + \
                                '&lengthOfStay=' + str(self.length_of_stay)
                            output = message_template.format(
                                id=self.job.id,
                                name=self.name,
                                site_name=self.site['name'],
                                arvdate=arvdate,
                                nights=self.length_of_stay,
                                url=link_with_arv_date
                            )
                            subject = u"\u26FA We found you a campsite for {0}!".format(arvdate)
                            print self.contact_methods
                            if 'email_address' in self.contact_methods:
                                self.notifications.send_email(
                                    self.contact_methods['email_address'],
                                    subject,
                                    output
                                    )
                            if 'phone_number' in self.contact_methods:
                                self.notifications.send_text(self.contact_methods['phone_number'], subject, link_with_arv_date)
                            # Debugging to see when people get notified.
                            # Also, if they get spammed I get spammed @_@
                            self.notifications.send_email(
                                config.admin_email,
                                subject,
                                output
                            )
                            self.update_job_last_notified(self.job)
                            break
        else:
            if page.status_code is 403:
                logging.error('IP Address {0} has been blocked'.format(self.proxies['http']))
            logging.error('No site available element found')
