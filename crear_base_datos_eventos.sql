-- Meta 2.3: Base de datos del Sistema de Eventos Universitarios
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
    CONSTRAINT chk_cupo_positivo CHECK (cupo > 0),
    CONSTRAINT chk_registrados_validos CHECK (registrados >= 0 AND registrados <= cupo)
);

-- Ocho eventos de ejemplo. IGNORE evita duplicar los mismos IDs si se vuelve a ejecutar.
INSERT IGNORE INTO eventos (id, nombre, fecha, hora, lugar, cupo, registrados) VALUES
(1, 'Conferencia de Inteligencia Artificial', '2026-11-05', '10:00:00', 'Auditorio Principal', 120, 85),
(2, 'Taller de Desarrollo Web', '2026-11-08', '12:00:00', 'Laboratorio de Cómputo 2', 30, 18),
(3, 'Curso de Python para Principiantes', '2026-11-12', '09:00:00', 'Aula Magna', 40, 25),
(4, 'Seminario de Emprendimiento', '2026-11-16', '16:00:00', 'Sala de Conferencias', 80, 42),
(5, 'Festival Cultural Universitario', '2026-11-20', '17:30:00', 'Explanada Universitaria', 250, 190),
(6, 'Torneo Deportivo Interfacultades', '2026-11-22', '08:00:00', 'Cancha Deportiva', 100, 60),
(7, 'Presentación de Proyectos Tecnológicos', '2026-11-25', '11:00:00', 'Centro de Innovación', 90, 55),
(8, 'Taller de Ciberseguridad', '2026-11-28', '13:00:00', 'Laboratorio de Redes', 35, 20);
