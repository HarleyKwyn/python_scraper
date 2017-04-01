import uuid
from datetime import datetime, date
epoch_start = datetime(1970,1,1)

class Job(object):
    date_db_format = "%Y-%m-%d %H:%M:%S"
    date_form_format = "%Y-%m-%d"

    def __init__(self, obj, db_row = None):
        if (db_row is None):
            self.id = getattr(obj, "id", str(uuid.uuid4()))
            self.name = obj["name"]
            self.email = obj.get("email", None)
            self.phone = obj.get("phone", None)
            try:
                arrival_date_string = obj["arrival_date"]
            except Exception as e:
                raise Exception("Please enter an arrival date")
            try:
                departure_date_string = obj["departure_date"]
            except Exception as e:
                raise Exception("Please enter a departure date")
            arrival_datetime = datetime.strptime(
                arrival_date_string,
                self.date_form_format)
            departure_datetime = datetime.strptime(
                departure_date_string,
                self.date_form_format)
            self.arrival_date = (arrival_datetime - epoch_start).total_seconds()
            self.departure_date = (departure_datetime - epoch_start).total_seconds()
            self.length_of_stay = (departure_datetime - arrival_datetime).days
            self.location = obj["location"]
            # Set timestamp to beginning of epoch time
            self.last_notified = getattr(
                obj,
                "last_notified",
                0
            )
        else:
            self.id = db_row[0]
            self.name = db_row[1]
            self.email = db_row[2]
            self.phone = db_row[3]
            self.arrival_date = db_row[4]
            self.departure_date = db_row[5]
            departure_datetime = datetime.utcfromtimestamp(self.departure_date)
            arrival_datetime = datetime.utcfromtimestamp(self.arrival_date)
            length_of_stay = (departure_datetime - arrival_datetime).days
            self.length_of_stay = length_of_stay
            self.location = db_row[6]
            self.last_notified = db_row[7]

    def set_last_notified(self, last_notified):
        self.last_notified = last_notified

    def set_sites(self, sites):
        self.sites = sites

    def get_sql_insert_query(self):
        return "INSERT OR REPLACE INTO job VALUES (?,?,?,?,?,?,?,?)"

    def get_sql_insert_query_data(self):
        return (str(self.id),
                self.name,
                self.email,
                self.phone,
                self.arrival_date,
                self.departure_date,
                self.location,
                self.last_notified)
