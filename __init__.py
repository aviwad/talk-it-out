import random
import os
import json
import datetime
import uuid
from flask import (
    flash, g, redirect, render_template, request, url_for, Flask, send_from_directory
)
app = Flask(__name__)

# Import random to shuffle distro list
import random
# Use SQLite3 for the Distro Database
import sqlite3
app = Flask(__name__)

swear_text = open("static/swear")
swears = swear_text.read().strip().split()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/therapists")
def therapists():
    db = sqlite3.connect('static/therapists.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,monthly_price,email,website FROM therapists''')
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    return render_template('therapist.html', therapist=allDB, pagetitle="Meet The Therapists", ismeetthetherapistsactive="thickfont")

@app.route("/cancellation")
def cancellation():
    return render_template('cancellation.html')

@app.route("/others")
def others():
    db = sqlite3.connect('static/trips.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,price,location,duration,display_price FROM trips WHERE collection = "Others"''')
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    return render_template('page.html', trips=allDB, pagetitle="Others", isothersactive="thickfont")

@app.route("/bali")
def bali():
    db = sqlite3.connect('static/trips.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,price,location,duration,display_price FROM trips WHERE collection = "Bali"''')
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    return render_template('page.html', trips=allDB, pagetitle="Bali", isbaliactive="thickfont")

@app.route("/contactus")
def contactus():
    return render_template('contactus.html')

@app.route("/ask", methods = ['POST','GET'])
def ask():
    if request.method == 'POST':
        db = sqlite3.connect('questionsanswers.sql')
        cursor = db.cursor()
        result= request.form
        if (any(word in result["question"] for word in swears) or any(word in result["name"] for word in swears)):
            return render_template('ask.html', isaskactive="thickfont",message="NO CUSSES", namevalue=result["name"], questionvalue=result["question"])
        else:
            if (len(result["question"]) > 280):
                return render_template('ask.html', isaskactive="thickfont",message="KEEP LENGTH LESS THAN 280 characters", namevalue=result["name"], questionvalue=result["question"])
            elif (len(result["question"]) == 0 or len(result["name"]) == 0):
                return render_template('ask.html', isaskactive="thickfont",message="empty question/name", namevalue=result["name"])
            elif (len(result["name"]) > 25):
                return render_template('ask.html', isaskactive="thickfont",message="KEEP NAME LENGTH LESS THAN 25 characters", namevalue=result["name"], questionvalue=result["question"])
            else:
                cursor.execute("INSERT INTO questions (name,date,question,'ip address',ID,moderated,answered) VALUES (?,?,?,?,?,?,?)",(result['name'],datetime.datetime.now().strftime('%b/%d/%Y'),result['question'],request.environ.get('HTTP_X_REAL_IP', request.remote_addr),str(uuid.uuid4()),0,0))
                db.commit()
                return render_template('ask.html', isaskactive="thickfont",message="ASKED")
        db.close()
    else:
        return render_template('ask.html', isaskactive="thickfont")

@app.route("/answered")
def answered():
    return render_template('ask.html', isansweractive="thickfont")

@app.route("/asked")
def asked():
    return render_template('asked.html', isaskedactive="thickfont")

@app.route("/weekendtrips")
def weekendtrips():
    db = sqlite3.connect('static/trips.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,price,location,duration,display_price FROM trips WHERE collection = "Weekend Getaways"''')
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    return render_template('page.html', trips=allDB, pagetitle="Weekend Getaways", isweekendgetawayactive="thickfont")

@app.route("/privacy")
def privacy():
    return render_template('privacy.html')

@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html')

@app.route('/trips/<some_place>')
def some_place_page(some_place):
    db = sqlite3.connect('static/trips.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,price,location,duration,display_price,overview1,overview2 FROM trips WHERE codename=(?)''',[some_place])
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    return render_template('trips.html', some_place=some_place, trip=allDB[0])
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
