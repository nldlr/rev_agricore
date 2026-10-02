-- Fixing Mistakes
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres; -- Or your specific database user

-- DROP TABLE IF EXISTS farms CASCADE;
-- DROP TABLE IF EXISTS operators CASCADE;
-- DROP TABLE IF EXISTS field_jobs CASCADE;
-- DROP TABLE IF EXISTS equipments CASCADE;
-- DROP TABLE IF EXISTS service_reports CASCADE;
-- -- DROP TABLE IF EXISTS users CASCADE;
-- DROP TYPE IF EXISTS equipment_status;
-- DROP TYPE IF EXISTS field_job_priority;
-- DROP TYPE IF EXISTS field_job_status;

CREATE TYPE equipment_status AS ENUM ('Idle', 'In-Use', 'Maintenance', 'Retired');
CREATE TYPE field_job_priority AS ENUM ('Low', 'Medium', 'Critical');
CREATE TYPE field_job_status AS ENUM ('Pending', 'In-Progress', 'Completed', 'Failed');

CREATE TABLE farms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location_region VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    supervisor_id INTEGER NOT NULL
);

CREATE TABLE operators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    farm_id INTEGER NOT NULL REFERENCES farms(id)
);

CREATE TABLE equipments (
    id SERIAL PRIMARY KEY,
    serial_number VARCHAR(50) NOT NULL UNIQUE,
    model VARCHAR(100) NOT NULL,
    status equipment_status NOT NULL DEFAULT 'Idle',
    fuel_level NUMERIC(5,2) NOT NULL CHECK (fuel_level BETWEEN 0 AND 100),
    farm_id INTEGER NOT NULL REFERENCES farms(id)
);

CREATE TABLE field_jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    priority field_job_priority NOT NULL,
    status field_job_status NOT NULL DEFAULT 'Pending',
    equipment_id INTEGER NOT NULL REFERENCES equipments(id),
    operator_id INTEGER NOT NULL REFERENCES operators(id)
);

CREATE TABLE service_reports (
    id SERIAL PRIMARY KEY,
    field_job_id INTEGER NOT NULL REFERENCES field_jobs(id),
    file_url TEXT NOT NULL,
    notes TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);