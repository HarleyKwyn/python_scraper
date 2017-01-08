DROP TABLE IF EXISTS job;
CREATE TABLE job
(
  job_id TEXT, --UUID
  lastname TEXT,
  firstname TEXT,
  email TEXT,
  phone TEXT,
  arrival_dates INT,
  length_of_stay INT,
  location TEXT, -- String representing general camping location of interest
  last_notified TEXT -- ISO 8601 formatted date string
  -- notification_frequency INT -- todo, figure out how to select on this as a parameter
);

DROP TABLE IF EXISTS location;
CREATE TABLE location
(
  location_id  INT,
  location_name TEXT
);

DROP TABLE IF EXISTS campsite;
CREATE TABLE campsite
(
  campsite_id INT,
  campsite_name TEXT,
  display_name TEXT,
  contract_code TEXT,
  park_id INT,
  site_types TEXT, -- ids seperated by commas
  location_id INT
);

DROP TABLE IF EXISTS site_type;
CREATE TABLE site_type
(
  site_type_id INT,
  site_type_name TEXT
);
