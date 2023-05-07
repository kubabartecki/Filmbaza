import psycopg2
from config import DATABASE_URL
from flask import Flask, session, render_template, redirect, request, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, login_not_required, logged_user, Film, Review, is_valid_name_surname, is_valid_mail, correct_password, update_rank


app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configure session to use filesystem 
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
url = DATABASE_URL


@app.before_first_request
def clear_session():
    """Ensuring that the user is not logged in."""
    session.clear()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_not_required
def default():
    """Main page of the website."""
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute("SELECT film.ID_FILM, film.poster, film.title, film.director, film.year, film.description, STRING_AGG(country.name, ', ') countries, (SELECT AVG(review.stars) avg_grade FROM review WHERE review.film_id_film = film.id_film) FROM film_country JOIN film ON film.id_film = film_country.film_id_film JOIN country ON film_country.country_id_country = country.id_country GROUP BY film.id_film;")
    films_records = cursor.fetchall()
    search_string = request.args.get("search_string")
    films = []
    for row in films_records:
        if search_string != None:
            cursor.execute(
                "SELECT c.name FROM category c JOIN film_category fc ON c.id_category = fc.category_id_category JOIN film f ON f.id_film = fc.film_id_film WHERE f.id_film = %s", [row[0]])
            films.append(Film(row, cursor.fetchall()[0]))
        else:
            films.append(Film(row, [0]))
    cursor.close()
    connection.close()
    return render_template("unloggedd.html", films=films, search_string=search_string)

@app.route("/main_page", methods=["GET", "POST"])
@login_not_required
def main_page():
    """Route to user login validation, handles errors within default route."""
    if request.method == "POST":
        if not request.form.get("email"):
            return redirect(url_for("login", checker="False", message="Email jest wymagany!"))
        email = request.form.get("email")
        if not request.form.get("password"):
            return redirect(url_for("login", checker="False", message="Hasło jest wymagane!"))
        password = request.form.get("password")
        connection = psycopg2.connect(url)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT \"User\".id_user, \"User\".password FROM \"User\" WHERE \"User\".mail = %s", [email])
        records = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(records) == 1:
            user_id = records[0][0]
            hash_from_db = records[0][1]
        else:
            return redirect(url_for("login", checker="False", message="Niepoprawny email!"))
        if check_password_hash(hash_from_db, password):
            session["user_id"] = user_id
            return redirect("/home")
        else:
            return redirect(url_for("login", checker="False", message="Niepoprawny email lub hasło!"))
    else:
        return redirect("/login")

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    """Main page of the website for logged user."""
    update_rank(url, session["user_id"])
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM \"User\" WHERE \"User\".id_user = %s", [session["user_id"]])
    user_records = cursor.fetchall()
    cursor.execute("SELECT COUNT(ID_REVIEW) FROM \"review\" INNER JOIN  \"User\" as u ON \"review\".User_ID_USER = u.ID_USER WHERE u.ID_USER = %s", [
                   session["user_id"]])
    user_reviews_count = cursor.fetchall()
    cursor.execute("SELECT film.ID_FILM, film.poster, film.title, film.director, film.year, film.description, STRING_AGG(country.name, ', ') countries, (SELECT AVG(review.stars) avg_grade FROM review WHERE review.film_id_film = film.id_film) FROM film_country JOIN film ON film.id_film = film_country.film_id_film JOIN country ON film_country.country_id_country = country.id_country GROUP BY film.id_film;")
    films_records = cursor.fetchall()
    search_string = request.args.get("search_string")
    films = []
    for row in films_records:
        if search_string != None:
            cursor.execute(
                "SELECT c.name FROM category c JOIN film_category fc ON c.id_category = fc.category_id_category JOIN film f ON f.id_film = fc.film_id_film WHERE f.id_film = %s", [row[0]])
            films.append(Film(row, cursor.fetchall()[0]))
        else:
            films.append(Film(row, [0]))
    cursor.close()
    connection.close()
    return render_template("main_page.html", films=films, logged_user=logged_user(user_records, user_reviews_count), search_string=search_string)

@app.route("/search", methods=["GET", "POST"])
def search():
    """Route used to search for movies, redirects to home page with search_string appended as a query string parameter."""
    if request.method == "POST":
        search_string = request.form.get("search_string").strip().title()
        if search_string != "":
            if session.get("user_id") is None:
                return redirect(f"/?search_string={search_string}")
            else:
                return redirect(f"/home?search_string={search_string}")
    return redirect("/home")

