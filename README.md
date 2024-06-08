# DIS Group project: Cinema reservation page
##### By Mark Brandt {jvq317}, Rasmus Kiel {zch403} & Simon Lykke Andersen {sxd682}.

## ER-diagram
![ER_DIS_cinema.png](/ER_DIS_cinema.png)

## Technical setup
### Requirements:
Run the code below to install the necessary modules.

    pip install -r requirements.txt


### Database init
1. Replace {username} with your database username and {databasename} with the name of your database in `app/__init__.py` file.
2. Run the sql files replacing {username} with your database username and {databasename} with the name of your database in the below collective statement.

Collected psql statement:

    psql -U {username} -d {databasename} -q -f sql_files/create_tables.sql -f sql_files/insert_movies.sql -f sql_files/insert_directors.sql -f sql_files/insert_stars.sql -f sql_files/update_movies_director.sql -f sql_files/insert_starsin.sql -f sql_files/generate_synthetic_data.sql
   
### Running flask

    export FLASK_APP=cinema.py
    flask run

### How to use
We have generated an example user:

    Email: fakeuser.email@genericemail.com
    Password: password

You can also register your own user.

The web-app consists of a movie page for the movies shown in the cinema ordered by showing date and time.

Each movie has a page with some info about the movie and the its showings.

For each showing there is a view of the seats, where red resembles already reserved seats and then a user can select seats by clicking (which turns them blue) and then click reserve.

This brings the user onto a reservation confirmation page where when the user confirms the reservation the reservation is registered in the database.

The user can see and delete their reservations on their user homepage which is accessed via. the link (with the username) in the top of the website.


## Description of fulfillment of requirements
### SQL queries
#### CREATE
We create tables in `sqlfiles/create_tables.sql` where we also make sure to model the weak relations using `ON DELETE CASADE`.

#### INSERT
We have multiple places where we use `INSERT` both when inserting the synthetic data (e.g. `insert_movies.sql`, `insert_directors.sql`, `insert_stars.sql`, `insert_starsin.sql` and `generate_synthetic_data.sql`) and multiple places in `models.py`.

#### UPDATE
We only use update when updating the `director_id` column in the `movies` table. This is done in `update_movies_director.sql`.

#### DELETE
We have used `ON DELETE CASADE` in our `create_tables.sql` and when deleting a reservation in `models.py` we generate a delete statement to delete first the seat reservations and then the reservation. (Though the seat reservations would also be deleted even if we only deleted the reservation due to the added `ON DELTE CASCADE`).

#### SELECT
We use multiple `SELECT` statements in `models.py`.

### RegEx
In `forms.py` we have added our own email validator (which is simply a regular expression) which we based on the description found [Wiki on email addresses](https://en.wikipedia.org/wiki/Email_address). Though we only support the followin TLDs `(com|org|net|int|edu|gov|mil|us|dk|se|no)`.

We also used a regular expression in `extract_IMDB_info.ipynb` to change the poster links from `imdb_top_1000.csv`to some with higher resolution. Where the change necessarry to the link was gathered from getting an example response from [OMDb API](https://www.omdbapi.com/).