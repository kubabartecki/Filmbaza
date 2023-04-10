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
          
class Film():
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
        print(f"ID: {self.id}")
        print(f"album: {self.album}")
        print(f"title: {self.title}")
        print(f"director: {self.director}")
        print(f"year: {self.year}")
        print(f"country: {self.country}")
        print(f"description: {self.description}")
        print(f"avg_grade: {self.avg_grade}")
        print(f"tags: {self.tags}")