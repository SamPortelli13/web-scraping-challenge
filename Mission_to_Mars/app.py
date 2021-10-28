from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars


app = Flask(__name__)


mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")


@app.route('/')
def home():
    # Find data
    mars_data = mongo.db.collection.find_one()
    print(mars_data)
    return render_template('index.html', mars_db=mars_data)


@app.route('/scrape')
def scrape():
    #mars = mongo.db.mars
    mars_data = scrape_mars.scrape()
    #mars.update(
    #    {},
    #    data,
    #    upsert=True
    #)
    mongo.db.collection.update({}, mars_data, upsert = True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
