from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, TextAreaField


import random
from datetime import datetime

Base = declarative_base()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Adjust as needed
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)  # Added name column
    otp = db.Column(db.String(6), nullable=True)

    def __repr__(self):
        return f"User(mobile_number={self.mobile_number}, name={self.name})"  # Updated representation


class FamilyHead(Base):
    __tablename__ = 'family_head'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    dob = Column(DateTime, default=datetime.utcnow, nullable=False)
    region = Column(String(25), nullable=False)
    district = Column(String(25), nullable=False)
    town = Column(String(25), nullable=False)
    village = Column(String(25))
    education = Column(String(25))
    occupation = Column(String(25))
    address = Column(String(255))
    vidhansabha = Column(String(20))
    loksabha = Column(String(20))

    # Additional fields for head-specific information (e.g., occupation)

    family_members = relationship("FamilyMember", backref="head", cascade="all, delete-orphan")


class FamilyMember(Base):
    __tablename__ = 'family_member'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))  # Consider using a more inclusive model for gender
    dob = Column(DateTime)
    relationship_to_head = Column(String(20))
    education = Column(String(20))
    occupation = Column(String(20))
    current_address = Column(String(200))

    family_head_id = Column(Integer, ForeignKey('family_head.id'), nullable=False)

    def __init__(self, name, age, gender, relationship_to_head, dob, education, occupation, current_address):
        # Update constructor to include dob
        self.name = name
        self.age = age
        self.gender = gender
        self.relationship_to_head = relationship_to_head
        self.dob = dob
        self.education = education
        self.occupation = occupation
        self.current_address = current_address

    def calculate_age(self):
        if self.dob:
            today = datetime.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        else:
            return None


class CensusForm(FlaskForm):
    name = StringField("Full Name")
    age = IntegerField("Age")
    gender = RadioField("Gender", choices=["Male", "Female", "Non-binary"])
    address = TextAreaField("Address")
    household_size = IntegerField("Household Size")
    additional_info = TextAreaField("Additional Information (optional)")

    def validate(self):
        # Add custom validations if needed
        return super().validate()


with app.app_context():
    db.create_all()


def insert_user(mobile_number, name):
    try:
        new_user = User(mobile_number=mobile_number, name=name)
        db.session.add(new_user)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error inserting user: {e}")
        db.session.rollback()
        return False


def generate_random_otp():
    """Generates a 4-digit random OTP."""
    digits = "0123456789"
    otp = ""
    for _ in range(4):
        otp += random.choice(digits)
    return otp


@app.route('/generate_otp', methods=['POST'])
def generate_otp():
    mobile_number = request.json.get('mobile_number')
    name = request.json.get('name')
    if not mobile_number:
        return jsonify({'error': 'Mobile number is required'}), 400
    insert_user(mobile_number, name)

    user = User.query.filter_by(mobile_number=mobile_number).first()
    if user:
        try:
            otp = generate_random_otp()
            user.otp = otp
            db.session.commit()

            # Choose your preferred OTP delivery method (e.g., email, in-app display, or other alternatives)
            # Implement the logic to deliver the OTP using your chosen method here
            print(f"OTP for {user.mobile_number}: {otp}")  # Example placeholder for delivery
        except Exception as e:
            print(f"Error sending OTP: {e}")
            return jsonify({'error': 'Failed to send OTP'}), 500

        return jsonify({'message': 'OTP sent successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 400


@app.route('/login', methods=['POST'])
def login():
    mobile_number = request.json.get('mobile_number')
    otp = request.json.get('otp')

    if not mobile_number or not otp:
        return jsonify({'error': 'Mobile number and OTP are required'}), 400

    user = User.query.filter_by(mobile_number=mobile_number, otp=otp).first()
    if user:
        user.otp = None  # Clear the OTP after successful login
        db.session.commit()
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid OTP'}), 401


@app.route('/submit_census', methods=['POST'])
def submit_census():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    form = CensusForm()
    if not form.validate_on_submit():
        return jsonify({'errors': form.errors}), 400

    # Save census data (adapt based on your chosen storage mechanism)
    # ...

    return jsonify({'message': 'Census form submitted successfully'})


@app.route('/get_census_data/<user_id>', methods=['GET'])
def get_census_data(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Retrieve and return census data based on your storage approach
    # ...

    return jsonify({'census_data': ...})  # Replace with actual data



