from typing import Optional
import psycopg
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, name, email, id=None, password_hash=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.name)

class Movie():
    def __init__(self, id, title, poster_link, certificate, meta_score, runtime, overview, director_id, director_name=None):
        self.id = id
        self.title = title
        self.poster_link = poster_link
        self.certificate = certificate
        self.meta_score = meta_score
        self.runtime = runtime
        self.overview = overview
        self.director_id = director_id
        self.director_name = director_name
    
    def getMovieByIdWithDirectorName(movie_id):
        sql = f"SELECT movies.title, movies.poster_link, movies.certificate, movies.meta_score, movies.runtime, movies.overview, movies.director_id, directors.name FROM movies, directors WHERE movies.director_id = directors.id AND movies.id = {movie_id};"
        cur = db.cursor()
        cur.execute(sql)
        movie_row = cur.fetchone()
        #print(f"MOVIE ROW: {movie_row}")
        if movie_row != None:
            return Movie(movie_id, *movie_row)
        else:
            return None

    def setStars(self):
        sql = f"SELECT stars.id, stars.name FROM stars, stars_in WHERE stars_in.movie_id = {self.id} AND stars_in.star_id = stars.id;"
        cur = db.cursor()
        cur.execute(sql)
        star_rows = cur.fetchall()
        self.stars = [Star(id, name) for (id, name) in star_rows]

class Star():
    def __init__(self, id, name):
        self.id = id
        self.name = name


# CREATE TABLE showings
# (
#     id SERIAL PRIMARY KEY,
#     showing_date DATE NOT NULL,
#     start_time TIME NOT NULL,
#     end_time TIME NOT NULL,
#     movie_id INT NOT NULL,
#     theater_id INT NOT NULL,
#     FOREIGN KEY (movie_id) REFERENCES movies (id),
#     FOREIGN KEY (theater_id) REFERENCES theaters (id)
# );
class Showing():
    def __init__(self, id, showing_date, start_time, end_time, movie_id, theater, reserved_seats=None):
        self.id = id
        self.showing_date = showing_date
        self.start_time = start_time
        self.end_time = end_time
        self.movie_id = movie_id
        self.theater = theater
        self.reserved_seats = reserved_seats
    
    def prettyString(self):
        return f"Theater {self.theater.num}, Date: {self.showing_date}, Start: {self.start_time}, End:{self.end_time}"
    
    def getShowingByIdWithTheater(showing_id):
        showing_sql = f"SELECT showing_date, start_time, end_time, movie_id, theater_id FROM showings WHERE showings.id = {showing_id};"
        cur = db.cursor()
        cur.execute(showing_sql)
        showing_row = cur.fetchone()
        cur.close()
        if showing_row != None:
            (_, _, _, _, theater_id) = showing_row
            theater = Theater.getTheaterByIdWithSeats(theater_id)
            return Showing(showing_id, *(showing_row[:len(showing_row)-1]), theater, get_reserved_seats_by_showing_id(showing_id))
        else:
            return None

class Theater():
    def __init__(self, id, num, seats=None):
        self.id = id
        self.num = num
        self.seats = seats
    
    def getTheaterByIdWithSeats(theater_id):
        num_sql = f"SELECT num FROM theaters WHERE id = {theater_id};"
        cur = db.cursor()
        cur.execute(num_sql)
        theater_num = cur.fetchone()[0]
        if theater_num != None:
            seats_sql = f"SELECT seats.id, seats.row, seats.num FROM seats WHERE seats.theater_id = {theater_id};"
            cur.execute(seats_sql)
            seats = cur.fetchall()
            cur.close()
            return Theater(theater_id, theater_num, seats)
        else:
            cur.close()
            return None

class Reservation():
    def __init__(self, id, user_id, showing_id):
        self.id = id
        self.user_id = user_id
        self.showing_id = showing_id
        self.showing = Showing.getShowingByIdWithTheater(self.showing_id)
        self.movie = Movie.getMovieByIdWithDirectorName(self.showing.movie_id)
        self.seats = get_seats_row_number_from_ids(get_reserved_seats_by_reservation_id(self.id))

