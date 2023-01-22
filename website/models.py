from pytz import timezone
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    notes = db.relationship('Note')
    students = db.relationship('Student', backref='teacher')
    lessons = db.relationship('Lesson', backref='teacher')

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
 
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    org = db.Column(db.String(150))
    tz = db.Column(db.String(150))
    contactmethod = db.Column(db.String(150))
    contactinfo = db.Column(db.String(150))
    rate = db.Column(db.Integer)
    lessons = db.relationship('Lesson', backref='student')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    length = db.Column(db.Integer)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    student_dtz = db.Column(db.DateTime(timezone=True))
    student_dtz_end = db.Column(db.DateTime(timezone=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tz = db.Column(db.String(150))
    user_dtz = db.Column(db.DateTime(timezone=True))
    user_dtz_end = db.Column(db.DateTime(timezone=True))