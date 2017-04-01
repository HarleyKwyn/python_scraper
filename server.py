from flask import Flask, Response, render_template, request, redirect, url_for
from logging.handlers import RotatingFileHandler
from logging import Formatter
import config
from src.job import Job
from src.job_crud_service import JobCRUDService
from functools import wraps
from datetime import datetime
app = Flask(__name__)
job_crud_service = JobCRUDService()

# Auth decorater
def check_auth(username, password):
    return username == config.admin_username and password == config.admin_pw

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    locations = job_crud_service.get_locations()
    return render_template("index.html", locations=locations)

@app.route('/jobs', methods=['POST'])
def add_job():
    job = Job(request.form)
    job_crud_service.write_job(job)
    # TODO: redirect ot / job_id
    return redirect("jobs/{0}".format(job.id))

@app.route('/jobs/<string:job_id>')
def get_job(job_id):
    job = job_crud_service.get_job_by_id(job_id)
    job_location = job_crud_service.get_location_id_name_by_id(job.location)
    data = {
        "id": job.id,
        "location": job_location,
        "date": datetime.strftime(datetime.utcfromtimestamp(job.arrival_date), '%m/%d/%Y'),
        "length_of_stay": job.length_of_stay
    }
    return render_template("job.html", locals=data)

@app.route('/admin-list')
@requires_auth
def get_jobs_list():
    return  job_crud_service.get_db_jobs_list()

@app.route('/jobs/<string:job_id>/delete')
# I realize this isn't RESTful but this is a side project
# Also it'll make it so I can send out a link to easily delete jobs
def delete_job(job_id):
    job_crud_service.delete_job_by_id(job_id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    handler = RotatingFileHandler(config.log_dir + 'ui.log', maxBytes=10000, backupCount=1)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(Formatter(log_format))
    handler.setLevel(config.logging_level)
    app.logger.addHandler(handler)
    app.run(host=config.host, port=config.port, debug=config.debug)
