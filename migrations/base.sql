CREATE TABLE IF NOT EXISTS job
(
  job_id TEXT PRIMARY KEY, --UUID
  name TEXT,
  email TEXT,
  phone TEXT,
  arrival_date FLOAT,
  departure_date FLOAT,
  location TEXT, -- String representing general camping location of interest
  last_notified FLOAT
  -- notification_frequency INT -- todo, figure out how to select on this as a parameter
);

CREATE TABLE IF NOT EXISTS location
(
  location_id  INT PRIMARY KEY,
  location_name TEXT
);

CREATE TABLE IF NOT EXISTS campsite
(
  campsite_id INT PRIMARY KEY,
  campsite_name TEXT,
  display_name TEXT,
  contract_code TEXT,
  park_id INT,
  site_types TEXT, -- ids seperated by commas
  location_id INT
);

CREATE TABLE IF NOT EXISTS site_type
(
  site_type_id INT PRIMARY KEY,
  site_type_name TEXT
);