@app.route("/film_page", methods=["GET", "POST"])
def film_page():
    """Route used to display details about a specific movie."""
    movie_id = request.form.get('film_butt')
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM film WHERE id_film = %s", [movie_id])
    film_id = cursor.fetchone()[0]
    cursor.execute(
        "SELECT film.poster, film.title, film.director, film.year, film.description, STRING_AGG(country.name, ', ') countries, (SELECT AVG(review.stars) avg_grade FROM review WHERE review.film_id_film = film.id_film) FROM film_country JOIN film ON film.id_film = film_country.film_id_film JOIN country ON film_country.country_id_country = country.id_country WHERE film.id_film = %s GROUP BY film.id_film", [film_id])
    film_data = cursor.fetchone()
    cursor.execute("SELECT u.username, r.description, r.stars FROM review r JOIN \"User\" u ON u.id_user = r.user_id_user WHERE r.film_id_film = %s;", [movie_id])
    review_data = cursor.fetchall()
    reviews = []
    for row in review_data:
        reviews.append(Review(row))
    cursor.execute("SELECT A.name FROM actor A JOIN film_actor FA ON A.id_actor=FA.actor_id_actor JOIN film F ON FA.film_ID_film=F.id_film WHERE F.id_film = %s;", [movie_id])
    actors_data = cursor.fetchall()
    actors = []
    for actor in actors_data:
        actors.append(actor[0])
    cursor.close()
    connection.close()
    return render_template('film_page.html', id=film_id, album=film_data[0], original_title=film_data[1], director=film_data[2], year=film_data[3], description=film_data[4], country=film_data[5], reviews=reviews, actors=actors)

@app.route("/add_review_form", methods=["GET", "POST"])
def add_review_form():
    if session.get("user_id") is None:
        return redirect("/login")
    '''movie_id = request.form.get('nazwa buttona frontu')
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute("SELECT film.title FROM film WHERE film.id_film = %s", [movie_id])
    original_title = cursor.fetchone()[0]
    cursor.close()
    connection.close()'''
    return render_template("add_review.html", original_title='')

@app.route("/add_review", methods=["GET", "POST"])
@login_required
def add_review():
        if not request.form.get("stars"):
            return redirect("/add_review_form")
        if not request.form.get("description"):
            return redirect("/add_review_form")
        try:
            stars = int(request.form.get("stars"))
        except:
            return redirect("/add_review_form")
        if stars < 0 or stars > 10 or isinstance(stars, int) == False:
            return redirect("/add_review_form")
        description = request.form.get("description").strip()
        if len(description) <= 1 or len(description) > 500000:
            return redirect("/add_review_form")
        '''movie_id = request.form.get('nazwa buttona frontu')
        connection = psycopg2.connect(url)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO review (description, stars, user_id_user, film_id_film) VALUES (%s, %s, %s, %s);", [description, stars, session["user_id"], movie_id])
        connection.commit()
        cursor.close()
        connection.close()'''
        # Tu powinien być powrót na stronę filmu, jednakże trzeba przechować w jakimś buttonie id filmu
        return render_template("add_review.html", original_title='')

@app.route("/add_catalog", methods=["GET", "POST"])
@login_required
def add_catalog():
    return render_template("add_catalog.html")

@app.route("/login", methods=["GET", "POST"])
@login_not_required
def login():
    checker = request.args.get("checker", default="True", type=str) == "True"
    message = request.args.get("message", default="", type=str)
    return render_template("login.html", checker=checker, message=message)

