DROP TABLE IF EXISTS aed_installation_locations;
CREATE TABLE aed_installation_locations(
  id SERIAL NOT NULL,
  area VARCHAR(32) NOT NULL,
  location_id integer NOT NULL PRIMARY KEY,
  location_name TEXT NOT NULL,
  postal_code CHAR(8),
  address TEXT NOT NULL,
  phone_number TEXT,
  available_time TEXT,
  installation_floor TEXT,
  latitude decimal NOT NULL,
  longitude decimal NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX ON aed_installation_locations (area);
