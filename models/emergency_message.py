from db import db


class EmergencyMessagesModel(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    phone_num = db.Column(db.String)
    message = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users')

    def __init__(self, phone_num, message, user_id):
        self.phone_num = phone_num
        self.message = message
        self.user_id = user_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
