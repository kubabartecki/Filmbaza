import psycopg2
from config import DATABASE_URL
from flask import Flask, session, render_template, redirect, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import is_valid_mail, login_required, logged_user, Film


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
url = DATABASE_URL


@app.route("/", methods=["GET", "POST"])
def default():
    session.clear()
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        if not request.form.get("name"):
            return redirect("/register")
        name = request.form.get("name")
        if not request.form.get("surname"):
            return redirect("/register")
        surname = request.form.get("surname")
        if not request.form.get("username"):
            return redirect("/register")
        username = request.form.get("username")
        if not request.form.get("email"):
            return redirect("/register")
        email = request.form.get("email")
        if not request.form.get("password"):
            return redirect("/register")
        if is_valid_mail(email):
            print("Adres email jest poprawny")
        else:
            print("Adres email jest niepoprawny")
            return redirect("/register")
        password = request.form.get("password")
        print(f"{name} {surname} {username} {email} {password}")

        connection = psycopg2.connect(url)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM \"User\" WHERE mail = %s', [email])
        email_check = cursor.fetchone()

        if email_check:
            message = "Podany adres jest juz zarejestrowany. Sprobuj zarejestrowac sie z innym adresem"
            # return render_template('register.html', message=message) -> Będzie możliwe wyświetlanie komunikatu jak front doda możliwość wyświetlenia message
            print(message)
            return redirect("/register")
        else:
            salt_length = 12
            hashed_password = generate_password_hash(
                password, salt_length=salt_length, method='sha256')
            cursor.execute('INSERT INTO \"User\" (mail, password, username, name, surname, rank_id_rank)'
                           'VALUES(%s, %s, %s, %s, %s, %s)',
                           [email, hashed_password, username, name, surname, 1])

            # Sprawdzanie całej bazy w Userze
            cursor.execute("SELECT* FROM \"User\"")
            ################################
            connection.commit()
            print("Uzytkowanik zostal pomyslnie zarejestrowany")
            test = cursor.fetchall()
            print(test)
            cursor.close()
            connection.close()

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/main_page", methods=["GET", "POST"])
def main_page():
    if request.method == "POST":
        if not request.form.get("email"):
            return render_template("login.html", checker=False, message="Niepoprawny email!")
        email = request.form.get("email")
        if not request.form.get("password"):
            return render_template("login.html", checker=False, message="Niepoprawne hasło!")
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
            return render_template("login.html", checker=False, message="Niepoprawny email!")
        if check_password_hash(hash_from_db, password):
            session["user_id"] = user_id
            return redirect("/home")
        else:
            return render_template("login.html", checker=False, message="Niepoprawne hasło lub email!")
    else:
        return redirect("/")


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
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
    if request.method == "POST":
        search_string = request.form.get("search_string")
        if search_string != "":
            return redirect(f"/home?search_string={search_string}")
    return redirect("/home")


@app.route("/film_page", methods=["GET", "POST"])
@login_required
def film_page():
    movie_id = request.form.get('film_butt')
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM film WHERE id_film = %s", [movie_id])
    film_id = cursor.fetchone()[0]
    print(film_id)
    print(request.args)
    cursor.execute(
        "SELECT film.poster, film.title, film.director, film.year, film.description, STRING_AGG(country.name, ', ') countries, (SELECT AVG(review.stars) avg_grade FROM review WHERE review.film_id_film = film.id_film) FROM film_country JOIN film ON film.id_film = film_country.film_id_film JOIN country ON film_country.country_id_country = country.id_country WHERE film.id_film = %s GROUP BY film.id_film", [film_id])
    film_data = cursor.fetchone()
    film_dict = {
        'poster': film_data[0],
        'title': film_data[1],
        'director': film_data[2],
        'year': film_data[3],
        'description': film_data[4],
        'countries': film_data[5],
        'avg_grade': film_data[6]
    }
    print(film_dict)
    return render_template('film_page.html', id=film_id, album=film_data[0], title=film_data[1], director=film_data[2], year=film_data[3], description=film_data[4], country=film_data[5])


if __name__ == "__main__":
    app.run()
