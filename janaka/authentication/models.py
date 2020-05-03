from janaka.db import db

class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def save(self):
        return db.user.insert_one(self.json())

    def json(self):
        return ({
            'email':self.email,
            'password':self.password
        })