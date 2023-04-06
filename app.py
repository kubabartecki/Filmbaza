import psycopg2
from config import DATABASE_URL
from flask import Flask, session, render_template, redirect, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import is_valid_mail, login_required


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
            print ("Adres email jest poprawny")
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
            #return render_template('register.html', message=message) -> Będzie możliwe wyświetlanie komunikatu jak front doda możliwość wyświetlenia message
            print(message)
            return redirect("/register")
        else:
            salt_length = 12
            hashed_password = generate_password_hash(password, salt_length=salt_length, method = 'sha256')
            cursor.execute('INSERT INTO \"User\" (mail, password, username, name, surname, rank_id_rank)' 
                        'VALUES(%s, %s, %s, %s, %s, %s)',
                        [email, hashed_password, username, name, surname, 1])
        
            #Sprawdzanie całej bazy w Userze
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
            return redirect("/")
        email = request.form.get("email")
        if not request.form.get("password"):
            return redirect("/")
        password = request.form.get("password")
        connection = psycopg2.connect(url)
        cursor = connection.cursor()
        cursor.execute("SELECT \"User\".id_user, \"User\".password FROM \"User\" WHERE \"User\".mail = %s", [email])
        records = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(records) == 1:
            user_id = records[0][0]
            hash_from_db = records[0][1]
        else:
            return redirect("/")
        if check_password_hash(hash_from_db, password):
            session["user_id"] = user_id
            return redirect("/home")
        else:
            return redirect("/")
    else:
        return redirect("/")


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    return render_template("main_page.html", films=[], logged_user=[])

if __name__ == "__main__":
    app.run()