-- init-db.sql

CREATE TABLE devices (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    region TEXT,
    registration_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE experiments (
    id UUID PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES devices(id),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    test_description TEXT
);

CREATE TABLE gngga (
    id SERIAL PRIMARY KEY,
    full_time TIMESTAMP with TIME ZONE,
    lat DOUBLE PRECISION,
    ns TEXT,
    lon DOUBLE PRECISION,
    ew TEXT,
    quality INTEGER,
    num_sv INTEGER,
    hdop DOUBLE PRECISION,
    alt DOUBLE PRECISION,
    alt_unit TEXT,
    sep DOUBLE PRECISION,
    sep_unit TEXT,
    diff_age INTEGER,
    diff_station TEXT,
    processed_time BIGINT,
    device_id TEXT,
    -- device_id TEXT NOT NULL REFERENCES devices(id),
    -- change to not null later
    experiment_id UUID REFERENCES experiments(id) 
);

-- Adding indexes
CREATE INDEX idx_gngga_device_id ON gngga(device_id);
CREATE INDEX idx_gngga_experiment_id ON gngga(experiment_id);

-- insert initial test device with uuid for device and test-rpi for name
INSERT INTO devices (id, name) VALUES ('test-rpi', 'test-rpi');
