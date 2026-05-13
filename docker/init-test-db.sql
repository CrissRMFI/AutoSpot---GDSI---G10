-- ═══════════════════════════════════════════════════════════════════════════
-- Script de inicialización: crea la base de datos de testing.
--
-- PostgreSQL ejecuta automáticamente los .sql en /docker-entrypoint-initdb.d/
-- la PRIMERA vez que se inicializa el volumen de datos.
--
-- Si el volumen ya existe, este script NO se re-ejecuta.
-- Para forzar re-ejecución: docker compose down -v && docker compose up db -d
-- ═══════════════════════════════════════════════════════════════════════════

-- Crear la base de datos de tests (si no existe).
-- Se usa SELECT para evitar error si ya fue creada.
SELECT 'CREATE DATABASE autospot_test_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'autospot_test_db')\gexec
