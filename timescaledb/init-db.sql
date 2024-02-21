-- Create hardware table
CREATE TABLE hardware (
    id SERIAL PRIMARY KEY,
    alias TEXT UNIQUE NOT NULL,
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
    start_time TIMESTAMP WITH TIME ZONE NOT NULL UNIQUE,
    end_time TIMESTAMP WITH TIME ZONE,
    alias TEXT UNIQUE NOT NULL,
    description TEXT,
    configuration JSONB,
    region TEXT,
    type TEXT CHECK(type IN ('static', 'dynamic', 'hybrid', 'unknown')) -- Ensures type is one of the specified values
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

CREATE TABLE nav_pvt (
    id SERIAL PRIMARY KEY,
    full_time TIMESTAMP WITH TIME ZONE NOT NULL,
    device_id INTEGER NOT NULL,
    experiment_id INTEGER NOT NULL,
    year INT,
    month INT,
    day INT,
    hour INT,
    min INT,
    second INT,
    validDate INT,
    validTime INT,
    tAcc BIGINT,
    fixType TEXT,
    gnssFixOk BOOLEAN,
    numSV INT,
    lon DOUBLE PRECISION,
    lat DOUBLE PRECISION,
    height FLOAT,
    hMSL FLOAT,
    hAcc FLOAT,
    vAcc FLOAT,
    velN FLOAT,
    velE FLOAT,
    velD FLOAT,
    gSpeed FLOAT,
    headMot FLOAT,
    sAcc FLOAT,
    headAcc FLOAT,
    pDOP FLOAT,
    FOREIGN KEY (device_id) REFERENCES hardware(id) ON DELETE CASCADE,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
);

-- Indexes for optimizing queries on nav_pvt table
CREATE INDEX idx_nav_pvt_full_time ON nav_pvt (full_time);
CREATE INDEX idx_nav_pvt_experiment_id ON nav_pvt (experiment_id);
CREATE INDEX idx_nav_pvt_device_id ON nav_pvt (device_id);

INSERT INTO experiments (start_time, end_time, alias, description, region, type)
VALUES ('2024-01-01T00:00:00+00', NULL, 'sandbox', 'generic sandbox experiment', 'global', 'unknown')
RETURNING id;
