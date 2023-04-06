import psycopg2
from config import DATABASE_URL
from flask import Flask, render_template, redirect, request
from werkzeug.security import check_password_hash, generate_password_hash
import re


app = Flask(__name__)
url = DATABASE_URL

  

@app.route("/", methods=["GET", "POST"])
def default():
    return render_template("login.html")

 

@app.route("/register", methods=["GET", "POST"])
  
def register():
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
        def is_valid_mail(mail):
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            match = re.match(pattern, email)
            return match is not None   
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
            max_password_length = 15
            salt_length = 12
            hashed_password = generate_password_hash(password, salt_length=salt_length, method = 'sha256')[:max_password_length]
            cursor.execute('INSERT INTO \"User\" (mail, password, username, name, surname, rank_id_rank)' 
                        'VALUES(%s,%s,%s,%s,%s,%s)',
                        [email,hashed_password,username,name,surname,1])
        
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
        if check_password_hash(pwhash=hash_from_db, password=password):
            # Tu tez bedzie przypisanie sesji do konkretnego id usera
            # tu bedzie wyciagniecie informacji o filmach z bazy
            return render_template("main_page.html", films=[], logged_user=[])
        else:
            return redirect("/")
        
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run()
