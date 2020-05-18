import random
import os
import json
import datetime
import uuid
from tempfile import mkdtemp
#from flask_session import Session
from flask_login import LoginManager
from functools import wraps
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from flask import (
    flash, g, redirect, render_template, request, url_for, Flask, send_from_directory, session
)

# Import random to shuffle distro list
import random
# Use SQLite3 for the Distro Database
import sqlite3

app = Flask(__name__)
# change secret key in final deployment
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#login_manager = LoginManager()
#login_manager.init_app(app)

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/therapistlogin")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#app.config['SECRET_KEY'] = os.urandom(24)


swear_text = open("static/swear")
swears = swear_text.read().strip().split()

@app.route("/moderation", methods = ['POST'])
def moderation():
    #try:
    if session["user_id"] != "aviwad" and session["user_id"] != "rohan" and session["user_id"] != "eshaan" and session["user_id"] != "aryan":
        return redirect("/therapistlogin")
    else:
        db = sqlite3.connect('questionsanswers.sql')
        cursor = db.cursor()
        if "delete" in request.form:
            cursor.execute('''DELETE FROM questions WHERE ID=(?)''',[request.form["delete"]])
            # find row with same ID as request.form["delete"] and delete it
        else:
            cursor.execute('''UPDATE questions SET moderated=1 WHERE ID=(?)''',[request.form["approve"]])
            # find row with same ID as request.form["approve"] and change moderated to 1
        db.commit()
        db.close()
    #except:
        #return redirect("/therapistlogin")
    return redirect(url_for("index"))

@app.route("/answer", methods = ['POST'])
def answer():
    if session.get("user_id") is None:
        return redirect("/therapistlogin")
    else:
        db = sqlite3.connect('questionsanswers.sql')
        cursor = db.cursor()
        # insert answer
        cursor.execute("INSERT INTO answers ('question ID',answer,name,codename,'ip address',date) VALUES (?,?,?,?,?,?)",(request.form["submit"],request.form["answer"],session["name"],session["user_id"],request.environ.get('HTTP_X_REAL_IP', request.remote_addr),datetime.datetime.now().strftime('%b/%d/%Y')))     #(result['name'],datetime.datetime.now().strftime('%b/%d/%Y'),result['question'],request.environ.get('HTTP_X_REAL_IP', request.remote_addr),str(uuid.uuid4()),0,0))
        #cursor.execute('''DELETE FROM questions WHERE ID=(?)''',[request.form["delete"]])
        # update question to answered
        cursor.execute('''UPDATE questions SET answered=1 WHERE ID=(?)''',[request.form["submit"]])
            # find row with same ID as request.form["approve"] and change moderated to 1
        db.commit()
        db.close()
    #if request.method == 'POST':
    #print("moderated!")
    return redirect(url_for("index"))

@app.route("/")
def index():
    if session.get("user_id") is None:
        return render_template('index.html')
    else:
        if session["user_id"] == "aviwad" or session["user_id"] == "rohan" or session["user_id"] == "eshaan" or session["user_id"] == "aryan":
            db = sqlite3.connect('questionsanswers.sql')
            cursor = db.cursor()
            cursor.execute('''SELECT * FROM questions WHERE moderated=0''')
            allDB = cursor.fetchall()
            allDB.reverse()
            return render_template('moderatorloggedin.html', questions=allDB, moderatorname=session["name"])
        else:
            db = sqlite3.connect('questionsanswers.sql')
            cursor = db.cursor()
            cursor.execute('''SELECT * FROM questions WHERE moderated=1 AND answered=0''')
            allDB = cursor.fetchall()
            allDB.reverse()
            return render_template('indexloggedin.html', therapistname=session["name"], questions=allDB)
    #return render_template('index.html')



@app.route("/meettheteam")
def meettheteam():
    db = sqlite3.connect('static/therapists.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,monthly_price,email,website,qualifications FROM therapists''')
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    return render_template('therapist.html', therapist=allDB, pagetitle="Meet The Team")

