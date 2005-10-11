--
-- PostgreSQL database dump
--

-- Started on 2005-08-24 03:13:08 Russian Daylight Time

SET client_encoding = 'UNICODE';
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 1574 (class 1262 OID 17665)
-- Name: PyPersistance; Type: DATABASE; Schema: -; Owner: root
--

CREATE DATABASE "PyPersistance" WITH TEMPLATE = template0 ENCODING = 'UNICODE';


ALTER DATABASE "PyPersistance" OWNER TO root;

\connect "PyPersistance"

SET client_encoding = 'UNICODE';
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 1575 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: root
--

COMMENT ON SCHEMA public IS 'Standard public schema';


SET search_path = public, pg_catalog;

--
-- TOC entry 17 (class 1255 OID 17666)
-- Dependencies: 5
-- Name: plpgsql_call_handler(); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION plpgsql_call_handler() RETURNS language_handler
    AS '$libdir/plpgsql', 'plpgsql_call_handler'
    LANGUAGE c;


ALTER FUNCTION public.plpgsql_call_handler() OWNER TO root;

--
-- TOC entry 18 (class 1255 OID 17667)
-- Dependencies: 5
-- Name: plpgsql_validator(oid); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION plpgsql_validator(oid) RETURNS void
    AS '$libdir/plpgsql', 'plpgsql_validator'
    LANGUAGE c;


ALTER FUNCTION public.plpgsql_validator(oid) OWNER TO root;

--
-- TOC entry 282 (class 16402 OID 17668)
-- Dependencies: 17 18
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: public; Owner: 
--

CREATE TRUSTED PROCEDURAL LANGUAGE plpgsql HANDLER plpgsql_call_handler VALIDATOR plpgsql_validator;


--
-- TOC entry 19 (class 1255 OID 17669)
-- Dependencies: 5
-- Name: database_size(name); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION database_size(name) RETURNS bigint
    AS '$libdir/dbsize', 'database_size'
    LANGUAGE c STRICT;


ALTER FUNCTION public.database_size(name) OWNER TO root;

--
-- TOC entry 20 (class 1255 OID 17670)
-- Dependencies: 5
-- Name: pg_database_size(oid); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_database_size(oid) RETURNS bigint
    AS '$libdir/dbsize', 'pg_database_size'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_database_size(oid) OWNER TO root;

--
-- TOC entry 21 (class 1255 OID 17671)
-- Dependencies: 5
-- Name: pg_dir_ls(text, boolean); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_dir_ls(text, boolean) RETURNS SETOF text
    AS '$libdir/admin', 'pg_dir_ls'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_dir_ls(text, boolean) OWNER TO root;

--
-- TOC entry 22 (class 1255 OID 17672)
-- Dependencies: 5
-- Name: pg_file_length(text); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_file_length(text) RETURNS bigint
    AS $_$SELECT len FROM pg_file_stat($1) AS s(len int8, c timestamp, a timestamp, m timestamp, i bool)$_$
    LANGUAGE sql STRICT;


ALTER FUNCTION public.pg_file_length(text) OWNER TO root;

--
-- TOC entry 23 (class 1255 OID 17673)
-- Dependencies: 5
-- Name: pg_file_read(text, bigint, bigint); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_file_read(text, bigint, bigint) RETURNS text
    AS '$libdir/admin', 'pg_file_read'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_file_read(text, bigint, bigint) OWNER TO root;

--
-- TOC entry 24 (class 1255 OID 17674)
-- Dependencies: 5
-- Name: pg_file_rename(text, text, text); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_file_rename(text, text, text) RETURNS boolean
    AS '$libdir/admin', 'pg_file_rename'
    LANGUAGE c;


ALTER FUNCTION public.pg_file_rename(text, text, text) OWNER TO root;

--
-- TOC entry 25 (class 1255 OID 17675)
-- Dependencies: 5
-- Name: pg_file_rename(text, text); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_file_rename(text, text) RETURNS boolean
    AS $_$SELECT pg_file_rename($1, $2, NULL); $_$
    LANGUAGE sql STRICT;


