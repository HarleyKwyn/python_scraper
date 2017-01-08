from flask import Flask, render_template, request, redirect, url_for
from logging.handlers import RotatingFileHandler
from logging import Formatter
from src.db_helper import SQLiteHelper
import config
from src.job import Job
from datetime import datetime
app = Flask(__name__)
db = SQLiteHelper(config.db_path)


@app.route('/')
def index():
    locations = db.get_locations()
    return render_template("index.html", locations=locations)

@app.route('/jobs', methods=['POST'])
def add_job():
    job = Job(request.form)
    db.write_job(job)
    # TODO: redirect ot / job_id
    return redirect("jobs/{0}".format(job.id))


@app.route('/jobs/<string:job_id>')
def get_job(job_id):
    job = db.get_job_by_id(job_id)
    print "this is the one you're lookin' for", job.id
    job_location = db.get_location_id_name_by_id(job.location)
    data = {
        "id": job.id,
        "location": job_location,
        "date": datetime.strftime(job.arrival_date, '%m/%d/%Y'),
        "length_of_stay": job.length_of_stay
    }
    return render_template("job.html", locals=data)

@app.route('/admin-list')
def get_jobs_list():
    return  db.get_jobs()

@app.route('/jobs/<string:job_id>/delete')
# I realize this isn't RESTful but this is a side project
# Also it'll make it so I can send out a link to easily delete jobs
def delete_job(job_id):
    db.delete_job_by_id(job_id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    handler = RotatingFileHandler(config.log_dir + 'ui.log', maxBytes=10000, backupCount=1)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(Formatter(log_format))
    handler.setLevel(config.logging_level)
    app.logger.addHandler(handler)
    app.run(host=config.host, port=config.port, debug=config.debug)