@app.route("/search")
def search():
    db = sqlite3.connect('static/therapists.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,monthly_price,email,website,qualifications FROM therapists''')
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    return render_template('therapist.html', therapist=allDB, pagetitle="Search", issearchactive="thickfont")


@app.route("/faq")
def faq():
    return render_template('faq.html')

@app.route("/ask", methods = ['POST','GET'])
def ask():
    if request.method == 'POST':
        db = sqlite3.connect('questionsanswers.sql')
        cursor = db.cursor()
        result= request.form
        print(result["category"])
        if (any(word in result["question"] for word in swears) or any(word in result["name"] for word in swears)):
            return render_template('ask.html', isaskactive="thickfont",message='No curses please!', namevalue=result["name"], questionvalue=result["question"], isError=True)
        else:
            if (len(result["question"]) > 280):
                return render_template('ask.html', isaskactive="thickfont",message='Keep length lesser than 280 characters please!', namevalue=result["name"], questionvalue=result["question"],isError=True)
            elif (len(result["question"]) == 0 or len(result["name"]) == 0):
                return render_template('ask.html', isaskactive="thickfont",message='Empty questions/name', namevalue=result["name"],questionvalue=result["question"],isError=True)
            elif result["category"]== "Pick a category":
                return render_template('ask.html', isaskactive="thickfont",message='Please pick a category', namevalue=result["name"],questionvalue=result["question"],isError=True)
            elif (len(result["name"]) > 25):
                return render_template('ask.html', isaskactive="thickfont",message='Name lesser than 25 characters please', namevalue=result["name"], questionvalue=result["question"],isError=True)
            else:
                cursor.execute("INSERT INTO questions (name,date,question,'ip address',ID,moderated,answered,category) VALUES (?,?,?,?,?,?,?,?)",(result['name'],datetime.datetime.now().strftime('%b/%d/%Y'),result['question'],request.environ.get('HTTP_X_REAL_IP', request.remote_addr),str(uuid.uuid4()),0,0,result["category"]))
                db.commit()
                return render_template('ask.html', isaskactive="thickfont",message="ASKED",isError=False, isFine=True)
        db.close()
    else:
        return render_template('ask.html', isaskactive="thickfont")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("index"))

@app.route("/therapistlogin", methods = ['POST','GET'])
def therapistlogin():
    if request.method == 'POST':
        result= request.form
        # if username or password blank:
            # error
        if (len(result["username"]) == 0 or len(result["password"]) == 0):
            return render_template('therapistlogin.html', message="empty username/password", namevalue=result["username"])
        session.clear()
        db = sqlite3.connect('login.sql')
        cursor = db.cursor()
        checked = 'remember_me' in request.form
        cursor.execute("SELECT * FROM login WHERE codename = (?)", [result["username"]])
        rows = cursor.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0][2], result["password"]):
            return render_template('therapistlogin.html', message="incorrect username/password", namevalue=result["username"])
        session["user_id"] = rows[0][0]
        session["name"] = rows[0][1]
        if checked:
            session.permanent = True
        # give logged in message bootstrap
        return redirect(url_for("index"))
        # if username exists in database:
            # if hash of password is same as password hash in Database
                # if remember me is True
                    # set session, login, take to homepage, save session cookie
                # else:
                    # set session, login, take to homepage
            # else:
                # error, wrong password
        #else:
            # error, username doesn't exist
        db.close()
    else:
        return render_template('therapistlogin.html')

