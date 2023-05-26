import psycopg2
from config import DATABASE_URL
from flask import Flask, session, render_template, redirect, request, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import correct_year, login_required, login_not_required, logged_user, Film, Review, Category, Actor, catalog, is_valid_name_surname, is_valid_mail, correct_password, update_rank, is_valid_link


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
    search_string = request.args.get("search_string")
    catalog_id = request.args.get("catalog_id")
    if catalog_id == None or catalog_id == 'Wszystkie':
        cursor.execute("SELECT film.ID_FILM, film.poster, film.title, film.director, film.year, film.description, STRING_AGG(country.name, ', ') countries, (SELECT AVG(review.stars) avg_grade FROM review WHERE review.film_id_film = film.id_film) FROM film_country JOIN film ON film.id_film = film_country.film_id_film JOIN country ON film_country.country_id_country = country.id_country GROUP BY film.id_film;")
    else:
        cursor.execute('SELECT film.ID_FILM, film.poster, film.title, film.director, film.year, film.description, STRING_AGG(country.name, %s) countries, (SELECT AVG(review.stars) avg_grade FROM review WHERE review.film_id_film = film.id_film) FROM film_country JOIN film ON film.id_film = film_country.film_id_film JOIN country ON film_country.country_id_country = country.id_country JOIN film_catalog ON film.ID_FILM=film_catalog.Film_ID_FILM WHERE film_catalog.Catalog_ID_CATALOG=%s GROUP BY film.id_film;', [', ', catalog_id])
    films_records = cursor.fetchall()
    films = []
    for row in films_records:
        films.append(Film(row, [0]))
    cursor.execute('SELECT c.ID_CATALOG, c.title FROM catalog c WHERE c.User_ID_USER=%s;', [session['user_id']])
    catalogs_records = cursor.fetchall()
    catalogs = []
    if len(catalogs_records) >= 1:
        for row in catalogs_records:
            catalogs.append(catalog(row[0], row[1])) 
    cursor.close()
    connection.close()
    return render_template("main_page.html", films=films, logged_user=logged_user(user_records, user_reviews_count, catalogs), search_string=search_string, catalog='Wszystkie')
    
@app.route("/search", methods=["GET", "POST"])
def search():
    """Route used to search for movies by title, redirects to home page with search_string appended as a query string parameter."""
    if request.method == "POST":
        search_string = request.form.get("search_string").strip().upper()
        if search_string != "":
            if session.get("user_id") is None:
                return redirect(f"/?search_string={search_string}")
            else:
                return redirect(f"/home?search_string={search_string}")
    return redirect("/home")


@app.route("/film_page", methods=["GET", "POST"])
def film_page():
    """Route used to display details about a specific movie."""
    if request.method == "GET":
        movie_id = request.args.get("movie_id")
    else:
        movie_id = request.form.get('film_butt')
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM film WHERE id_film = %s", [movie_id])
    film_id = cursor.fetchone()[0]
    cursor.execute(
        "SELECT film.poster, film.title, film.director, film.year, film.description, STRING_AGG(country.name, ', ') countries, (SELECT AVG(review.stars) avg_grade FROM review WHERE review.film_id_film = film.id_film) FROM film_country JOIN film ON film.id_film = film_country.film_id_film JOIN country ON film_country.country_id_country = country.id_country WHERE film.id_film = %s GROUP BY film.id_film", [film_id])
    film_data = cursor.fetchone()
    cursor.execute(
        "SELECT u.username, r.description, r.stars FROM review r JOIN \"User\" u ON u.id_user = r.user_id_user WHERE r.film_id_film = %s;", [movie_id])
    review_data = cursor.fetchall()
    reviews = []
    for row in review_data:
        reviews.append(Review(row))
    cursor.execute(
        "SELECT A.name FROM actor A JOIN film_actor FA ON A.id_actor=FA.actor_id_actor JOIN film F ON FA.film_ID_film=F.id_film WHERE F.id_film = %s;", [movie_id])
    actors_data = cursor.fetchall()
    actors = []
    for actor in actors_data:
        actors.append(actor[0])
    cursor.close()
    connection.close()
    return render_template('film_page.html', id=film_id, album=film_data[0], original_title=film_data[1], director=film_data[2], year=film_data[3], description=film_data[4], country=film_data[5], reviews=reviews, actors=actors, movie_id=movie_id)


