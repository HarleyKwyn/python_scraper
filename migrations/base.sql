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

-- populate known sites

INSERT INTO site_type (site_type_id, site_type_name) VALUES
    (2003, "tent"),
    (3100, "tent-only"),
    (9002, "group sites");

INSERT INTO campsite (campsite_id, campsite_name, display_name, contract_code, park_id, site_types, location_id) VALUES
    (1, "upper-pines", "Upper Pines", "NRSO", 70928, "2003,3100,9002", 0),
    (2, "north-pines", "North Pines", "NRSO", 70927, "2003,3100,9002", 0),
    (3, "lower-pines", "Lower Pines", "NRSO", 70925, "2003,3100,9002", 0),
    (4, "toulumne-meadows", "Toulumne Meadows", "NRSO", 70926, "2003,3100,9002", 1);

INSERT INTO location (location_id, location_name) VALUES
    (0, "Yosemite Valley"),
    (1, "Toulumne Meadows");
