import sqlite3 as lite
import sys
import logging
from datetime import datetime
from job import Job

class SQLiteHelper(object):
    con = None

    def __init__(self, db_name):
        self.db_name = db_name

    def execute(self, query, all, data=None):
        try:
            con = lite.connect(self.db_name)
            cursor = con.cursor()
        except lite.Error, e:
            logging.error("Error {0}:".format(e.args[0]))
        try:
            results = None
            cursor_execute = None
            if data is not None:
                cursor_execute = cursor.execute(query, data)
            else:
                cursor_execute = cursor.execute(query)

            if all:
                results = cursor_execute.fetchall()
            else:
                results = cursor_execute.fetchone()
            con.commit()
            return results
            con.close()
        except lite.Error, e:
            logging.error("Error {0}:".format(e.args[0]))
        except Exception, e:
            logging.error("Error running query: {0} ".format(query))
            logging.error(e)
        finally:
            con.close()

    def fetchall(self, query, data=None):
        if data is not None:
            return self.execute(query, True, data=data)
        else:
            return self.execute(query, True)

    def fetch(self, query, data=None):
        if data is not None:
            return self.execute(query, False, data=data)
        else:
            return self.execute(query, False)

    def write_job(self, job):
        job_insert_query = job.get_sql_insert_query()
        data = job.get_sql_insert_query_data()
        logging.debug('job insert query: {0}'.format(job_insert_query))
        self.execute(job_insert_query, False, data=data)

    def get_jobs(self):
        rows = self.execute("""
            SELECT *
            FROM job
            WHERE last_notified <= datetime('now', '-15 minutes')
            """, True)
        jobs = list()
        for row in rows:
            jobs.append(Job.from_db_record(row))
        return jobs

    def get_site_details_by_location_id(self, location_id):
        site_query = """
            SELECT *
            FROM campsite
            WHERE location_id = (?)
        """
        data = [location_id]
        logging.debug('sites for location query: {0}'.format(site_query))
        rows = self.fetchall(site_query, data=data)
        sites = list()
        for row in rows:
            sites.append(self._site_from_db_record(row))
        return sites

    def get_location_id_name_by_id(self, location_id):
        name =self.fetch(
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
    def get_jobs(self):
        rows = self.fetchall("SELECT * FROM job;")
        row_strings = list()
        if rows == None:
            return "No jobs currently scheduled..."
        for row in rows:
            row_strings.append(' | '.join(map(str, row)))
        return "\n".join(row_strings);

    def get_locations(self):
        rows = self.fetchall("SELECT * FROM location")
        locations = list()
        for row in rows:
            locations.append({"id": row[0], "name": row[1]})
        return locations

    def get_job_by_id(self, job_id):
        data = [job_id]
        row = self.fetch("SELECT * FROM job where job_id = (?)", data=data)
        if row is None:
            return None
        job = Job.from_db_record(row)
        return job

    def update_job_by_id(self, job_id, job):
        self.execute(
            job.get_sql_insert_query(),
            False,
            data=job.get_sql_insert_query_data())
        return job

    def update_job_last_notified(self, job):
        self.execute(
            "UPDATE job SET last_notified = (?) job WHERE job_id = (?)",
            False,
            data=[datetime.now(), job.id]
        )

    def delete_job_by_id(self, job_id):
        self.execute(
            "DELETE FROM job WHERE job_id = (?) LIMIT 1",
            False,
            data=[job_id])
