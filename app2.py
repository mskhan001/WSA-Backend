from flask import Flask, request, jsonify, make_response
import requests
import json
from functools import wraps
import uuid
import datetime
from datetime import datetime, timedelta
from models.OTP import Users, OTPSIN, OTPSUP, generateOTP
from models.contacts import RegisteredContactsModel
from models.location import UserLocation
import jwt
app = Flask(__name__)

API_KEY = "AIzaSyDKyC8k5UNUx5tQ3wDJNz5ipzrsGQ_4zCU"
app.config['SECRET_KEY'] = 'Th1s1ss3cr3t'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.before_first_request
def create_table():
    db.create_all()


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Users.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


# Below function is for sending OTP during Sign Up


@app.route('/sendOTPSUP', methods=['POST'])
def send_otp_sup():
    data = request.get_json()
    print(data)

    # assuming user is sending the mobile data in his js
    mobile_no = data['phone_num']

    # Checking if, the user has alreadt verified his mobile number. If the user has already verified his mobile number,
    # he must go to Sign In
    if Users.query.filter_by(phone_number=mobile_no).first():
        return {'message': 'User already registered. Please Sign In'}

    # otp_gen stores a 4 digit random number
    otp_gen = generateOTP()

    # Right now, OTP is being printed on the console
    # For sending OTP to the mobile number, send it from here
    print(otp_gen)

    # This is some string to uniquely identify the user
    session_id = str(uuid.uuid4())
    t = datetime.now()+timedelta(seconds=120)

    # This is the otp object
    new_otp = OTPSUP(session=session_id, otp=otp_gen, expiry=t,
                     mobileno=mobile_no, verified=False)
    db.session.add(new_otp)
    db.session.commit()

    # User receives a session ID
    return jsonify({'session_id': session_id})

# Below function is for verifying OTP during SIGN UP


