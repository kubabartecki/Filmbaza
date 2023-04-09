import re
from flask import redirect, session
from functools import wraps

def is_valid_mail(mail):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        match = re.match(pattern, mail)
        return match is not None 

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def get_rank_name(rank):
    if rank == 1:
        return "Początkujący"
    elif rank == 2:
        return "Młody filmowiec"
    elif rank == 3:
         return "Filmowiec"
    elif rank == 4:
         return "Filmomaniak"

class logged_user():
     def __init__(self, records, user_reviews_count):
          self.username = records[0][3]
          self.name = records[0][4]
          self.surname = records[0][5]
          self.rank = get_rank_name(records[0][6])
          self.no_review = user_reviews_count[0][0]
          
class film():
     def __init__(self, records):
          self.title = 0
          self.director = 0
          self.year = 0
          self.country = 0
          self.description = 0
          self.avg_grade = 0