@app.route("/register", methods=["GET", "POST"])
@login_not_required
def register():
    """Route called when user wants to register a new account."""
    checker = request.args.get("checker", default="True", type=str) == "True"
    message = request.args.get("message", default="", type=str)
    if request.method == "POST":
        if not request.form.get("name"):
            return redirect(url_for("register", checker="False", message="Imię jest wymagane!"))
        name = request.form.get("name")
        if not is_valid_name_surname(name):
            return redirect(url_for("register", checker="False", message="Podane imię jest niepoprawne! Nie powinno ono zawierać znaków specjalnych i co najmnniej dwa znaki!"))
        surname = request.form.get("surname")
        if not request.form.get("surname"):
            return redirect(url_for("register", checker="False", message="Nazwisko jest wymagane!"))
        if not is_valid_name_surname(surname):
            return redirect(url_for("register", checker="False", message="Podane nazwisko jest niepoprawne! Nie powinno ono zawierać znaków specjalnych i co najmniej dwa znaki!"))
        username = request.form.get("username")
        if not request.form.get("username"):
            return redirect(url_for("register", checker="False", message="Nazwa użytkownika jest wymagana!"))
        email = request.form.get("email")
        if not request.form.get("email"):
            return redirect(url_for("register", checker="False", message="Email jest wymagany!"))
        if not is_valid_mail(email):
            return redirect(url_for("register", checker="False", message="Podany email jest niepoprawny!"))
        password = request.form.get("password")
        if not request.form.get("password"):
            return redirect(url_for("register", checker="False", message="Hasło jest wymagane!"))
        if not correct_password(password):
            return redirect(url_for("register", checker="False", message="Podane hasło jest niepoprawne! Powinno ono zawierać co najmniej 8 znaków, jedną dużą literę oraz znak specjalny."))
        connection = psycopg2.connect(url)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM \"User\" WHERE mail = %s', [email])
        email_check = cursor.fetchone()
        if email_check:
            return redirect(url_for("register", checker="False", message="Podany email jest już zarejestrowany!"))
        else:
            salt_length = 12
            hashed_password = generate_password_hash(
                password, salt_length=salt_length, method='sha256')
            cursor.execute('INSERT INTO \"User\" (mail, password, username, name, surname, rank_id_rank)'
                           'VALUES(%s, %s, %s, %s, %s, %s)',
                           [email, hashed_password, username, name, surname, 1])
            connection.commit()
            cursor.close()
            connection.close()
        return redirect("/login")
    else:
        return render_template("register.html", checker=checker, message=message)
    
<<<<<<< Updated upstream
=======

@app.route("/add_film", methods=["GET", "POST"])
@login_required
def add_film():
    return render_template("add_film.html")