def delete_seat_reservations_and_reservations_by_id(reservation_ids):
    #First delete seat reservations
    sql_seat_reservations = f"DELETE FROM seat_reservations WHERE {' OR '.join(map(lambda reservation_id: f'seat_reservations.reservation_id = {reservation_id}', reservation_ids))};"
    cur = db.cursor()
    cur.execute(sql_seat_reservations)

    #Then delete reservations
    sql_reservations = f"DELETE FROM reservations WHERE {' OR '.join(map(lambda reservation_id: f'reservations.id = {reservation_id}', reservation_ids))};"
    cur = db.cursor()
    cur.execute(sql_reservations)
    db.commit()
    cur.close()


def get_reservations_by_user_id(user_id):
    sql = f"SELECT id, user_id, showing_id FROM reservations WHERE user_id = {user_id}"
    cur = db.cursor()
    cur.execute(sql)
    reservation_tuples = cur.fetchall()
    #print("RESERVATION TUPLES: ", reservation_tuples)
    reservations = [Reservation(*reservation_tuple) for reservation_tuple in reservation_tuples]
    return reservations


def get_reserved_seats_by_showing_id(showing_id):
    sql = f"SELECT seat_reservations.seat_id FROM seat_reservations, reservations WHERE seat_reservations.reservation_id = reservations.id AND reservations.showing_id = {showing_id};"
    cur = db.cursor()
    cur.execute(sql)
    reserved_seats = cur.fetchall()
    cur.close()
    return [reserved_seat_tuple[0] for reserved_seat_tuple in reserved_seats]

def get_reserved_seats_by_reservation_id(reservation_id):
    sql = f"SELECT seat_reservations.seat_id FROM seat_reservations, reservations WHERE seat_reservations.reservation_id = {reservation_id};"
    cur = db.cursor()
    cur.execute(sql)
    reserved_seats = cur.fetchall()
    cur.close()
    return [reserved_seat_tuple[0] for reserved_seat_tuple in reserved_seats]

def get_seats_row_number_from_ids(seat_ids):
    sql = f"SELECT row, num FROM seats WHERE {' OR '.join([ f'seats.id = {seat_id}' for seat_id in seat_ids ])};"
    cur = db.cursor()
    cur.execute(sql)
    seats_row_num = cur.fetchall()
    cur.close()
    return seats_row_num


def get_all_showings_for_movie_id(movie_id):
    sql = f"SELECT showings.id, showing_date, start_time, end_time, movie_id, theater_id, theaters.num FROM showings, theaters WHERE movie_id = {movie_id} AND theaters.id = showings.theater_id ORDER BY showing_date, start_time;"
    cur = db.cursor()
    cur.execute(sql)
    all_rows = cur.fetchall()
    cur.close()
    return [Showing(id,date,start,end,movie_id,Theater(theater_id, theater_num)) for (id, date, start, end, movie_id, theater_id, theater_num) in all_rows]

def get_all_movies_id_title_and_image_with_a_showing_ordered_by_date():
    sql = "SELECT movies.id AS movie_id, movies.title, movies.poster_link, MIN(showings.showing_date + showings.start_time) AS earliest_showing_datetime FROM movies JOIN showings ON movies.id = showings.movie_id GROUP BY movies.id, movies.title, movies.poster_link ORDER BY earliest_showing_datetime;"
    cur = db.cursor()
    cur.execute(sql)
    all_rows = cur.fetchall()
    cur.close()
    return [{"id": id, "title" : title, "poster_link":poster_link, "earliest_showing":earliest_showing} for (id, title, poster_link, earliest_showing) in list(all_rows)]

def __select_user(id=None, email=None) -> Optional[User]:
    if id != None or email != None:
        if id != None:
            sql = f"SELECT id, name, email, password_hash FROM users WHERE id = {id}"
        elif email != None:
            sql = f"SELECT id, name, email, password_hash FROM users WHERE email = '{email}'"
        cur = db.cursor()
        cur.execute(sql)
        data_row = cur.fetchone()
        cur.close()
        if data_row == None:
            return None
        else:
            (id, name, email, password_hash) = data_row
            user = User(name=name, email=email)
            user.id = id
            user.password_hash = password_hash
        return user
    else:
        #print("! YOU HAVE TO SPECIFY EITHER AN ID OR EMAIL !")
        return None

