CREATE TABLE IF NOT EXISTS dim_artista (
    id_artista SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    imagen TEXT,
    generos TEXT,
    spotify_id VARCHAR(255)
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

CREATE TABLE IF NOT EXISTS dim_cancion (
    id_cancion SERIAL PRIMARY KEY,
    titulo VARCHAR(255) UNIQUE NOT NULL,
    id_artista INT REFERENCES dim_artista(id_artista)
);

CREATE TABLE IF NOT EXISTS fact_metricas (
    id_metrica SERIAL PRIMARY KEY,
    id_artista INT NOT NULL,
    id_tiempo INT NOT NULL,
    escuchas BIGINT DEFAULT 0,
    reproducciones BIGINT DEFAULT 0,
    vistas BIGINT DEFAULT 0,
    likes BIGINT DEFAULT 0,
    popularidad NUMERIC(5,2) DEFAULT 0,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_metricas_artista FOREIGN KEY (id_artista) REFERENCES dim_artista(id_artista),
    CONSTRAINT fk_metricas_tiempo FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo(id_tiempo),
    CONSTRAINT unique_artista_tiempo UNIQUE (id_artista, id_tiempo)
);

CREATE TABLE IF NOT EXISTS fact_popularidad_region (
    id_popularidad_region SERIAL PRIMARY KEY,
    id_artista INT NOT NULL,
    id_region INT NOT NULL,
    id_tiempo INT NOT NULL,
    vistas BIGINT DEFAULT 0,
    likes BIGINT DEFAULT 0,
    popularidad_region NUMERIC(12,2) DEFAULT 0,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pop_artista FOREIGN KEY (id_artista) REFERENCES dim_artista(id_artista),
    CONSTRAINT fk_pop_region FOREIGN KEY (id_region) REFERENCES dim_region(id_region),
    CONSTRAINT fk_pop_tiempo FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo(id_tiempo),
    CONSTRAINT unique_artista_region UNIQUE (id_artista, id_region, id_tiempo)
);

CREATE TABLE IF NOT EXISTS eventos_streaming (
    id_evento SERIAL PRIMARY KEY,
    tipo_evento VARCHAR(100),
    artista VARCHAR(150),
    fuente VARCHAR(50),
    payload JSONB,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hechos_consumo (
    id_hecho SERIAL PRIMARY KEY,
    id_cancion INT REFERENCES dim_cancion(id_cancion),
    id_artista INT REFERENCES dim_artista(id_artista),
    id_tiempo INT REFERENCES dim_tiempo(id_tiempo),
    id_region INT REFERENCES dim_region(id_region),
    vistas BIGINT DEFAULT 0,
    likes BIGINT DEFAULT 0,
    score_popularidad FLOAT
);

INSERT INTO dim_region (codigo, nombre) VALUES
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