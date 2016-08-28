from flask import Flask, render_template, request, redirect, url_for
from logging.handlers import RotatingFileHandler
from logging import Formatter
from db_helper import SQLiteHelper
import config
from job import Job
app = Flask(__name__)
db = SQLiteHelper("scraper.db")

@app.route('/')
def index():
    locations = db.get_locations()
    return render_template("index.html",locations=locations)

@app.route('/add_job', methods=['POST'])
def add_job():
    try:
        job = Job(request.form)
    except Exception as e:
        print e

    db.write_job(job)
    return redirect("/")

@app.route('/<int:job_id>')
def get_job():
    job = db.get_job_by_id(job_id)
    return render_template("job.html", job=job)

if __name__ == '__main__':
    handler = RotatingFileHandler('ui.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    handler.setLevel(config.logging_level)
    app.logger.addHandler(handler)
    app.run()
