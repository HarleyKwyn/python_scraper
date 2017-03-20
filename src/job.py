import uuid
from datetime import datetime, date


class Job(object):
    date_db_format = "%Y-%m-%d %H:%M:%S"
    date_form_format = "%Y-%m-%d"

    def __init__(self, obj, db_row = None):
        if (db_row is None):
            self.id = getattr(obj, "id", uuid.uuid4())
            self.lastname = obj["lastname"]
            self.firstname = obj["firstname"]
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
            self.departure_date = datetime.strptime(
                departure_date_string,
                self.date_form_format)
            self.arrival_date = datetime.strptime(
                arrival_date_string,
                self.date_form_format)
            self.length_of_stay = (self.departure_date - self.arrival_date).days
            self.location = obj["location"]
            self.last_notified = getattr(
                obj,
                "last_notified",
                datetime.fromtimestamp(0).isoformat()
            )
        else:
            self.id = db_row[0]
            self.lastname = db_row[1]
            self.firstname = db_row[2]
            self.email = db_row[3]
            self.phone = db_row[4]
            date_string = db_row[5]
            self.arrival_date = datetime.strptime(date_string, self.date_db_format)
            self.length_of_stay = db_row[6]
            self.location = db_row[7]
            self.last_notified = db_row[8]

    def set_last_notified(self, last_notified):
        self.last_notified = last_notified

    def set_sites(self, sites):
        self.sites = sites

    def trim_past_dates(self):
        valid_dates = list()
        for arv_date in self.arrival_dates:
            today = date.today()
            if arv_date > today:
                valid_dates.append(arv_date)
        return valid_dates

    def get_sql_insert_query(self):
        return "INSERT OR REPLACE INTO job VALUES (?,?,?,?,?,?,?,?,?)"

    def get_sql_insert_query_data(self):
        return (str(self.id),
                self.lastname,
                self.firstname,
                self.email,
                self.phone,
                self.arrival_date,
                self.length_of_stay,
                self.location,
                self.last_notified)
