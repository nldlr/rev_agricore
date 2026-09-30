INSERT INTO farms (id, name, location_region, capacity, supervisor_id) VALUES
    (1, 'Iowa Corn Fields', 'US-Midwest', 40, 101),
    (2, 'Florida Orange County', 'US-South', 25, 102);

INSERT INTO operators (id, name, farm_id) VALUES
    (201, 'C. Restrepo', 1),
    (202, 'C. Feng', 1);

INSERT INTO equipments (id, serial_number, model, status, fuel_level, farm_id) VALUES
    (1, 'MG-1001', 'Miracle-V2', 'In-Use', 18.5, 1),
    (2, 'MG-1002', 'Miracle-V2', 'Idle', 76.0, 1),
    (3, 'IR-2050', 'Irrigator-V3', 'In-Use', 9.0, 2),
    (4, 'MG-1003', 'Miracle-V2', 'Maintenance', 42.0, 1);

INSERT INTO field_jobs (id, title, priority, status, equipment_id, operator_id) VALUES
    (1, 'Order 01', 'Critical', 'Pending', 1, 201),
    (2, 'Order 02', 'Low', 'Pending', 3, 202),
    (3, 'Order 03', 'Medium', 'Completed', 2, 201),
    (4, 'Order 04', 'Low', 'Failed', 4, 201);

INSERT INTO service_reports (field_job_id, file_url, notes) VALUES
    (1, 's3://rev_argicore-diagnostics/mm-1001.pdf', 'OLED Display Model');


SELECT setval('farms_id_seq', (SELECT MAX(id) FROM farms));
SELECT setval('operators_id_seq', (SELECT MAX(id) FROM operators));
SELECT setval('equipments_id_seq', (SELECT MAX(id) FROM equipments));
SELECT setval('field_jobs_id_seq', (SELECT MAX(id) FROM field_jobs));