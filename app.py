from flask import Flask,render_template,session
from flask import request, redirect, url_for, flash
from sqlalchemy import LargeBinary
import uuid


app = Flask(__name__)

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    username = db.Column(db.String, primary_key=True)
    name=db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role=db.Column(db.String(20), nullable=False)  # 'user' or 'admin'


class Complaint(db.Model):
    id = db.Column(db.String, primary_key=True)
    username=db.Column(db.String,nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    image= db.Column(LargeBinary)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '23232323232323'
db.init_app(app)
@app.route('/',methods=["POST",'GET']) 
def login():
    print("Hi")
    if request.method == 'POST':
        print("bye")
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = user.username
            session['role'] = user.role
            flash('Logged in successfully!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = 'user'  # Default role is 'user'
        if not username or not name or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))
        new_user = User(username=username, name=name, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
    return render_template('register.html')

@app.route('/user_dashboard')
def user_dashboard():
    if 'username' not in session or session.get('role') != 'user':
        flash('Please log in as a user to access this page', 'warning')
        return redirect(url_for('login'))

    

    return render_template('dashboard.html')

@app.route('/user_complaint',methods=['POST',"GET"])
def user_comlaint():
    if request.method == 'POST':
        category = request.form['category']
        location = request.form['location']
        department = request.form['department']
        description = request.form['description']
        file = request.files.get('image')
        if file:
            image_data = file.read()  # read raw bytes from file
        else:
            image_data = None


        if not category or not location or not department or not description:
            flash('All fields are required to submit a complaint', 'danger')
            return redirect(url_for('user_dashboard'))

        new_complaint = Complaint(
            id=str(uuid.uuid4()),
            username=session['username'],
            category=category,
            location=location,
            department=department,
            description=description,
            image=image_data
        )
        db.session.add(new_complaint)
        db.session.commit()

        flash('Complaint submitted successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    return render_template('fileComplaint.html')

@app.route('/admin')
def complaint():
    return render_template('admin_dashboard.html')    

@app.route('/user_track')
def user_track():
    return render_template('trackComplaint.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)