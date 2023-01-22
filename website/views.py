from email.utils import encode_rfc2231
from nis import cat
from flask import Blueprint, render_template, flash, request, jsonify
from flask_login import login_required, current_user
from .models import Note, Student, Lesson, User
from . import db
import json
from sqlalchemy import select, join
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
import pytz


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    
    return jsonify({})

@views.route('/delete-student', methods=['POST'])
def delete_student():
    student = json.loads(request.data)
    studentId = student['studentId']
    student = Student.query.get(studentId)
    if student:
        if student.user_id == current_user.id:
            db.session.delete(student)
            db.session.commit()
            flash('Student deleted!', category='success')
    
    return jsonify({})

@views.route('/delete-lesson', methods=['POST'])
def delete_lesson():
    lesson = json.loads(request.data)
    lessonId = lesson['lessonId']
    lesson = Lesson.query.get(lessonId)
    if lesson:
        if lesson.user_id == current_user.id:
            db.session.delete(lesson)
            db.session.commit()
            flash('Lesson deleted!', category='success')
    
    return jsonify({})

@views.route('/student', methods=['GET', 'POST'])
@login_required
def student():
    if request.method == 'POST':
        name = request.form.get('name')
        org = request.form.get('org')
        tz = request.form.get('tz')
        contactmethod = request.form.get('contactmethod')
        contactinfo = request.form.get('contactinfo')
        rate = request.form.get('rate')

        exist_student = Student.query.filter_by(name=name).first()

        if exist_student:
            exist_student.org = org
            exist_student.tz = tz
            exist_student.contactmethod = contactmethod
            exist_student.contactinfo = contactinfo
            exist_student.rate = rate
            db.session.add(exist_student)
            db.session.commit()
            flash('Student updated!', category='success')
            return render_template("student.html", user=current_user)
        else:
            new_student = Student(
                name = name, 
                org = org, 
                tz = tz, 
                contactmethod = contactmethod, 
                contactinfo = contactinfo, 
                rate = rate, 
                user_id = current_user.id)
            db.session.add(new_student)
            db.session.commit()
            flash('Student added!', category='success')
            return render_template("student.html", user=current_user)

    return render_template("student.html", user=current_user)

@views.route('/invoice', methods=['GET', 'POST'])
@login_required
def invoice():

    if request.method =='POST':
        start_dt = parse(request.form.get('startdate'))
        end_dt = parse(request.form.get('enddate'))
        startdate = start_dt.strftime('%b-%d-%Y')
        enddate = end_dt.strftime('%b-%d-%Y')
        org = request.form.get('org')
        total = 0
        lessons = Lesson.query.join(Student).filter(
                                    Student.org == org,
                                    Lesson.date >= start_dt,
                                    Lesson.date <= end_dt).all()
        
        if startdate > enddate:
            flash("Invalid timeframe.", category="error")

        if org == 'all':
            lessons = Lesson.query.join(Student).filter(
                                    Lesson.date >= start_dt,
                                    Lesson.date <= end_dt).all()

        for lesson in lessons:
            total += int(((int(lesson.length)/60) * int(lesson.student.rate)))

        else:
            flash('Invoice created!', category="success")
            return render_template("invoice.html", user=current_user, lessons=lessons, org=org, startdate=startdate, enddate=enddate, total=total)

        
    return render_template("invoice.html", user=current_user)
        


@views.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    if request.method == 'GET':
        events = Lesson.query.filter_by(user_id=current_user.id).all()
        return render_template("schedule.html", user=current_user, events=events)

    if request.method == 'POST':

        name = request.form.get('name')
        exist_student = Student.query.filter_by(name=name).first()
        length = int(request.form.get('length'))
        string_date = request.form.get('date')
        tz = request.form.get('tz')
        objdate = parse(string_date)
        user_tz = pytz.timezone(tz)
        user_dtz = user_tz.localize(objdate)
        user_dtz_end = user_dtz + timedelta(minutes=length)
        student_tz = pytz.timezone(exist_student.tz)
        student_dtz = user_dtz.astimezone(student_tz)
        student_dtz_end = student_dtz + timedelta(minutes=length)

        if exist_student:
            events = Lesson.query.filter_by(user_id=current_user.id).all()
            new_lesson = Lesson(
                date = objdate, 
                length = length, 
                student_id = exist_student.id,
                student_dtz = student_dtz,
                student_dtz_end = student_dtz_end, 
                user_id = current_user.id,
                tz = tz,
                user_dtz = user_dtz,
                user_dtz_end = user_dtz_end)

            start = Lesson.query.filter(Lesson.user_dtz < new_lesson.user_dtz,
                                        Lesson.user_dtz_end > new_lesson.user_dtz).count()
            end = Lesson.query.filter(Lesson.user_dtz < new_lesson.user_dtz_end,
                                        Lesson.user_dtz_end > new_lesson.user_dtz_end).count()
            equal = Lesson.query.filter(Lesson.user_dtz == new_lesson.user_dtz,
                                        Lesson.user_dtz_end == new_lesson.user_dtz_end).count()

            if start >= 1 or end >= 1 or equal >= 1:
                flash("Your lesson time is occupied.", category="error")

            else:
                
                db.session.add(new_lesson)
                db.session.commit()
                flash('Lesson added!', category='success')
                events = Lesson.query.filter_by(user_id=current_user.id).all()
                return render_template("schedule.html", user=current_user, events=events)

        else:
            flash('Student does not exist', category='error')

    return render_template("schedule.html", user=current_user, events=events)