ALTER FUNCTION public.pg_file_rename(text, text) OWNER TO root;

--
-- TOC entry 26 (class 1255 OID 17676)
-- Dependencies: 5
-- Name: pg_file_stat(text); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_file_stat(text) RETURNS record
    AS '$libdir/admin', 'pg_file_stat'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_file_stat(text) OWNER TO root;

--
-- TOC entry 27 (class 1255 OID 17677)
-- Dependencies: 5
-- Name: pg_file_unlink(text); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_file_unlink(text) RETURNS boolean
    AS '$libdir/admin', 'pg_file_unlink'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_file_unlink(text) OWNER TO root;

--
-- TOC entry 28 (class 1255 OID 17678)
-- Dependencies: 5
-- Name: pg_file_write(text, text, boolean); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_file_write(text, text, boolean) RETURNS bigint
    AS '$libdir/admin', 'pg_file_write'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_file_write(text, text, boolean) OWNER TO root;

--
-- TOC entry 29 (class 1255 OID 17679)
-- Dependencies: 5
-- Name: pg_logdir_ls(); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_logdir_ls() RETURNS SETOF record
    AS '$libdir/admin', 'pg_logdir_ls'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_logdir_ls() OWNER TO root;

--
-- TOC entry 30 (class 1255 OID 17680)
-- Dependencies: 5
-- Name: pg_postmaster_starttime(); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_postmaster_starttime() RETURNS timestamp without time zone
    AS '$libdir/admin', 'pg_postmaster_starttime'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_postmaster_starttime() OWNER TO root;

--
-- TOC entry 31 (class 1255 OID 17681)
-- Dependencies: 5
-- Name: pg_relation_size(oid); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_relation_size(oid) RETURNS bigint
    AS '$libdir/dbsize', 'pg_relation_size'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_relation_size(oid) OWNER TO root;

--
-- TOC entry 32 (class 1255 OID 17682)
-- Dependencies: 5
-- Name: pg_reload_conf(); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_reload_conf() RETURNS integer
    AS '$libdir/admin', 'pg_reload_conf'
    LANGUAGE c STABLE STRICT;


ALTER FUNCTION public.pg_reload_conf() OWNER TO root;

--
-- TOC entry 33 (class 1255 OID 17683)
-- Dependencies: 5
-- Name: pg_size_pretty(bigint); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_size_pretty(bigint) RETURNS text
    AS '$libdir/dbsize', 'pg_size_pretty'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_size_pretty(bigint) OWNER TO root;

--
-- TOC entry 34 (class 1255 OID 17684)
-- Dependencies: 5
-- Name: pg_tablespace_size(oid); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION pg_tablespace_size(oid) RETURNS bigint
    AS '$libdir/dbsize', 'pg_tablespace_size'
    LANGUAGE c STRICT;


ALTER FUNCTION public.pg_tablespace_size(oid) OWNER TO root;

--
-- TOC entry 35 (class 1255 OID 17685)
-- Dependencies: 5
-- Name: relation_size(text); Type: FUNCTION; Schema: public; Owner: root
--

CREATE FUNCTION relation_size(text) RETURNS bigint
    AS '$libdir/dbsize', 'relation_size'
    LANGUAGE c STRICT;


ALTER FUNCTION public.relation_size(text) OWNER TO root;

--
-- TOC entry 1195 (class 1259 OID 17686)
-- Dependencies: 1273 5
-- Name: pg_logdir_ls; Type: VIEW; Schema: public; Owner: root
--

CREATE VIEW pg_logdir_ls AS
    SELECT a.filetime, a.filename FROM pg_logdir_ls() a(filetime timestamp without time zone, filename text);


ALTER TABLE public.pg_logdir_ls OWNER TO root;

SET default_tablespace = '';

SET default_with_oids = true;

