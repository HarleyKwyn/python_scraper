import logging
import config
from datetime import datetime
from job import Job
from db_helper import SQLiteHelper

class JobCRUDService(object):
    db_path = None

    def __init__(self, override=None):
        if override is None:
            self.db_path = config.db_path
        else:
            self.db_path = override
        self.db = SQLiteHelper(self.db_path)

    def write_job(self, job):
        job_insert_query = job.get_sql_insert_query()
        data = job.get_sql_insert_query_data()
        logging.debug('job insert query: {0}'.format(job_insert_query))
        self.db.execute(job_insert_query, False, data=data)

    def get_jobs(self):
        rows = self.db.execute("""
            SELECT *
            FROM job
            WHERE datetime(last_notified) <= datetime('now', '-15 minutes')
            """, True)
        return [Job(None, db_row = row) for row in rows];

    def get_site_details_by_location_id(self, location_id):
        site_query = """
            SELECT *
            FROM campsite
            WHERE location_id = (?)
        """
        data = [location_id]
        logging.debug('sites for location query: {0}'.format(site_query))
        rows = self.db.fetchall(site_query, data=data)
        sites = list()
        for row in rows:
            sites.append(self._site_from_db_record(row))
        return sites

    def get_location_id_name_by_id(self, location_id):
        name =self.db.fetch(
            "SELECT location_name FROM location WHERE location_id = (?)",
            data=location_id
        )
        return { "id": location_id, "name": name[0]}

    def _site_from_db_record(self, row):
        return {
            "name": row[1],
            "contract_code": row[3],
            "park_id": row[4],
            "site_types": row[5].split(',')
        }

    '''
    Used for debuging from the browser
    '''
    def get_db_jobs_list(self):
        rows = self.db.fetchall("SELECT * FROM job;")
        row_strings = list()
        if rows == None:
            return "No jobs currently scheduled..."
        for row in rows:
            row_strings.append(' | '.join(map(str, row)))
        return "\n".join(row_strings);

    def get_locations(self):
        rows = self.db.fetchall("SELECT * FROM location")
        locations = list()
        for row in rows:
            locations.append({"id": row[0], "name": row[1]})
        return locations

    def get_job_by_id(self, job_id):
        data = [job_id]
        row = self.db.fetch("SELECT * FROM job where job_id = (?)", data=data)
        if row is None:
            return None
        job = Job(None, db_row = row)
        return job

    def update_job_by_id(self, job_id, job):
        self.db.execute(
            job.get_sql_insert_query(),
            False,
            data=job.get_sql_insert_query_data())
        return job

    def update_job_last_notified(self, job):
        updated_timestamp = datetime.now().isoformat();
        statement = "UPDATE job SET last_notified = '{0}' WHERE job_id = '{1}'"
        formatted_statement = statement.format(updated_timestamp,job.id)
        self.db.execute(
            formatted_statement,
            False
        )

    def delete_job_by_id(self, job_id):
        self.db.execute(
            "DELETE FROM job WHERE job_id = '{0}'".format(job_id),
            False)
