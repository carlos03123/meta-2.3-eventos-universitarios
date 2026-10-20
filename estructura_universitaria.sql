CREATE DATABASE IF NOT EXISTS eventos_universitarios
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE eventos_universitarios;

CREATE TABLE IF NOT EXISTS eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    lugar VARCHAR(120) NOT NULL,
    cupo INT NOT NULL,
    registrados INT NOT NULL DEFAULT 0,
    CONSTRAINT chk_eventos_cupo CHECK (cupo > 0),
    CONSTRAINT chk_eventos_registrados CHECK (registrados >= 0 AND registrados <= cupo)
);

INSERT INTO eventos (nombre, fecha, hora, lugar, cupo, registrados)
SELECT datos.nombre, datos.fecha, datos.hora, datos.lugar, datos.cupo, datos.registrados
FROM (
    SELECT 'Taller de prototipado digital' AS nombre, '2026-11-05' AS fecha,
           '10:00:00' AS hora, 'Laboratorio de Innovación' AS lugar, 35 AS cupo, 12 AS registrados
    UNION ALL
    SELECT 'Feria de prácticas profesionales', '2026-11-12', '09:30:00',
           'Explanada Central', 120, 47
    UNION ALL
    SELECT 'Encuentro de clubes estudiantiles', '2026-11-18', '13:00:00',
           'Plaza de la Facultad', 80, 26
    UNION ALL
    SELECT 'Charla de ciberseguridad', '2026-11-24', '16:00:00',
           'Auditorio Norte', 90, 63
    UNION ALL
    SELECT 'Muestra de proyectos tecnológicos', '2026-12-02', '11:00:00',
           'Edificio de Vinculación', 100, 54
    UNION ALL
    SELECT 'Jornada de orientación académica', '2026-12-08', '08:30:00',
           'Sala de Usos Múltiples', 70, 18
    UNION ALL
    SELECT 'Concurso de emprendimiento joven', '2026-12-15', '12:00:00',
           'Centro de Negocios', 60, 31
    UNION ALL
    SELECT 'Ciclo de conferencias de tecnología', '2027-01-20', '10:30:00',
           'Auditorio Principal', 150, 82
) AS datos
WHERE NOT EXISTS (
    SELECT 1 FROM eventos e WHERE e.nombre = datos.nombre
);