@app.route("/answered", methods = ['POST','GET'])
def answered():
    if request.method == 'POST':
        result= request.form
        print(result)
        # if specific Category and Search
            # specific search in Category
        if len(result["query"]) != 0 and result["category"] != "All categories":
            print("specific search, specific category. nice")
            db = sqlite3.connect('questionsanswers.sql')
            # TODO make category selected in html
            cursor = db.cursor()
            cursor.execute('''SELECT questions.name,questions.question, answers.answer,answers.name,answers.date,questions.date,questions.category FROM questions,answers WHERE (questions.ID = answers.'question ID' AND questions.answered = 1 AND questions.category = ?) AND (questions.name LIKE ? or questions.question LIKE ? or answers.answer LIKE ?)''', [result["category"], "%"+result["query"]+"%","%"+result["query"]+"%","%"+result["query"]+"%"])
            allDB = cursor.fetchall()
            allDB.reverse()
            return render_template('answered.html', isansweractive="thickfont", answered=allDB, whatresults='Showing results for "'+result["query"][:5]+'..." in category '+result["category"])



        # if specific category and no Search
            # cursor execute but add Category
        elif len(result["query"]) == 0 and result["category"] != "All categories":
            print("no search, specific category. nice")
            db = sqlite3.connect('questionsanswers.sql')
            # TODO make category selected in html
            cursor = db.cursor()
            cursor.execute('''SELECT questions.name,questions.question, answers.answer,answers.name,answers.date,questions.date,questions.category FROM questions,answers WHERE questions.ID = answers.'question ID' AND questions.answered = 1 AND questions.category = ?''', [result["category"]])
            allDB = cursor.fetchall()
            allDB.reverse()
            return render_template('answered.html', isansweractive="thickfont", answered=allDB, whatresults="Showing all results in category "+result["category"])
        # if all category and search
            # specific search in all category
        elif len(result["query"]) != 0 and result["category"] == "All categories":
            print("specific search, all category. nice")
            db = sqlite3.connect('questionsanswers.sql')
            cursor = db.cursor()
            cursor.execute('''SELECT questions.name,questions.question, answers.answer,answers.name,answers.date,questions.date,questions.category FROM questions,answers WHERE (questions.ID = answers.'question ID' AND questions.answered = 1) AND (questions.name LIKE ? or questions.question LIKE ? or answers.answer LIKE ?)''', [ "%"+result["query"]+"%","%"+result["query"]+"%","%"+result["query"]+"%"])
            allDB = cursor.fetchall()
            allDB.reverse()
            return render_template('answered.html', isansweractive="thickfont", answered=allDB, whatresults='Showing all results for "'+result["query"][:5]+'..."')
        # if no category, no search
            # redirect to get method
        else:
            print("no search no category. nice")
            db = sqlite3.connect('questionsanswers.sql')
            cursor = db.cursor()
            cursor.execute('''SELECT questions.name,questions.question, answers.answer,answers.name,answers.date,questions.date,questions.category FROM questions,answers WHERE questions.ID = answers.'question ID' AND questions.answered = 1''')
            allDB = cursor.fetchall()
            allDB.reverse()
            return render_template('answered.html', isansweractive="thickfont", answered=allDB, whatresults="Showing all results")

    else:
        db = sqlite3.connect('questionsanswers.sql')
        cursor = db.cursor()
        cursor.execute('''SELECT questions.name,questions.question, answers.answer,answers.name,answers.date,questions.date,questions.category FROM questions,answers WHERE questions.ID = answers.'question ID' AND questions.answered = 1''')
        allDB = cursor.fetchall()
        allDB.reverse()
        return render_template('answered.html', isansweractive="thickfont", answered=allDB, whatresults="Showing all results")

@app.route("/privacy")
def privacy():
    return render_template('privacy.html')

@app.route("/aboutus")
def aboutus():
    db = sqlite3.connect('static/partners.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,description,website FROM partners''')
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    db.close()
    return render_template('aboutus.html', partners=allDB)

    #return(HTML_TEMPLATE.substitute(place_name=some_place))

# add this for all errors to go to same generic page
#app.config['TRAP_HTTP_EXCEPTIONS']=True

# generic error page
#@app.errorhandler(Exception)
def page_not_found(e):
    return render_template('404.html'), 404

# use this for the DigitalOcean server
if __name__ == "__main__":
    app.run()