@login.user_loader
def select_user_by_id(id) -> Optional[User]:
    return __select_user(id=id)

def select_user_by_email(email) -> Optional[User]:
    return __select_user(email=email)

def insert_user(user):
    if user != None and type(user) == User and user.password_hash != None:
        cur = db.cursor()
        sql = f"""INSERT INTO users (name, email, password_hash)
                  VALUES ('{user.name}', '{user.email}', '{user.password_hash}')"""
        cur.execute(sql)
        db.commit()
        cur.close()
        return user
    else:
        print("! INSERT NOT DONE !")
        print(f"User was either None or not a User or password was not set. user = {user}")

def does_showing_exist(showing_id):
    cur = db.cursor()
    sql = f"SELECT id FROM showings WHERE showings.id = {showing_id}"
    cur.execute(sql)
    got_id = cur.fetchone()
    retbool = got_id != None# and got_id == showing_id
    retmsg = ""
    if not retbool: 
        retmsg = f"Showing with id={showing_id} does not exists\n"
    return (retbool, retmsg)
    

def is_seat_unreserved(seat_id, showing_id):
    cur = db.cursor()
    sql = f"SELECT seat_id FROM seat_reservations, reservations WHERE seat_id = {seat_id} AND reservations.id = reservation_id AND reservations.showing_id = {showing_id}"
    cur.execute(sql)
    got_id = cur.fetchone()
    cur.close()
    retbool = got_id == None
    retmsg = ""
    if not retbool:
        retmsg = retmsg + f"Seat with id={seat_id} is reserved\n"
    return (retbool, retmsg)

def are_seats_unreserved(seat_ids, showing_id):
    retbool = True
    retmsg = ""
    for seat_id in seat_ids:
        (bool1, msg1) = is_seat_unreserved(seat_id, showing_id)
        retbool = retbool and bool1
        retmsg = retmsg + msg1
    return (retbool, retmsg)

def find_theater_by_showing(showing_id):
    cur = db.cursor()
    sql = f"SELECT theater_id FROM showings WHERE id = {showing_id}"
    cur.execute(sql)
    theater_id = cur.fetchone()
    cur.close()
    if theater_id == None:
        raise Exception("Couldn't find theater from showing id")
    (retval,) = theater_id
    return retval

def is_seat_valid(seat_id, showing_id):
    theater_id = find_theater_by_showing(showing_id)
    cur = db.cursor()
    sql = f"SELECT id FROM seats WHERE id = {seat_id} AND theater_id = {theater_id}"
    cur.execute(sql)
    got_id = cur.fetchone()
    cur.close()
    retbool = got_id != None
    retmsg = ""
    if not retbool:
        retmsg = retmsg + f"Seat with id={seat_id} in theater with id = {theater_id} does not exist\n"
    return (retbool, retmsg)


def are_seats_valid(seat_ids, showing_id):
    retbool = True
    retmsg = ""
    for seat_id in seat_ids:
        (bool1, msg1) = is_seat_valid(seat_id, showing_id)
        retbool = retbool and bool1
        retmsg = retmsg + msg1
    return (retbool, retmsg)

def is_reservation_valid(showing_id, seat_ids):
    (bool1, msg1) = does_showing_exist(showing_id)
    (bool2, msg2) = are_seats_valid(seat_ids, showing_id)
    (bool3, msg3) = are_seats_unreserved(seat_ids, showing_id)
    retbool = bool1 and bool2 and bool3
    retmsg = "\n" + msg1 + "\n" + msg2 + "\n" + msg3
    return (retbool, retmsg)

def insert_seat_reservation(seat_id, reservation_id):
    sql = f"INSERT INTO seat_reservations (seat_id, reservation_id) VALUES ({seat_id}, {reservation_id})"
    cur = db.cursor()
    cur.execute(sql)
    db.commit()
    cur.close()    

def insert_reservation(showing_id, seat_ids, user_id):
    sql = f"INSERT INTO reservations (user_id, showing_id) VALUES ({user_id}, {showing_id}) RETURNING id"
    cur = db.cursor()
    cur.execute(sql)
    reservation_id = cur.fetchone()[0]
    db.commit()
    cur.close()
    for seat_id in seat_ids:
        insert_seat_reservation(seat_id, reservation_id)