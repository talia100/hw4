from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from yelp import find_coffee
from flask_login import current_user, login_user, login_required, logout_user
from models import db, login, UserModel
from wiki import findBirths
import logging
logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('test.log') 
logger.addHandler(handler)

class loginForm(FlaskForm):
    email=StringField(label="Enter email", validators=[DataRequired(),Email()])
    password=PasswordField(label="Enter password",validators=[DataRequired(), Length(min=6,max=16)])
    submit=SubmitField(label="Login")

class birthdayForm(FlaskForm):
    date=DateField(label = "Enter birth date", validators=[DataRequired()])
    number_of_results=IntegerField(label = "number_of_results", validators=[DataRequired()])
    submit=SubmitField(label="Submit")

#passwords={}
#passwords['lhhung@uw.edu']='qwerty'

app = Flask(__name__)
app.secret_key="a secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login.init_app(app)

def addUser(email, password):
    #check if email or username exits
    user=UserModel()
    user.set_password(password)
    user.email=email
    db.session.add(user)
    db.session.commit()

@app.before_first_request
def create_table():
    db.create_all()
    user = UserModel.query.filter_by(email = "lhhung@uw.edu").first()
    if user is None:
        addUser("lhhung@uw.edu","qwerty")    
    
@app.route("/home")
@login_required
def findCoffee():
    return render_template("home.html", myData=find_coffee())

@app.route("/")
def redirectToLogin():
    return redirect("/login")

@app.route("/login",methods=['GET','POST'])
def login():
    form=loginForm()
    if form.validate_on_submit():
        if request.method == "POST":
            email=request.form["email"]
            pw=request.form["password"]
            user = UserModel.query.filter_by(email = email).first()
            if user is not None and user.check_password(pw) :
                login_user(user)
                return redirect('/home')
    return render_template("login.html",form=form)

@app.route("/birthdays",methods=['GET','POST'])
def birthdays():
    form=birthdayForm()
    sortYear = ''
    if form.validate_on_submit():
        if request.method == "POST":
            date=request.form["date"]
            number=request.form["number_of_results"]
            date_split = date.split('-')
            year = date_split[0]
            month = date_split[1]
            day = date_split[2]
            monthDay = month + '/' + day
            print(year, monthDay)
            sortYear = findBirths(monthDay, year, size = number)
            print(sortYear[0]['text'])
    return render_template("birthdays.html",form=form, a = sortYear)

# have myData = wiki at findBirths (date and number) call with date and number from form - done 

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
