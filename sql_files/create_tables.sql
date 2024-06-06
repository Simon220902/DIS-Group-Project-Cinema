DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS movies CASCADE;
DROP TABLE IF EXISTS stars CASCADE;
DROP TABLE IF EXISTS stars_in CASCADE;
DROP TABLE IF EXISTS directors CASCADE;
DROP TABLE IF EXISTS theaters CASCADE;
DROP TABLE IF EXISTS seats CASCADE;
DROP TABLE IF EXISTS showings CASCADE;
DROP TABLE IF EXISTS reservations CASCADE;
DROP TABLE IF EXISTS seat_reservations CASCADE;


CREATE TABLE users
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL
);

CREATE TABLE directors
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(35) NOT NULL
);

CREATE TABLE movies
(
    id SERIAL PRIMARY KEY,
    title VARCHAR(70) NOT NULL,
    poster_link VARCHAR(150) NOT NULL,
    certificate VARCHAR(10) NOT NULL,
    meta_score INT NOT NULL,
    runtime INT NOT NULL,
    overview VARCHAR(350) NOT NULL,
    director_id INT,
    FOREIGN KEY (director_id) REFERENCES directors (id)
);

CREATE TABLE stars
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(35) NOT NULL
);

CREATE TABLE stars_in
(
    star_id INT NOT NULL,
    movie_id INT NOT NULL,
    PRIMARY KEY (star_id, movie_id),
    FOREIGN KEY (star_id) REFERENCES stars (id),
    FOREIGN KEY (movie_id) REFERENCES movies (id)
);


CREATE TABLE theaters
(
    id SERIAL PRIMARY KEY,
    num INT NOT NULL UNIQUE
);

CREATE TABLE seats
(
    id SERIAL PRIMARY KEY,
    theater_id INT NOT NULL,
    row INT NOT NULL,
    num INT NOT NULL,
    FOREIGN KEY (theater_id) REFERENCES theaters (id),
    UNIQUE (theater_id, row, num)
);

CREATE TABLE showings
(
    id SERIAL PRIMARY KEY,
    showing_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    movie_id INT NOT NULL,
    theater_id INT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies (id),
    FOREIGN KEY (theater_id) REFERENCES theaters (id)
);

CREATE TABLE reservations
(
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    showing_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (showing_id) REFERENCES showings (id)
);

CREATE TABLE seat_reservations
(
    seat_id INT NOT NULL,
    reservation_id INT NOT NULL,
    PRIMARY KEY (seat_id, reservation_id),
    FOREIGN KEY (seat_id) REFERENCES seats (id),
    FOREIGN KEY (reservation_id) REFERENCES reservations (id)
);

-- /*
--     Tables to be made: [In general in our ER-diagram we do not have IDs though that is a good idea.]
--     - Users(id, name, email, password) [Username not in our ER-diagram]
--     - Movies(id, title, poster_link, certificate, meta_score, runtime, overview, director_id)
--     - Stars(id, name)
--         - StarsIn(star_id, movie_id)
--     - Directors(id, name)
--     - Showings(id, date, start, end, movie_id, theater_id)
--     - Theaters(id, name)
--     - Seats(id, theater_id, row, num)
--     - Reservations(id, user_id, showing_id)
--         - SeatReservations(seat_id, reservation_id)
-- */