import re, psycopg2
from flask import redirect, session
from functools import wraps


def is_valid_mail(mail):
    """The function checks if the email address is valid."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    match = re.match(pattern, mail)
    return match is not None


def is_valid_name_surname(name):
    pattern = r'^([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{1,20}([ -][A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{1,20})?)$'
    match = re.match(pattern, name)
    return match is not None

def correct_year(year):
    pattern = r"^\d{4}$"
    match = re.match(pattern, year)
    return match is not None


def correct_password(password):
    pattern = r'^(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&ęóąśłżźćńĘÓĄŚŁŻŹĆŃ]{8,}$'
    match = re.match(pattern, password)
    return match is not None


def login_required(f):
    """Decorator function that checks if a user is logged in. If not, the function redirects to the login page."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def login_not_required(f):
    """Decorator function that checks if a user is logged in. If so, the function redirects to the home page."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return f(*args, **kwargs)
        else:
            return redirect("/home")
    return decorated_function

def get_rank_name(rank):
    """The function returns the string equivalent of rank."""
    if rank == 1:
        return "Początkujący"
    elif rank == 2:
        return "Młody filmowiec"
    elif rank == 3:
        return "Filmowiec"
    elif rank == 4:
        return "Filmomaniak"

def get_rank_id(reviews):
    """The function returns the id of rank based on the number of reviews."""
    if reviews >= 0 and reviews <= 10:
        return 1
    elif reviews >= 11 and reviews <= 50:
        return 2
    elif reviews >= 51 and reviews <= 100:
        return 3
    elif reviews > 100:
        return 4

def update_rank(url, user_id):
    """The function updates user rank in database."""
    connection = psycopg2.connect(url)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(ID_REVIEW) FROM \"review\" INNER JOIN  \"User\" as u ON \"review\".User_ID_USER = u.ID_USER WHERE u.ID_USER = %s", [
                   session["user_id"]])
    reviews = cursor.fetchone()[0]
    rank_id = get_rank_id(reviews)
    cursor.execute(
        "UPDATE \"User\" SET rank_id_rank = %s WHERE id_user = %s;", [rank_id, user_id])
    connection.commit()
    cursor.close()
    connection.close()
    
class logged_user():
    """Class used to improve code readability and to make it easier to pass values about logged user to the frontend."""

    def __init__(self, records, user_reviews_count):
        self.username = records[0][3]
        self.name = records[0][4]
        self.surname = records[0][5]
        self.rank = get_rank_name(records[0][6])
        self.no_review = user_reviews_count[0][0]


class Film():
    """Class used to improve code readability and to make it easier to pass values about specific film to the frontend."""

    def __init__(self, records, tags):
        self.id = records[0]
        self.album = records[1]
        self.title = records[2]
        self.director = records[3]
        self.year = records[4]
        self.description = records[5]
        self.country = records[6]
        if records[7] != None:
            self.avg_grade = round(records[7], 2)
        else:
            self.avg_grade = records[7]
        self.tags = tags

    def Show(self):
        """The function used for the debugging process."""
        print(f"ID: {self.id}")
        print(f"album: {self.album}")
        print(f"title: {self.title}")
        print(f"director: {self.director}")
        print(f"year: {self.year}")
        print(f"country: {self.country}")
        print(f"description: {self.description}")
        print(f"avg_grade: {self.avg_grade}")
        print(f"tags: {self.tags}")

class Review():
    def __init__(self, records):
        self.autor = records[0]
        self.description = records[1]
        self.grade = records[2]

class Category:
    def __init__(self, records):
        self.id = records[0]
        self.name = records[1]
    
    def Show(self):
        print(f"ID: {self.id}")
        print(f"Name: {self.name}")