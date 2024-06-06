from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
import psycopg
from flask_login import current_user, login_user, logout_user, login_required
import app.models as model
from urllib.parse import urlsplit

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = model.select_user_by_email(form.email.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email-address or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route("/user/<user_id>", methods=['GET', 'POST'])
def user(user_id):
    # User info
    # Reservations (with seats)
    reservations = model.get_reservations_by_user_id(user_id)
    if request.method == "POST":

        #print(f"WE WANT TO PUT THE FOLLOWING TUPLE IN RESERVATION DATABASE")
        #print(f"User_id: {current_user.get_id()}, Showing_id: {showing_id}")
        #print(f"In seat reservations:")
        #print(f"{seat_ids}")
        
        reservations_to_be_deleted = list(filter(int, request.form.getlist("reservation-delete-checkbox")))
        model.delete_seat_reservations_and_reservations_by_id(reservations_to_be_deleted)
        user_page = url_for("user", user_id=user_id)
        return redirect(user_page)
    else:
        return render_template("user.html", user_id=user_id, reservations=reservations)

@app.route('/movies')
def movies():
    movies = model.get_all_movies_id_title_and_image()
    
    rows = [movies[i:i + 3] for i in range(0, len(movies), 3)]

    return render_template('movies.html', movie_name="movie_name", rows=rows)

@app.route('/movie/<movie_id>')
def movie(movie_id):
    movie = model.Movie.getMovieByIdWithDirectorName(movie_id)
    movie.setStars()
    if movie != None:
        showings = model.get_all_showings_for_movie_id(movie.id)
        print(f"LEN SHOWINGS: {len(showings)}")
        return render_template('movie.html', movie=movie, showings=showings)
        #return f"GOT THIS MOVIE ID: {movie.id} WITH TITLE: {movie.title} AND META SCORE: {movie.meta_score} AND STARS: {', '.join(map(lambda m: m.name, movie.stars))}"
    else:
        return f"GOT NONE BACK"

@app.route('/showing/<showing_id>', methods=['GET', 'POST'])
def showing(showing_id):
    showing = model.Showing.getShowingByIdWithTheater(showing_id)
    row_seat_dict = dict()
    for (seat_id, row, num) in showing.theater.seats:
        if row in row_seat_dict:
            row_seat_dict[row].append((seat_id, num))
        else:
            row_seat_dict[row] = [(seat_id, num)]
    if request.method == "POST":
        seats_reserved = []
        for (seat_id, row, num) in showing.theater.seats:
            #print(f"Seat with seta_id: {seat_id} in row: {row} num: {num} was selected:")
            if request.form.get(f'{seat_id}'):
                seats_reserved.append(seat_id)
                #print(f"Seat with seta_id: {seat_id} in row: {row} num: {num} was selected:")
        
        if len(seats_reserved) > 0:
            print(f"Seats reserved: {seats_reserved}")
            reservation_page = url_for("reservation", showing_id=showing.id, seat_ids=seats_reserved)
            return redirect(reservation_page)
        else:
            return "Fail no seats reserved"
    else:
        movie_shown = model.Movie.getMovieByIdWithDirectorName(showing.movie_id)
        return render_template("showing.html", showing=showing, movie_shown=movie_shown, row_seat_dict=row_seat_dict)
    #return f"Got showing_id: {showing_id}\nSeats: {showing.theater.seats}\nReserved seats: {showing.reserved_seats}"

#Seats reserved: [140, 184, 206, 228]
#%5B 140,%20 184,%20 206,%20 228 %5D
@app.route('/reservation/<showing_id>/<seat_ids>', methods=['GET', 'POST'])
@login_required
def reservation(showing_id, seat_ids):
    showing = model.Showing.getShowingByIdWithTheater(showing_id)
    movie = model.Movie.getMovieByIdWithDirectorName(showing.movie_id)
    #print(f"Seat ids: {seat_ids} | List(seatids): {list(seat_ids)}")
    #print(type(list(seat_ids)))
    #print(type(list(seat_ids)[0]))
    seat_ids = list(map(int, seat_ids[1:len(seat_ids)-1].split(",")))
    print(f"SEAT_IDS: {seat_ids}")
    seats_row_number = model.get_seats_row_number_from_ids(seat_ids)
    if request.method == "POST":

        #print(f"WE WANT TO PUT THE FOLLOWING TUPLE IN RESERVATION DATABASE")
        #print(f"User_id: {current_user.get_id()}, Showing_id: {showing_id}")
        #print(f"In seat reservations:")
        #print(f"{seat_ids}")
        model.insert_reservation(showing_id, seat_ids, current_user.get_id())
        return render_template('index.html', title='Home')
    else:
        return render_template("reservation.html", movie_title=movie.title, date=showing.showing_date, start_time=showing.start_time, end_time=showing.end_time, seats_row_number=seats_row_number)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = model.User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        model.insert_user(user)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