@app.route("/add_review_form", methods=["GET", "POST"])
def add_review_form():
    """Route used to display the form for adding a new review for a film with a given id."""
    if session.get("user_id") is None:
        return redirect("/login")
    checker = request.args.get("checker", default="True", type=str) == "True"
    message = request.args.get("message", default="", type=str)
    if request.method == "GET":
        movie_id = request.args.get("movie_id")
    else:
        movie_id = request.form.get('movie_id')
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT film.title FROM film WHERE film.ID_FILM = %s", [movie_id])
    original_title = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return render_template("add_review.html", original_title=original_title, movie_id=movie_id, checker=checker, message=message)


@app.route("/add_review", methods=["GET", "POST"])
@login_required
def add_review():
    """Route used to handle the form for adding a new review."""
    movie_id = request.form.get('movie_id')
    if not request.form.get("stars"):
        message = "Nie podano oceny!"
        return redirect(url_for("add_review_form", movie_id=movie_id, checker=False, message=message))
    if not request.form.get("description"):
        message = "Nie podano opisu!"
        return redirect(url_for("add_review_form", movie_id=movie_id, checker=False, message=message))
    try:
        stars = int(request.form.get("stars"))
    except:
        message = "Ocena ma być liczbą!"
        return redirect(url_for("add_review_form", movie_id=movie_id, checker=False, message=message))
    if stars < 0 or stars > 10 or isinstance(stars, int) == False:
        message = "Ocena ma być liczbą całkowitą!"
        return redirect(url_for("add_review_form", movie_id=movie_id, checker=False, message=message))
    description = request.form.get("description").strip()
    if len(description) <= 1 or len(description) > 500000:
        message = "Długość opisu musi zawierać od 2 do 500000 liter!"
        return redirect(url_for("add_review_form", movie_id=movie_id, checker=False, message=message))
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO review (description, stars, user_id_user, film_id_film) VALUES (%s, %s, %s, %s);", [
                   description, stars, session["user_id"], movie_id])
    connection.commit()
    cursor.close()
    connection.close()
    update_rank(url, session["user_id"])
    return redirect(f"/film_page?movie_id={movie_id}")


@app.route("/add_catalog", methods=["GET", "POST"])
@login_required
def add_catalog():
    """Route used to display the form for adding a new catalog."""
    checker = request.args.get("checker", default="True", type=str) == "True"
    message = request.args.get("message", default="", type=str)
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute("SELECT film.ID_FILM, film.poster, film.title, film.director, film.year, film.description, STRING_AGG(country.name, ', ') countries, (SELECT AVG(review.stars) avg_grade FROM review WHERE review.film_id_film = film.id_film) FROM film_country JOIN film ON film.id_film = film_country.film_id_film JOIN country ON film_country.country_id_country = country.id_country GROUP BY film.id_film;")
    films_records = cursor.fetchall()
    films = []
    for row in films_records:
        films.append(Film(row, [0]))
    cursor.close()
    connection.close()
    return render_template("add_catalog.html", films=films, checker=checker, message=message)

@app.route("/add_catalog_form", methods=['GET', 'POST'])
@login_required
def add_catalog_form():
    """Route used to handle the form for adding a new catalog."""
    if not request.form.get("name"):
        message = "Nie podano nazwy katalogu!"
        return redirect(url_for("add_catalog", message=message, checker=False))
    catalog_name = request.form.get("name").strip()
    if catalog_name == 'Wszystkie':
        message = "Taka nazwa katalogu jest zarezerwowana!"
        return redirect(url_for("add_catalog", message=message, checker=False))
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute('SELECT c.ID_CATALOG FROM catalog c WHERE c.title = %s AND c.User_ID_USER = %s', [catalog_name, session["user_id"]])
    matches = cursor.fetchall()
    if len(matches) > 0:
        message = "Taka nazwa katalogu już istnieje!"
        return redirect(url_for("add_catalog", message=message, checker=False))
    if not request.form.getlist("films"):
        message = "Nie wybrano żadnego filmu!"
        return redirect(url_for("add_catalog", message=message, checker=False))
    cursor.execute("INSERT INTO catalog (User_ID_USER, title) VALUES (%s, %s);", [session["user_id"], catalog_name])
    films = request.form.getlist("films")
    for film_id in films:
        cursor.execute("INSERT INTO film_catalog (Film_ID_FILM, Catalog_ID_CATALOG) VALUES (%s, COALESCE((SELECT catalog.ID_CATALOG FROM catalog WHERE catalog.User_ID_USER=%s AND catalog.title=%s), 1))", [film_id, session["user_id"], catalog_name])
    connection.commit()
    cursor.close()
    connection.close()
    return redirect("/home")


