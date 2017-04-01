import copy
import config
import logging
from src.scraper import SiteScraper
from src.db_helper import SQLiteHelper
from src.job_crud_service import JobCRUDService

# def build_scrapers():
#     db.getJobs():
# def remove_invalid_jobs():
#     logging.info('Removing jobs')

def main():
    db = JobCRUDService()
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename=config.log_dir + 'scraper.log', level=config.logging_level)
    logging.info('Deleting old jobs')
    db.delete_old_jobs()
    logging.info('Started')
    jobs = db.get_jobs()
    for job in jobs:
        sites = db.get_site_details_by_location_id(job.location)
        for site in sites:
            logging.info('Building scraper for job id {2}: {0} and dates {1}'.format(site['name'], job.arrival_date, job.length_of_stay, job.id))
            scraper = SiteScraper(site, job, db.update_job_last_notified)
            logging.info('running scraper {0} for date {1} and {2} nights'.format(scraper.site['name'], scraper.arrival_date, scraper.length_of_stay))
            scraper.run()
    logging.info('Finished')



if __name__ == '__main__':
    main()
