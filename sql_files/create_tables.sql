DROP SEQUENCE users_id_seq;
DROP TABLE users;
CREATE SEQUENCE users_id_seq;
CREATE TABLE users
(
    id INT PRIMARY KEY NOT NULL DEFAULT NEXTVAL('users_id_seq'),
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL
);