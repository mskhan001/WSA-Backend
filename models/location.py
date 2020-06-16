from db import db


class UserLocation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float(precision=2))
    lon = db.Column(db.Float(precision=2))

    user_id = db.Column(db.String(80), db.ForeignKey('users.id'))
    user = db.relationship('Users')

    def __init__(self, lat, lon, user_id):
        self.lat = lat
        self.lon = lon
        self.user_id = user_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
