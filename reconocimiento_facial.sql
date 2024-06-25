drop database if exists reconocimiento_facial;

CREATE DATABASE reconocimiento_facial;

USE reconocimiento_facial;

CREATE TABLE usuarios (
    nombre_aplica VARCHAR(100),
    encoding BLOB,
	password VARBINARY(255),
    email_aplica VARCHAR(255),
	numero_aplica VARCHAR(250) PRIMARY KEY
);

CREATE TABLE alumnos(
	nombre VARCHAR(100),
    apellido VARCHAR(100),
    genero VARCHAR(20),
    edad VARCHAR(10),
    nacionalidad VARCHAR(100),
    curp VARCHAR(100),
    APLescuela VARCHAR(100),
    APLturno VARCHAR(100),
    tipoexa VARCHAR(20),
    encoding BLOB
);

SELECT * FROM `usuarios`;
SELECT * FROM `alumnos`;