'''
@app.route("/", methods=["GET", "POST"])
@login_not_required
def default():
    """Default route for website. Renders login form and errors if any."""
    checker = request.args.get("checker", default="True", type=str) == "True"
    message = request.args.get("message", default="", type=str)
    return render_template("login.html", checker=checker, message=message)

@app.route("/register", methods=["GET", "POST"])
@login_not_required
def register():
    """Route called when user wants to register a new account."""
    checker = request.args.get("checker", default="True", type=str) == "True"
    message = request.args.get("message", default="", type=str)
    if request.method == "POST":
        if not request.form.get("name"):
            return redirect(url_for("register", checker="False", message="Imię jest wymagane!"))
        name = request.form.get("name")
        if not is_valid_name_surname(name):
            return redirect(url_for("register", checker="False", message="Podane imię jest niepoprawne! Nie powinno ono zawierać znaków specjalnych i co najmnniej dwa znaki!"))
        surname = request.form.get("surname")
        if not request.form.get("surname"):
            return redirect(url_for("register", checker="False", message="Nazwisko jest wymagane!"))
        if not is_valid_name_surname(surname):
            return redirect(url_for("register", checker="False", message="Podane nazwisko jest niepoprawne! Nie powinno ono zawierać znaków specjalnych i co najmniej dwa znaki!"))
        username = request.form.get("username")
        if not request.form.get("username"):
            return redirect(url_for("register", checker="False", message="Nazwa użytkownika jest wymagana!"))
        email = request.form.get("email")
        if not request.form.get("email"):
            return redirect(url_for("register", checker="False", message="Email jest wymagany!"))
        if not is_valid_mail(email):
            return redirect(url_for("register", checker="False", message="Podany email jest niepoprawny!"))
        password = request.form.get("password")
        if not request.form.get("password"):
            return redirect(url_for("register", checker="False", message="Hasło jest wymagane!"))
        if not correct_password(password):
            return redirect(url_for("register", checker="False", message="Podane hasło jest niepoprawne! Powinno ono zawierać co najmniej 8 znaków, jedną dużą literę oraz znak specjalny."))
        connection = psycopg2.connect(url)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM \"User\" WHERE mail = %s', [email])
        email_check = cursor.fetchone()
        if email_check:
            return redirect(url_for("register", checker="False", message="Podany email jest już zarejestrowany!"))
        else:
            salt_length = 12
            hashed_password = generate_password_hash(
                password, salt_length=salt_length, method='sha256')
            cursor.execute('INSERT INTO \"User\" (mail, password, username, name, surname, rank_id_rank)'
                           'VALUES(%s, %s, %s, %s, %s, %s)',
                           [email, hashed_password, username, name, surname, 1])
            connection.commit()
            cursor.close()
            connection.close()
        return redirect("/")
    else:
        return render_template("register.html", checker=checker, message=message)


@app.route("/main_page", methods=["GET", "POST"])
@login_not_required
def main_page():
    """Route to user login validation, handles errors within default route."""
    if request.method == "POST":
        if not request.form.get("email"):
            return redirect(url_for("default", checker="False", message="Email jest wymagany!"))
        email = request.form.get("email")
        if not request.form.get("password"):
            return redirect(url_for("default", checker="False", message="Hasło jest wymagane!"))
        password = request.form.get("password")
        connection = psycopg2.connect(url)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT \"User\".id_user, \"User\".password FROM \"User\" WHERE \"User\".mail = %s", [email])
        records = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(records) == 1:
            user_id = records[0][0]
            hash_from_db = records[0][1]
        else:
            return redirect(url_for("default", checker="False", message="Niepoprawny email!"))
        if check_password_hash(hash_from_db, password):
            session["user_id"] = user_id
            return redirect("/home")
        else:
            return redirect(url_for("default", checker="False", message="Niepoprawny email lub hasło!"))
    else:
        return redirect("/")


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    """Main page of the website."""
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM \"User\" WHERE \"User\".id_user = %s", [session["user_id"]])
    user_records = cursor.fetchall()
    cursor.execute("SELECT COUNT(ID_REVIEW) FROM \"review\" INNER JOIN  \"User\" as u ON \"review\".User_ID_USER = u.ID_USER WHERE u.ID_USER = %s", [
                   session["user_id"]])
    user_reviews_count = cursor.fetchall()
    # tutaj i w innych miejscach gdzie beda recenzje bedzie trzeba dodac czy przypadkiem ktos nie awansowal, a wtedy trzeba zmienic range
    cursor.execute("SELECT film.ID_FILM, film.poster, film.title, film.director, film.year, film.description, STRING_AGG(country.name, ', ') countries, (SELECT AVG(review.stars) avg_grade FROM review WHERE review.film_id_film = film.id_film) FROM film_country JOIN film ON film.id_film = film_country.film_id_film JOIN country ON film_country.country_id_country = country.id_country GROUP BY film.id_film;")
    films_records = cursor.fetchall()
    search_string = request.args.get("search_string")
    films = []
    for row in films_records:
        if search_string != None:
            cursor.execute(
                "SELECT c.name FROM category c JOIN film_category fc ON c.id_category = fc.category_id_category JOIN film f ON f.id_film = fc.film_id_film WHERE f.id_film = %s", [row[0]])
            films.append(Film(row, cursor.fetchall()[0]))
        else:
            films.append(Film(row, [0]))
    cursor.close()
    connection.close()
    return render_template("main_page.html", films=films, logged_user=logged_user(user_records, user_reviews_count), search_string=search_string)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Route used to search for movies, redirects to home page with search_string appended as a query string parameter."""
    if request.method == "POST":
        search_string = request.form.get("search_string").strip().title()
        if search_string != "":
            return redirect(f"/home?search_string={search_string}")
    return redirect("/home")


@app.route("/film_page", methods=["GET", "POST"])
@login_required
def film_page():
    """Route used to display details about a specific movie."""
    movie_id = request.form.get('film_butt')
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM film WHERE id_film = %s", [movie_id])
    film_id = cursor.fetchone()[0]
    cursor.execute(
        "SELECT film.poster, film.title, film.director, film.year, film.description, STRING_AGG(country.name, ', ') countries, (SELECT AVG(review.stars) avg_grade FROM review WHERE review.film_id_film = film.id_film) FROM film_country JOIN film ON film.id_film = film_country.film_id_film JOIN country ON film_country.country_id_country = country.id_country WHERE film.id_film = %s GROUP BY film.id_film", [film_id])
    film_data = cursor.fetchone()
    cursor.execute("SELECT u.username, r.description, r.stars FROM review r JOIN \"User\" u ON u.id_user = r.user_id_user WHERE r.film_id_film = %s;", [movie_id])
    review_data = cursor.fetchall()
    reviews = []
    for row in review_data:
        reviews.append(Review(row))
    cursor.close()
    connection.close()
    return render_template('film_page.html', id=film_id, album=film_data[0], original_title=film_data[1], director=film_data[2], year=film_data[3], description=film_data[4], country=film_data[5], reviews=reviews)


@app.route("/add_review_form", methods=["GET", "POST"])
@login_required
def add_review_form():
    return render_template("add_review.html", original_title='')
'''
>>>>>>> Stashed changes
if __name__ == "__main__":
    app.run()
