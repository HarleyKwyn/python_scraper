from uuid import UUID
from datetime import datetime
from datetime import date
class Job(object):
    @classmethod
    def __init__(self, obj):
        self.id = getattr(obj, "id", UUID.uuid4())
        self.lastname = obj["lastname"]
        self.firstname = obj["firstname"]
        self.email = obj["email"]
        self.phone = obj["phone"]
        arrivale_dates =  obj["arrival_dates"]
        if isinstance(arrival_dates, list):
            self.arrival_dates = arrival_dates
        else:
            date_strings = arrivale_dates.split(',')
            self.arrival_dates = self.date_strings_to_dates(date_strings)
        self.length_of_stay = obj["length_of_stay"]
        self.location = obj["location"]
        self.last_notified = getattr(obj, "last_notified", datetime.fromtimestamp(0).isoformat())

    @classmethod
    def from_db_record(self, object):
        self.id = db_row[0]
        self.lastname = db_row[1]
        self.firstname = db_row[2]
        self.email = db_row[3]
        self.phone = db_row[4]
        date_strings = db_row[5].split(',')
        self.arrival_dates = self.date_strings_to_dates(date_strings)
        self.length_of_stay = db_row[6]
        self.location = db_row[7]
        self.last_notified = db_row[8]

    def set_sites(self, sites):
        self.sites = sites

    def trim_past_dates(self):
        valid_dates = list()
        for date in self.arrival_dates:
            today = date.today()
            if date > today:
                valid_dates.append(date)
        return valid_dates

    def date_strings_to_dates(self, date_strings):
        dates = list()
        for string in date_strings:
            d = self.date_string_to_date(string)
            dates.append(d)
        return dates

    def date_string_to_date(self, date_string):
        try:
            return date.strptime("%m/%d/%Y", date_string)
        except Exception as e:
            raise "Could not parse date {0} must be in MM/DD/YYYY format"

    def get_sql_insert_query(self):
        return """
        INSERT OR REPLACE INTO job VALUES (
            {0.id},
            {0.lastname},
            {0.firstname},
            {0.email},
            {0.phone},
            {0.arrival_dates},
            {0.length_of_stay},
            {0.location},
            {0.last_notified}
        )
        """.format(self)
