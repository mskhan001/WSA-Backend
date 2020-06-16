from db import db


class RegisteredContactsModel(db.Model):
    # __tablename__ = 'registered_contacts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    phone_number = db.Column(db.String(80))

    user_id = db.Column(db.String(80), db.ForeignKey('users.id'))
    user = db.relationship('Users')

    def __init__(self, username, phone_number, user_id):
        self.username = username
        self.phone_number = phone_number
        self.user_id = user_id

    def json(self):
        return {
            'username': self.username,
            'phone_number': self.phone_number,
            'user_id': self.user_id
        }

    @classmethod
    def find_by_userid_and_phone_number(cls, user_id, phone_number):
        return cls.query.filter_by(user_id=user_id, phone_number=phone_number).first()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
