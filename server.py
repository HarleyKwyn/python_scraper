from flask import Flask, render_template, request, redirect
from logging.handlers import RotatingFileHandler
from logging import Formatter
from src.db_helper import SQLiteHelper
import config
from src.job import Job
app = Flask(__name__)
db = SQLiteHelper(config.db_path)


@app.route('/')
def index():
    locations = db.get_locations()
    return render_template("index.html", locations=locations)


@app.route('/add_job', methods=['POST'])
def add_job():
    print request.form
    print Job
    job = Job(request.form)
    print job
    db.write_job(job)
    # TODO: redirect ot / job_id
    return redirect("/{0}".format(job.id))


@app.route('/<string:job_id>')
def get_job(job_id):
    job = db.get_job_by_id(job_id)
    return render_template("job.html", job=job)


@app.route('/<string:job_id>/delete')
# I realize this isn't RESTful but this is a side project
# Also it'll make it so I can send out a link to easily delete jobs
def delete_job(job_id):
    db.delete_job_by_id(job_id)
    return redirect("/")

if __name__ == '__main__':
    handler = RotatingFileHandler(config.log_dir + 'ui.log', maxBytes=10000, backupCount=1)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(Formatter(log_format))
    handler.setLevel(config.logging_level)
    app.logger.addHandler(handler)
    app.run(host=config.host, port=config.port, debug=config.debug)
