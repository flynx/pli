SET client_encoding = 'UNICODE';
-- CREATE DATABASE "poker" WITH TEMPLATE = template0 ENCODING = 'UNICODE';

-- TODO add transaction id's to all objects (and make an object's primery key a combination of the two oid and tid...)




BEGIN;

-- this will provide a way to access objects in the database using simple string names.
CREATE TABLE py_registry (
    name VARCHAR(512) PRIMARY KEY,
    pyoid BIGINT REFERENCES py_object(pyoid)
);
CREATE UNIQUE INDEX py_registry_name_idx ON py_registry (name);

CREATE TABLE py_object (
    pyoid SERIAL PRIMARY KEY,
    type VARCHAR(64) DEFAULT 'py_object' NOT NULL
);

CREATE TABLE py_dict (
    pyoid BIGINT PRIMARY KEY REFERENCES py_object(pyoid)
);

CREATE TABLE py_dict_item (
    pyoid BIGINT REFERENCES py_object(pyoid) NOT NULL,
    key BIGINT REFERENCES py_object(pyoid) NOT NULL,
    value BIGINT REFERENCES py_object(pyoid) NOT NULL
);

CREATE TABLE py_float (
    pyoid BIGINT REFERENCES py_object(pyoid) PRIMARY KEY,
    value DOUBLE PRECISION NOT NULL
);

CREATE TABLE py_int (
    pyoid BIGINT REFERENCES py_object(pyoid) PRIMARY KEY,
    value INTEGER NOT NULL
);

CREATE TABLE py_list (
    pyoid BIGINT REFERENCES py_object(pyoid) PRIMARY KEY
);

CREATE TABLE py_list_item (
    pyoid BIGINT REFERENCES py_object(pyoid) NOT NULL,
    "order" BIGINT NOT NULL,
    value BIGINT REFERENCES py_object(pyoid) NOT NULL
);

CREATE TABLE py_long (
    pyoid BIGINT REFERENCES py_object(pyoid) PRIMARY KEY,
    value NUMERIC NOT NULL
);

CREATE TABLE py_object_attribute (
    pyoid BIGINT REFERENCES py_object(pyoid) NOT NULL,
    name VARCHAR(256) NOT NULL,
    value BIGINT REFERENCES py_object(pyoid) NOT NULL
);

CREATE TABLE py_pickled_class (
    pyoid BIGINT REFERENCES py_object(pyoid) PRIMARY KEY,
    pickle TEXT
);

CREATE TABLE py_pickled_function (
    pyoid BIGINT REFERENCES py_object(pyoid) PRIMARY KEY,
    pickle TEXT NOT NULL
);

CREATE TABLE py_str (
    pyoid BIGINT REFERENCES py_object(pyoid) PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE py_tuple (
    pyoid BIGINT REFERENCES py_object(pyoid) PRIMARY KEY
);

CREATE TABLE py_tuple_item (
    pyoid BIGINT REFERENCES py_object(pyoid) NOT NULL,
    "order" BIGINT NOT NULL,
    value BIGINT REFERENCES py_object(pyoid) NOT NULL
);

CREATE TABLE py_unicode (
    pyoid BIGINT REFERENCES py_object(pyoid) PRIMARY KEY,
    value TEXT NOT NULL
);

END;
