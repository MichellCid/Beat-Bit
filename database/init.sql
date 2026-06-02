CREATE TABLE IF NOT EXISTS dim_artista (
    id_artista SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    imagen TEXT,
    spotify_id VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS dim_genero (
    id_genero SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bridge_artista_genero (
    id_artista INT NOT NULL REFERENCES dim_artista(id_artista) ON DELETE CASCADE,
    id_genero INT NOT NULL REFERENCES dim_genero(id_genero) ON DELETE CASCADE,
    PRIMARY KEY (id_artista, id_genero)
);

CREATE TABLE IF NOT EXISTS dim_cancion (
    id_cancion SERIAL PRIMARY KEY,
    nombre_cancion VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_region (
    id_region SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_tiempo (
    id_tiempo SERIAL PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    anio INT NOT NULL,
    mes INT NOT NULL,
    dia INT NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_rendimiento_streaming (
    id_hecho SERIAL PRIMARY KEY,
    id_artista INT NOT NULL REFERENCES dim_artista(id_artista),
    id_tiempo INT NOT NULL REFERENCES dim_tiempo(id_tiempo),
    id_region INT NOT NULL REFERENCES dim_region(id_region),
    id_cancion INT REFERENCES dim_cancion(id_cancion),
    escuchas BIGINT DEFAULT 0,
    reproducciones BIGINT DEFAULT 0,
    vistas BIGINT DEFAULT 0,
    likes BIGINT DEFAULT 0,
    score_popularidad NUMERIC(12,2) DEFAULT 0,
    tipo_ingesta VARCHAR(50),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_evento_rendimiento UNIQUE (id_artista, id_tiempo, id_region, id_cancion, tipo_ingesta)
);

CREATE TABLE IF NOT EXISTS eventos_streaming (
    id_evento SERIAL PRIMARY KEY,
    tipo_evento VARCHAR(100),
    artista VARCHAR(150),
    fuente VARCHAR(50),
    payload JSONB,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO dim_region (codigo, nombre) VALUES
('GL', 'Global'),
('AG', 'Antigua y Barbuda'),
('AR', 'Argentina'),
('BS', 'Bahamas'),
('BB', 'Barbados'),
('BZ', 'Belice'),
('BO', 'Bolivia'),
('BR', 'Brasil'),
('CA', 'Canadá'),
('CL', 'Chile'),
('CO', 'Colombia'),
('CR', 'Costa Rica'),
('CU', 'Cuba'),
('DM', 'Dominica'),
('EC', 'Ecuador'),
('SV', 'El Salvador'),
('ES', 'España'),
('US', 'Estados Unidos'),
('GD', 'Granada'),
('GT', 'Guatemala'),
('GY', 'Guyana'),
('HT', 'Haití'),
('HN', 'Honduras'),
('JM', 'Jamaica'),
('MX', 'México'),
('NI', 'Nicaragua'),
('PA', 'Panamá'),
('PY', 'Paraguay'),
('PE', 'Perú'),
('DO', 'República Dominicana'),
('KN', 'San Cristóbal y Nieves'),
('VC', 'San Vicente y las Granadinas'),
('LC', 'Santa Lucía'),
('SR', 'Surinam'),
('TT', 'Trinidad y Tobago'),
('UY', 'Uruguay'),
('VE', 'Venezuela')
ON CONFLICT (codigo) DO NOTHING;