--
-- TOC entry 1196 (class 1259 OID 17689)
-- Dependencies: 5
-- Name: py_dict; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_dict (
    pyoid integer NOT NULL
);


ALTER TABLE public.py_dict OWNER TO root;

--
-- TOC entry 1197 (class 1259 OID 17691)
-- Dependencies: 5
-- Name: py_dict_item; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_dict_item (
    pyoid integer NOT NULL,
    "key" integer NOT NULL,
    value integer NOT NULL
);


ALTER TABLE public.py_dict_item OWNER TO root;

--
-- TOC entry 1198 (class 1259 OID 17693)
-- Dependencies: 5
-- Name: py_float; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_float (
    pyoid integer NOT NULL,
    value double precision NOT NULL
);


ALTER TABLE public.py_float OWNER TO root;

--
-- TOC entry 1199 (class 1259 OID 17695)
-- Dependencies: 5
-- Name: py_int; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_int (
    pyoid integer NOT NULL,
    value smallint NOT NULL
);


ALTER TABLE public.py_int OWNER TO root;

--
-- TOC entry 1200 (class 1259 OID 17697)
-- Dependencies: 5
-- Name: py_list; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_list (
    pyoid integer NOT NULL
);


ALTER TABLE public.py_list OWNER TO root;

--
-- TOC entry 1201 (class 1259 OID 17699)
-- Dependencies: 5
-- Name: py_list_item; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_list_item (
    pyoid integer NOT NULL,
    "order" bigint NOT NULL,
    value integer NOT NULL
);


ALTER TABLE public.py_list_item OWNER TO root;

--
-- TOC entry 1202 (class 1259 OID 17701)
-- Dependencies: 5
-- Name: py_long; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_long (
    pyoid integer NOT NULL,
    value numeric NOT NULL
);


ALTER TABLE public.py_long OWNER TO root;

--
-- TOC entry 1204 (class 1259 OID 17708)
-- Dependencies: 1526 1527 5
-- Name: py_object; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_object (
    pyoid serial NOT NULL,
    "type" character(64) DEFAULT 'py_object'::bpchar NOT NULL
);


ALTER TABLE public.py_object OWNER TO root;

--
-- TOC entry 1205 (class 1259 OID 17712)
-- Dependencies: 5
-- Name: py_object_attribute; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_object_attribute (
    pyoid integer NOT NULL,
    name character varying(256) NOT NULL,
    value integer NOT NULL
);


ALTER TABLE public.py_object_attribute OWNER TO root;

--
-- TOC entry 1206 (class 1259 OID 17714)
-- Dependencies: 5
-- Name: py_pickled_class; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_pickled_class (
    pyoid integer NOT NULL,
    pickle text
);


ALTER TABLE public.py_pickled_class OWNER TO root;

SET default_with_oids = false;

--
-- TOC entry 1211 (class 1259 OID 19283)
-- Dependencies: 5
-- Name: py_pickled_function; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_pickled_function (
    pyoid integer NOT NULL,
    pickle text NOT NULL
);


ALTER TABLE public.py_pickled_function OWNER TO root;

SET default_with_oids = true;

--
-- TOC entry 1207 (class 1259 OID 17719)
-- Dependencies: 5
-- Name: py_str; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_str (
    pyoid integer NOT NULL,
    value text NOT NULL
);


ALTER TABLE public.py_str OWNER TO root;

--
-- TOC entry 1208 (class 1259 OID 17724)
-- Dependencies: 5
-- Name: py_tuple; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_tuple (
    pyoid integer NOT NULL
);


ALTER TABLE public.py_tuple OWNER TO root;

--
-- TOC entry 1209 (class 1259 OID 17726)
-- Dependencies: 5
-- Name: py_tuple_item; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_tuple_item (
    pyoid integer NOT NULL,
    "order" bigint NOT NULL,
    value integer NOT NULL
);


ALTER TABLE public.py_tuple_item OWNER TO root;

