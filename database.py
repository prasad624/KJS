from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, TextAreaField


Base = declarative_base()


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
