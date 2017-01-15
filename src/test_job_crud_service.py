import os
import sys
import unittest
import tempfile
import config
import uuid
from datetime import datetime, timedelta
from job_crud_service import JobCRUDService
from job import Job
from db_helper import SQLiteHelper

test_job_object = {
    "lastname": "Doe",
    "firstname": "Jane",
    "email": "Jane.Doe@gmail.com",
    "phone": "4086212997",
    "arrival_date": "2020-05-10",
    "departure_date": "2020-05-12",
    "location": 0
}
class jobCRUDServiceTest(unittest.TestCase):

    def setUp(self):
        # Clear db
        self.test_db_path = os.path.dirname(__file__) + '/test.db';
        try:
            os.remove(self.test_db_path)
        except OSError:
            pass

        open(self.test_db_path, 'w').close()
        # Create new db
        self.db = SQLiteHelper(self.test_db_path)
        with open(os.path.dirname(__file__) + '/../migrations/base.sql', 'r') as base_sql_file:
            base_sql=base_sql_file.read()
            statements = base_sql.split(';')
            for statement in statements:
                self.db.execute(statement, False)
        with open(os.path.dirname(__file__) + '/../migrations/populate_sites.sql', 'r') as site_data:
            site_data_sql = site_data.read()
            statements = base_sql.split(';')
            for statement in statements:
                self.db.execute(statement, False)
        self.service = JobCRUDService(override=self.test_db_path)

    def test_correct_db_on_init(self):
        # Test that we're testing the right DB :P
        assert self.service.db_path is not None
        assert self.service.db_path is self.test_db_path
        # Test default db
        defaultCrudService = JobCRUDService()
        assert defaultCrudService.db_path is config.db_path

    def test_empty_db(self):
        jobs = self.service.get_jobs()
        assert len(jobs) is 0

    def test_write_job(self):
        test_uuid = uuid.uuid4()
        job = Job(test_job_object)
        self.service.write_job(job)
        db_jobs = self.service.get_jobs()
        db_job = db_jobs[0]
        assert len(db_jobs) is 1
        assert db_job.id == job.id
        assert db_job.lastname == "Doe"
        assert db_job.firstname == job.firstname
        assert db_job.email == "Jane.Doe@gmail.com"
        assert db_job.phone == "4086212997"
        assert db_job.arrival_date == datetime.strptime("2020-05-10", "%Y-%m-%d")
        assert db_job.length_of_stay is 2
        return job.id

    def test_get_job_by_id(self):
        job = Job(test_job_object)
        self.service.write_job(job)
        retrieved_job = self.service.get_job_by_id(str(job.id))
        print retrieved_job
        assert retrieved_job is not None
        assert retrieved_job.id is job.id

    def test_update_job_last_notified(self):
        job = Job(test_job_object)
        fifteen_minutes_ago = (datetime.now() - timedelta(minutes=15)).isoformat()
        job.set_last_notified(fifteen_minutes_ago)
        print job.last_notified
        self.service.write_job(job)
        retrieved_job = self.service.get_job_by_id(str(job.id))
        assert retrieved_job.last_notified == job.last_notified

        self.service.update_job_last_notified(retrieved_job)
        updated_job = self.service.get_job_by_id(str(job.id))
        assert updated_job.last_notified > job.last_notified

    def tearDown(self):
        os.remove(self.test_db_path)


if __name__ == '__main__':
    unittest.main()