--
-- TOC entry 1210 (class 1259 OID 17728)
-- Dependencies: 5
-- Name: py_unicode; Type: TABLE; Schema: public; Owner: root; Tablespace: 
--

CREATE TABLE py_unicode (
    pyoid integer NOT NULL,
    value text NOT NULL
);


ALTER TABLE public.py_unicode OWNER TO root;

--
-- TOC entry 1529 (class 16386 OID 17734)
-- Dependencies: 1196 1196
-- Name: py_dict_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_dict
    ADD CONSTRAINT py_dict_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_dict_pkey OWNER TO root;

--
-- TOC entry 1531 (class 16386 OID 17736)
-- Dependencies: 1198 1198
-- Name: py_float_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_float
    ADD CONSTRAINT py_float_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_float_pkey OWNER TO root;

--
-- TOC entry 1533 (class 16386 OID 17738)
-- Dependencies: 1199 1199
-- Name: py_int_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_int
    ADD CONSTRAINT py_int_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_int_pkey OWNER TO root;

--
-- TOC entry 1535 (class 16386 OID 17740)
-- Dependencies: 1200 1200
-- Name: py_list_OID_key; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_list
    ADD CONSTRAINT "py_list_OID_key" UNIQUE (pyoid);


ALTER INDEX public."py_list_OID_key" OWNER TO root;

--
-- TOC entry 1537 (class 16386 OID 17742)
-- Dependencies: 1200 1200
-- Name: py_list_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_list
    ADD CONSTRAINT py_list_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_list_pkey OWNER TO root;

--
-- TOC entry 1539 (class 16386 OID 17744)
-- Dependencies: 1202 1202
-- Name: py_long_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_long
    ADD CONSTRAINT py_long_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_long_pkey OWNER TO root;

--
-- TOC entry 1541 (class 16386 OID 17746)
-- Dependencies: 1204 1204
-- Name: py_object_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_object
    ADD CONSTRAINT py_object_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_object_pkey OWNER TO root;

--
-- TOC entry 1543 (class 16386 OID 17748)
-- Dependencies: 1206 1206
-- Name: py_pickled_class_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_pickled_class
    ADD CONSTRAINT py_pickled_class_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_pickled_class_pkey OWNER TO root;

--
-- TOC entry 1553 (class 16386 OID 19289)
-- Dependencies: 1211 1211
-- Name: py_pickled_function_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_pickled_function
    ADD CONSTRAINT py_pickled_function_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_pickled_function_pkey OWNER TO root;

--
-- TOC entry 1545 (class 16386 OID 17750)
-- Dependencies: 1207 1207
-- Name: py_str_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_str
    ADD CONSTRAINT py_str_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_str_pkey OWNER TO root;

--
-- TOC entry 1547 (class 16386 OID 17752)
-- Dependencies: 1208 1208
-- Name: py_tuple_OID_key; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_tuple
    ADD CONSTRAINT "py_tuple_OID_key" UNIQUE (pyoid);


ALTER INDEX public."py_tuple_OID_key" OWNER TO root;

--
-- TOC entry 1549 (class 16386 OID 17754)
-- Dependencies: 1208 1208
-- Name: py_tuple_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_tuple
    ADD CONSTRAINT py_tuple_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_tuple_pkey OWNER TO root;

--
-- TOC entry 1551 (class 16386 OID 17756)
-- Dependencies: 1210 1210
-- Name: py_unicode_pkey; Type: CONSTRAINT; Schema: public; Owner: root; Tablespace: 
--

ALTER TABLE ONLY py_unicode
    ADD CONSTRAINT py_unicode_pkey PRIMARY KEY (pyoid);


ALTER INDEX public.py_unicode_pkey OWNER TO root;

--
-- TOC entry 1554 (class 16386 OID 17757)
-- Dependencies: 1196 1540 1204
-- Name: py_dict_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_dict
    ADD CONSTRAINT "py_dict_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1555 (class 16386 OID 17765)
