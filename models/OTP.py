import random
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from db import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(80), unique=True)
    phone_number = db.Column(db.String)
    admin = db.Column(db.Boolean)
    profile_name = db.Column(db.String)
    profile_pin = db.Column(db.String)

    contacts = db.relationship('RegisteredContactsModel', lazy='dynamic')
    messages = db.relationship('EmergencyMessagesModel', lazy='dynamic')

    def get_all_contacts(self):
        print(self)
        return {'contacts': [contact.json() for contact in self.contacts.all()]}
        # print(contacts)

    def json(self):
        return {
            "profile_name": self.profile_name,
            "phone_number": self.phone_number
        }


class OTPSUP(db.Model):
    session = db.Column(db.String(50), primary_key=True)
    otp = db.Column(db.Integer)
    expiry = db.Column(db.DateTime)
    mobileno = db.Column(db.Integer)
    verified = db.Column(db.Boolean)


class OTPSIN(db.Model):
    session_sin = db.Column(db.String(50), primary_key=True)
    otp_sin = db.Column(db.Integer)
    expiry_sin = db.Column(db.DateTime)
    mobileno_sin = db.Column(db.Integer)
    verified_sin = db.Column(db.Boolean)


class OTPCHANGEPIN(db.Model):
    otp_changepin = db.Column(db.Integer)
    session_changepin = db.Column(db.String(50), primary_key=True)
    expiry_changepin = db.Column(db.DateTime)
    verified_changepin = db.Column(db.Boolean)


def generateOTP():
    OTP = random.randrange(1000, 10000)
    return OTP
