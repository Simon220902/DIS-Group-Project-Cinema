from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
import psycopg
from flask_login import current_user, login_user, logout_user, login_required
import app.models as model
from urllib.parse import urlsplit

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user', user_id=current_user.get_id()))
    form = LoginForm()
    if form.validate_on_submit():
        user = model.select_user_by_email(form.email.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email-address or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('movies')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route("/user/<user_id>", methods=['GET', 'POST'])
@login_required
def user(user_id):
    if user_id == current_user.get_id():
        # User info
        # Reservations (with seats)
        reservations = model.get_reservations_by_user_id(user_id)
        if request.method == "POST":
            reservations_to_be_deleted = list(filter(int, request.form.getlist("reservation-delete-checkbox")))
            model.delete_seat_reservations_and_reservations_by_id(reservations_to_be_deleted)
            user_page = url_for("user", user_id=user_id)
            return redirect(user_page)
        else:
            return render_template("user.html", reservations=reservations)
    else:
        return render_template('failure_page.html', failure_message = f"The user_id in the url does not match the logged in user") # TODO: FAILURE PAGE

@app.route('/')
@app.route('/movies')
def movies():
    movies = model.get_all_movies_id_title_and_image_with_a_showing_ordered_by_date()
    rows = [movies[i:i + 3] for i in range(0, len(movies), 3)]
    return render_template('movies.html', movie_name="movie_name", rows=rows)

@app.route('/movie/<movie_id>')
def movie(movie_id):
    movie = model.Movie.getMovieByIdWithDirectorName(movie_id)
    if movie != None:
        movie.setStars()
        showings = model.get_all_showings_for_movie_id(movie.id)
        return render_template('movie.html', movie=movie, showings=showings)
    else:
        return render_template('failure_page.html', failure_message = f"Could not find movie with name=\"{movie.title}\"")

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
        seats_reserved = list(map(int, request.form.getlist('available-seat-checkbox')))#[]
        if len(seats_reserved) > 0:
            reservation_page = url_for("reservation", showing_id=showing.id, seat_ids=seats_reserved)
            return redirect(reservation_page)
        else:
            return render_template('failure_page.html', failure_message = f"No seats where selected for reservation!!!") # TODO: ADD FAILURE PAGE HERE (thOUGH ALSO MAKE THIS BASICALLY IMPOSSIBLE BY CHANGING UI (BUT REDIRECT TO FAILURE PAGE))
    else:
        movie_shown = model.Movie.getMovieByIdWithDirectorName(showing.movie_id)
        return render_template("showing.html", showing=showing, movie_shown=movie_shown, row_seat_dict=row_seat_dict)

@app.route('/reservation/<showing_id>/<seat_ids>', methods=['GET', 'POST'])
@login_required
def reservation(showing_id, seat_ids):
    showing = model.Showing.getShowingByIdWithTheater(showing_id)
    movie = model.Movie.getMovieByIdWithDirectorName(showing.movie_id)
    seat_ids = list(map(int, seat_ids[1:len(seat_ids)-1].split(",")))
    print(f"SEAT_IDS: {seat_ids}")
    seats_row_number = model.get_seats_row_number_from_ids(seat_ids)
    if request.method == "POST":
        (validbool, errmsg) = model.is_reservation_valid(showing_id, seat_ids)
        if validbool:
            model.insert_reservation(showing_id, seat_ids, current_user.get_id())
            return render_template("succ_reservation.html", movie_title=movie.title, date=showing.showing_date, start_time=showing.start_time, end_time=showing.end_time, seats_row_number=seats_row_number) # TODO: GO TO SUCCESS PAGE FOR RESERVATION
        else:
            return render_template('failure_page.html', failure_message = errmsg)
    else:
        return render_template("reservation.html", movie_title=movie.title, date=showing.showing_date, start_time=showing.start_time, end_time=showing.end_time, seats_row_number=seats_row_number)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('movies'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user', user_id=current_user.get_id()))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = model.User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        model.insert_user(user)
        flash('Congratulations, you are now a registered user!')
        next = request.args.get("next")
        if next:
            return redirect(url_for('login', next=next))
        else:
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