-- Dependencies: 1540 1204 1197
-- Name: py_dict_item_key_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_dict_item
    ADD CONSTRAINT py_dict_item_key_fkey FOREIGN KEY ("key") REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1557 (class 16386 OID 18402)
-- Dependencies: 1196 1528 1197
-- Name: py_dict_item_pyoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_dict_item
    ADD CONSTRAINT py_dict_item_pyoid_fkey FOREIGN KEY (pyoid) REFERENCES py_dict(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1556 (class 16386 OID 17769)
-- Dependencies: 1204 1197 1540
-- Name: py_dict_item_value_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_dict_item
    ADD CONSTRAINT py_dict_item_value_fkey FOREIGN KEY (value) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1558 (class 16386 OID 17773)
-- Dependencies: 1204 1540 1198
-- Name: py_float_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_float
    ADD CONSTRAINT "py_float_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1559 (class 16386 OID 17777)
-- Dependencies: 1199 1204 1540
-- Name: py_int_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_int
    ADD CONSTRAINT "py_int_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1560 (class 16386 OID 17781)
-- Dependencies: 1204 1540 1200
-- Name: py_list_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_list
    ADD CONSTRAINT "py_list_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1561 (class 16386 OID 17785)
-- Dependencies: 1201 1200 1534
-- Name: py_list_item_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_list_item
    ADD CONSTRAINT "py_list_item_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_list(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1562 (class 16386 OID 17789)
-- Dependencies: 1204 1540 1201
-- Name: py_list_item_value_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_list_item
    ADD CONSTRAINT py_list_item_value_fkey FOREIGN KEY (value) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1563 (class 16386 OID 17793)
-- Dependencies: 1204 1202 1540
-- Name: py_long_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_long
    ADD CONSTRAINT "py_long_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1564 (class 16386 OID 17797)
-- Dependencies: 1540 1204 1205
-- Name: py_object_attributes_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_object_attribute
    ADD CONSTRAINT "py_object_attributes_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1565 (class 16386 OID 17801)
-- Dependencies: 1204 1540 1205
-- Name: py_object_attributes_value_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_object_attribute
    ADD CONSTRAINT py_object_attributes_value_fkey FOREIGN KEY (value) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1566 (class 16386 OID 17805)
-- Dependencies: 1206 1204 1540
-- Name: py_pickled_class_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_pickled_class
    ADD CONSTRAINT "py_pickled_class_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1572 (class 16386 OID 19290)
-- Dependencies: 1211 1204 1540
-- Name: py_pickled_function_pyoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_pickled_function
    ADD CONSTRAINT py_pickled_function_pyoid_fkey FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1567 (class 16386 OID 17809)
-- Dependencies: 1204 1540 1207
-- Name: py_str_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_str
    ADD CONSTRAINT "py_str_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1568 (class 16386 OID 17813)
-- Dependencies: 1208 1204 1540
-- Name: py_tuple_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_tuple
    ADD CONSTRAINT "py_tuple_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1569 (class 16386 OID 17817)
-- Dependencies: 1208 1546 1209
-- Name: py_tuple_item_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_tuple_item
    ADD CONSTRAINT "py_tuple_item_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_tuple(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1570 (class 16386 OID 17821)
-- Dependencies: 1540 1204 1209
-- Name: py_tuple_item_value_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_tuple_item
    ADD CONSTRAINT py_tuple_item_value_fkey FOREIGN KEY (value) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1571 (class 16386 OID 17825)
-- Dependencies: 1210 1204 1540
-- Name: py_unicode_OID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY py_unicode
    ADD CONSTRAINT "py_unicode_OID_fkey" FOREIGN KEY (pyoid) REFERENCES py_object(pyoid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 1576 (class 0 OID 0)
-- Dependencies: 5
-- Name: public; Type: ACL; Schema: -; Owner: root
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM root;
GRANT ALL ON SCHEMA public TO root;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2005-08-24 03:13:10 Russian Daylight Time

--
-- PostgreSQL database dump complete
--

