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
