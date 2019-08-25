import random
import os
import json
from flask import (
    flash, g, redirect, render_template, request, url_for, Flask, send_from_directory
)
app = Flask(__name__)

# Import random to shuffle distro list
import random
# Use SQLite3 for the Distro Database
import sqlite3
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/ladakh")
def ladakh():
    db = sqlite3.connect('static/trips.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,price,location,duration,display_price FROM trips WHERE collection = "Ladakh"''')
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    return render_template('collections.html', trips=allDB, collectioname="Ladakh", isladakhactive="thickfont")

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
    return render_template('collections.html', trips=allDB, collectioname="Others", isothersactive="thickfont")

@app.route("/bali")
def bali():
    db = sqlite3.connect('static/trips.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,price,location,duration,display_price FROM trips WHERE collection = "Bali"''')
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    return render_template('collections.html', trips=allDB, collectioname="Bali", isbaliactive="thickfont")

@app.route("/contactus")
def contactus():
    return render_template('contactus.html')

@app.route("/contiki")
def contiki():
    return render_template('contiki.html', iscontikiactive="thickfont")

@app.route("/weekendtrips")
def weekendtrips():
    db = sqlite3.connect('static/trips.sql')
    cursor = db.cursor()
    cursor.execute('''SELECT name,codename,price,location,duration,display_price FROM trips WHERE collection = "Weekend Getaways"''')
    allDB = cursor.fetchall()
    random.shuffle(allDB)
    return render_template('collections.html', trips=allDB, collectioname="Weekend Getaways", isweekendgetawayactive="thickfont")

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
