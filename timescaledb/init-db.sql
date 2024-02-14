-- Create hardware table
CREATE TABLE hardware (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT,
    location_desc TEXT,
    owner_name TEXT,
    make TEXT,
    model TEXT,
    signals TEXT,
    configuration JSONB
);

-- Create experiments table
CREATE TABLE experiments (
    id SERIAL PRIMARY KEY,
    start_time TIMESTAMP NOT NULL UNIQUE,
    end_time TIMESTAMP, -- Renamed from 'end' to 'end_time' to avoid conflict with SQL reserved
    description TEXT,
    configuration JSONB,
    region TEXT,
    type TEXT CHECK(type IN ('Static', 'Dynamic', 'Hybrid')) -- Ensures type is one of the specified values
);

-- Create experiment_devices junction table
CREATE TABLE experiment_devices (
    experiment_id INTEGER NOT NULL,
    device_id INTEGER NOT NULL,
    PRIMARY KEY (experiment_id, device_id),
    FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES hardware(id) ON DELETE CASCADE
);

CREATE TABLE gngga (
    id SERIAL PRIMARY KEY,
    full_time TIMESTAMP WITH TIME ZONE,
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
    device_id INTEGER NOT NULL,
    experiment_id INTEGER NOT NULL,
    FOREIGN KEY (device_id) REFERENCES hardware(id) ON DELETE CASCADE,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
);

-- Indexes for optimizing queries on gngga table
CREATE INDEX idx_gngga_full_time ON gngga (full_time);
CREATE INDEX idx_gngga_device_id ON gngga (device_id);
CREATE INDEX idx_gngga_experiment_id ON gngga (experiment_id);

-- Create nav_pvt table
CREATE TABLE nav_pvt (
    id SERIAL PRIMARY KEY,
    full_time TIMESTAMP WITH TIME ZONE NOT NULL,
    device_id INTEGER NOT NULL,
    experiment_id INTEGER NOT NULL,
    gps_time_tag FLOAT,
    utc_date_time TIMESTAMP,
    utc_time_confirmation TEXT,
    utc_time_accuracy INT,
    fix_type TEXT,
    fix_flags TEXT,
    power_save TEXT,
    lat FLOAT,
    lon FLOAT,
    height FLOAT,
    height_msl FLOAT,
    horizontal_acc FLOAT,
    vertical_acc FLOAT,
    velocity_north FLOAT,
    velocity_east FLOAT,
    velocity_down FLOAT,
    velocity FLOAT,
    heading_acc FLOAT,
    speed_over_ground FLOAT,
    heading_of_motion FLOAT,
    heading_of_vehicle FLOAT,
    magnetic_declination FLOAT,
    declination_acc FLOAT,
    pdop FLOAT,
    num_satellites INT,
    carrier_range_status TEXT,
    age_of_corrections INT,
    time_auth_status TEXT,
    FOREIGN KEY (device_id) REFERENCES hardware(id) ON DELETE CASCADE,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
);

-- Indexes for optimizing queries on nav_pvt table
CREATE INDEX idx_nav_pvt_full_time ON nav_pvt (full_time);
CREATE INDEX idx_nav_pvt_experiment_id ON nav_pvt (experiment_id);
CREATE INDEX idx_nav_pvt_device_id ON nav_pvt (device_id);
