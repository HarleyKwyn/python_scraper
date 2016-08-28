import yaml
import copy
import config
import logging
from scraper import SiteScraper
from db_helper import SQLiteHelper

# def build_scrapers():
#     db.getJobs():
# def remove_invalid_jobs():
#     logging.info('Removing jobs')

def main():
    db = SQLiteHelper(config.db_name)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename='scraper.log', level=config.logging_level)
    logging.info('Started')
    jobs = db.get_jobs()
    for job in jobs:
        sites = db.get_site_details_by_location_id(job.location)
        job.set_sites(sites)
        scrapers = list()
        print sites
        for site in sites:
            logging.info('Building scraper for {0} and dates {1}'.format(site['name'], job['arrival_dates']))
            scraper = SiteScraper(site=site, user_preferences=job)
            logging.info('running scraper {0} for dates {1}'.format(scraper.site['name'], scraper.dates))
            scraper.run()
    logging.info('Finished')

if __name__ == '__main__':
    main()
