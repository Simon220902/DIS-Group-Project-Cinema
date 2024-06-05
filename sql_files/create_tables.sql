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
-- AFTER:  {'Poster_Link': (146, 'https://m.media-amazon.com/images/M/MV5BZjA0OWVhOTAtYWQxNi00YzNhLWI4ZjYtNjFjZTEyYjJlNDVlL2ltYWdlL2ltYWdlXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg'),
--          'Series_Title': (68, 'Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb'),
--          'Released_Year': (4, '1994'),
--          'Certificate': (8, 'Approved'),
--          'Runtime': (7, '142 min'),
--          ---'Genre': (29, 'Animation, Adventure, Fantasy'),
--          --'IMDB_Rating': (3, '9.3'),
--          'Overview': (313, "As adults, best friends Julien and Sophie continue the odd game they started as children -- a fearless competition to outdo one another with daring and outrageous stunts. While they often act out to relieve one another's pain, their game might be a way to avoid the fact that they are truly meant for one another."),
--          'Meta_score': (3, '100'),
--          'Director': (32, 'Florian Henckel von Donnersmarck'),
--          'Star1': (25, "Predrag 'Miki' Manojlovic"),
--          'Star2': (25, 'Mélissa Désormeaux-Poulin'),
--          'Star3': (27, 'Boluwatife Treasure Bankole'),
--          'Star4': (27, 'Mary Elizabeth Mastrantonio'),
--          --'No_of_Votes': (7, '2343110'),
--          --'Gross': (11, '134,966,411')
--         }
-- */


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