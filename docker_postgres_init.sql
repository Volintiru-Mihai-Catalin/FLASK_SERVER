CREATE TABLE Countries (
    id SERIAL PRIMARY KEY,
    country_name VARCHAR(30) UNIQUE NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);

CREATE TABLE Cities (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES Countries(id) ON DELETE CASCADE,
    city_name VARCHAR(30) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    CONSTRAINT uc_city_name UNIQUE (city_name)
);

CREATE TABLE Temperatures (
    id SERIAL PRIMARY KEY,
    val DOUBLE PRECISION NOT NULL,
    timestmp VARCHAR(30) NOT NULL,
    city_id INTEGER REFERENCES Cities(id) ON DELETE CASCADE,
    CONSTRAINT uc_timestamp UNIQUE (timestmp)
);