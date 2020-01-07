from flask import Flask, render_template, url_for, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from geometricMedian import geometric_median
import os, uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

"""
A visualizer of the Geometric Median algorithm
"""

# the database table
class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(2000), nullable=False) #a unique identifier so your 'people' dont spread to other users
    name = db.Column(db.String(200), nullable=True)
    #color = db.Column()
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<People %r>' % self.id


#initial index page
@app.route("/", methods=["POST", "GET"])
def index():
    API_KEY = os.environ.get('API_KEY') #gets the google maps api key from the environment variable
    userId = request.cookies.get("userId") #unique user cookies key
    if request.method == "POST":
        people_name = request.form['name']
        people_latitude = request.form['latitude']
        people_longitude = request.form['longitude']
        new_task = People(user_id=userId, name=people_name, latitude=people_latitude, longitude=people_longitude)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/#map")
        except:
            return "An error occured adding the person"
    else:
        if userId is None:
            people = People.query.order_by(People.date_created).all()
            geomMedian = [46.227638, 2.213749] #random starting point if no people are populated
            resp = make_response(render_template("index.html", people=people, geomMedian=geomMedian, key=API_KEY))
            i = str(uuid.uuid1())
            resp.set_cookie('userId', i) #set a unique user cooker
            return resp 
        else:
            inputs = []
            people = People.query.filter_by(user_id=userId).order_by(People.date_created).all() #database call
            if len(people) >= 1:
                for p in people:
                    inputs.append([p.latitude, p.longitude])
                geomMedian = geometric_median(inputs, method="weiszfeld") #calling geometric median function
            else:
                geomMedian = [46.227638, 2.213749] #random starting point if no people are populated
            return render_template("index.html", people=people, geomMedian=geomMedian, key=API_KEY)
    
#delete 'people'
@app.route("/delete/<int:id>")
def delete(id):
    deletePerson = People.query.get_or_404(id)
    try:
        db.session.delete(deletePerson)
        db.session.commit()
        return redirect("/")
    except:
        return "Error deleting Person"

#update 'people'
@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    person =  People.query.get_or_404(id)
    if request.method == "POST":
        person.name = request.form["name"]
        person.latitude = request.form["latitude"]
        person.longitude = request.form["longitude"]
        try:
            db.session.commit()
            return redirect("/")
        except:
            return "There was an error updating this person"
    else:
        return render_template("update.html", person=person)

if __name__ == "__main__":
    app.run(debug=True)