@app.route("/select_catalog", methods=["GET", "POST"])
@login_required
def select_catalog():
    """Route used display films within specific catalog."""
    if not request.form.get("catalog_id"):
        return redirect('/home')
    catalog_id = request.form.get("catalog_id")
    return redirect(f"/home?catalog_id={catalog_id}")

@app.route("/login", methods=["GET", "POST"])
@login_not_required
def login():
    """Route used to handle login form."""
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


@app.route("/add_film", methods=["GET", "POST"])
@login_required
def add_film():
    """Route used to display the form for adding a new film to database."""
    checker = request.args.get("checker", default="True", type=str) == "True"
    message = request.args.get("message", default="", type=str)
    connection = psycopg2.connect(url)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM category")
    categories_records = cursor.fetchall()
    categories = []
    for row in categories_records:
        categories.append(Category(row))

    cursor.execute("SELECT * FROM actor")
    actors_records = cursor.fetchall()
    actors = []
    for row in actors_records:
        actors.append(Actor(row))

    cursor.close()
    connection.close()
    
    return render_template("add_film.html", checker=checker, message=message,categories=categories, actors=actors)


@app.route("/add_actor", methods=["GET", "POST"])
@login_required
def add_actor():
    """Route used to handle the form for adding a new actor."""
    name = request.form.get("name")
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO actor (name) VALUES (%s);", [name])
    connection.commit()
    cursor.close()
    connection.close()
    print (name)
    return redirect("/add_film")

@app.route("/add_film_form", methods=["GET", "POST"])
@login_required
def add_film_form():
    """Route used to handle the form for adding a new film."""
    if request.method == "POST":
        if not request.form.get("title"):
            return redirect(url_for("add_film", checker="False", message="Nazwa filmu jest wymagana!"))
        title = request.form.get("title")
        if not request.form.get("director"):
            return redirect(url_for("add_film", checker="False", message="Podanie reżysera jest wymagane!"))
        director = request.form.get("director")
        if not request.form.get("year"):
            return redirect(url_for("add_film", checker="False", message="Podanie roku jest wymagane!"))
        year = request.form.get("year")
        if not correct_year(year):
            return redirect(url_for("add_film", checker="False", message="Podany rok jest niepoprawny!"))
        else:
            if not request.form.get("country"):
                return redirect(url_for("add_film", checker="False", message="Podanie kraju jest wymagane!"))
            country = request.form.get("country")
            if not request.form.getlist("actors"):
                return redirect(url_for("add_film", checker="False" ,message="Nie wybrano żadnego aktora!"))
            selected_actors = request.form.getlist('actors')
            if not request.form.getlist("categories"):
                return redirect(url_for("add_film", checker="False" ,message="Nie wybrano żadnej kategorii!"))
            selected_categories = request.form.getlist('categories')
            if not request.form.get("description"):
                return redirect(url_for("add_film",checker="False", message="Nie wprowadzono opisu filmu!"))
            description = request.form.get("description").strip()
            if not request.form.get("album_link"):
                return redirect(url_for("add_film", checker="False", message="Podanie linku do okładki filmu jest wymagane!"))
            album_link = request.form.get("album_link")
            if not is_valid_link(album_link):
                return redirect(url_for("add_film", checker="False", message="Podany link jest niepoprawny!"))
            print(selected_categories, selected_actors,description)
            print(title,director,year,country)
            print(album_link)
            return redirect("/add_film")

if __name__ == "__main__":
    app.run()
