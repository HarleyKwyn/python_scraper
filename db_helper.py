import sqlite3 as lite
import sys
import config
import logging
from datetime import datetime
from job import Job

class SQLiteHelper(object):
    con = None

    def __init__(self, db_name):
        try:
            self.con = lite.connect(db_name)
        except lite.Error, e:
            logging.error("Error {0}:".format(e.args[0]))
            sys.exit(1)

    def get_connection(self):
        return self.con

    def get_cursor(self):
        return self.con.cursor()

    def close_connection(self):
        self.con.close()

    def execute(self, cursor, query, data):
        try:
            if data != None:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
                self.conn.commit()
        except lite.Error, e:
            logging.error("Error {0}:".format(e.args[0]))
        except e:
            logging.error("Error running query: {0} ".format(query))
            logging.error(e)

    def write_job(self, job):
        cursor = self.get_cursor()
        job_insert_query = job.get_sql_insert_query
        logging.debug('job insert query: {0}'.format(job_insert_query))
        self.execute(cursor, job_insert_query)

    def get_jobs(self):
        cursor = self.get_cursor()
        rows = cursor.execute("SELECT * FROM job;").fetchall()
        "SELECT * FROM job WHERE last_notified <= datetime('now', '-15 minutes')"
        jobs = list()
        for row in rows:
            jobs.append(Job.from_db_record(row))
        return jobs

    def get_site_details_by_location_id(self, location_id):
        cursor = self.get_cursor()
        site_query = "SELECT * FROM campsite WHERE location_id = {0}".format(location_id);
        logging.debug('sites for location query: {0}'.format(site_query))
        rows = cursor.execute(site_query).fetchall()
        sites = list()
        for row in rows:
            sites.append(self._site_from_db_record(row))
        return sites

    def _site_from_db_record(self, row):
        return {
            "name": row[1],
            "contract_code": row[2],
            "park_id": row[3],
            "site_types": row[4].split(',')
        }

    def get_locations(self):
        cursor = self.get_cursor()
        rows = cursor.execute("SELECT * FROM location").fetchall()
        locations = list()
        for row in rows:
            locations.append({"id":row[0], "name":row[1]})
        return locations

    def get_job_by_id(self, job_id):
        cursor = self.get_cursor()
        row = cursor.execute("SELECT * from job where job_id = {0}".format(job_id)).fetch()
        return Job.from_db_record(row)

    def update_job_by_id(self, job_id, job):
        cursor = self.get_cursor()
        cursor.execute(job.get_sql_insert_query)
        return job

    # def deleteJob(self, jobId):