@app.route('/verifyOTPSUP', methods=['POST'])
def verify_otp_sup():
    data = request.get_json()

    # JSON payload from the user has OTP and sessionId
    otp = data['OTP']
    session_id = data['session_id']

    # instance of OTPSUP class with the unique id that was created
    otp_session = OTPSUP.query.filter_by(session=session_id).first()

    if (otp_session.expiry <= datetime.now()):
        db.session.delete(otp_session)
        db.session.commit()
        return jsonify({"message": "OTP expired"})

    if otp_session.otp == otp:
        otp_session.verified = True
        db.session.commit()

        # public_id is to uniquely identify the user, it is being generate
        # the user mobile number is being stored against that public id in the Users Database
        new_user = Users(public_id=str(uuid.uuid4()),
                         phone_number=otp_session.mobileno, admin=False)
        db.session.add(new_user)
        db.session.commit()

        # This is the unique token that is being generated
        token = jwt.encode({'public_id': new_user.public_id, 'exp': datetime.utcnow(
        ) + timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8'), 'message': 'registered successfully'})

    # db.session.delete(otp_session)
    db.session.commit()

    return jsonify({'message': 'OTP false'})

# Below function is for sending OTP during LOG IN


@app.route('/sendOTPSIN', methods=['POST'])
def send_otp_sin():
    data = request.get_json()
    print(data)
    mobile_no = data['phone_num']
    user1 = Users.query.filter_by(phone_number=mobile_no).first()
    if user1:
        otp_gen = generateOTP()
        print(otp_gen)
        session_id = str(uuid.uuid4())
        t = datetime.now()+timedelta(seconds=120)
        new_otp_sin = OTPSIN(session_sin=session_id, otp_sin=otp_gen,
                             expiry_sin=t, mobileno_sin=mobile_no, verified_sin=False)
        db.session.add(new_otp_sin)
        db.session.commit()
        return jsonify({'session_id': session_id})
    return make_response('Phone Number not registered', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

# Below function is for verifying OTP during SIGN IN


@app.route('/verifyOTPSIN', methods=['POST'])
def verify_otp_sin():
    data = request.get_json()

    # JSON payload from the user has session ID
    otp = data['OTP']
    session_id = data['session_id']

    # instance of OTPSIN class with the unique id that was created
    otp_session = OTPSIN.query.filter_by(session_sin=session_id).first()

    if (otp_session.expiry_sin <= datetime.now()):
        db.session.delete(otp_session)
        db.session.commit()
        return jsonify({"message": "OTP expired"})

    if otp_session.otp_sin == otp:
        otp_session.verified_sin = True
        db.session.commit()

        # This finds the mobile number of the by using session ID
        # The OTPSIN class instance which has the given sessinId is searched
        user_mobileno = OTPSIN.query.filter_by(
            session_sin=session_id).first().mobileno_sin

        # We now search for the user against which the mobile number was generate.
        user = Users.query.filter_by(phone_number=user_mobileno).first()

        # This is the unique token that is being generated
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow(
        ) + timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8'), 'message': 'Logged in successfully'})

    # db.session.delete(otp_session)
    db.session.commit()
    return jsonify({'message': 'wrong otp'})


@app.route('/savedetails', methods=['POST'])
@token_required
def save_details(self):

    data = request.get_json()
    profilename = data['profilename']
    userpin = data['userpin']
    userid = self.id
    user2 = Users.query.filter_by(id=userid).first()
    user2.profile_name = profilename
    user2.profile_pin = userpin
    db.session.add(user2)
    db.session.commit()
    return {'message': 'Details have been saved.'}


@app.route('/savecontact', methods=['POST'])
@token_required
def save_emergency_contact(self):

    # Data of Emergency contact from paylaod
    data = request.get_json()
    print(data)

    # User ID extracted from the token
    user_id = self.id

    for contact in data:
        phone_number = contact['phone_num']
        username = contact['name']

        if RegisteredContactsModel.find_by_userid_and_phone_number(user_id, phone_number):
            continue
        # return {'message': 'An item with the {} phone number already exists'.format(phone_number)}, 400

        contact = RegisteredContactsModel(username, phone_number, user_id)
        contact.save_to_db()

    # return contact.json(), 201
    return {'message': 'Contacts have been saved.'}


@app.route('/deletecontact', methods=['POST'])
@token_required
def delete_emergency_contact(self):
    # Data of Emergency contact from paylaod
    data = request.get_json()
    phone_number = data['phone_num']
    # print(self)
    # User ID extracted from the token
    user_id = self.id
    contact = RegisteredContactsModel.find_by_userid_and_phone_number(
        user_id, phone_number)
    if contact:
        contact.delete_from_db()
    return{'message': 'Contact was deleted'}


@app.route('/getallcontacts', methods=['GET'])
@token_required
def get_all_emergency_contacts(self):
    return(Users.get_all_contacts(self))
    # return {'message': 'All emergency contacts'}


@app.route('/savecurrentlocation', methods=['POST'])
@token_required
def save_curr_location(self):
    data = request.get_json()
    UserLocation(data['lat'], data['lon'], self.id).save_to_db()
    return {'message': 'Location saved'}


@app.route('/userdetails', methods=['GET'])
@token_required
def get_user_details(self):
    return self.json()


@app.route("/getlandmarks", methods=['POST'])
def findPlaces(loc=("16.5062", "80.6480"), radius=50):
    data = request.get_json()
    lat, lng = data['lat'], data['lon']
    if not lat and not lng:
        lat, lng = loc
    sahithi = []
    typi = ["hospital", 'atm', 'police station']
    data = {}
    i = 0
    for xy in typi:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type={type}&key={API_KEY}".format(
            lat=lat, lng=lng, radius=radius, type=xy, API_KEY=API_KEY)
        print(url)
        response = requests.get(url)
        res = json.loads(response.text)
        print(len(res["results"]))
        for result in res["results"]:
            info = ";".join(map(str, [result["name"], result["geometry"]["location"]
                                      ["lat"], result["geometry"]["location"]["lng"], result["place_id"]]))
            data[i] = info
            i = i+1

    return data


if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
