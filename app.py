import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DMNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)
users = mongo.db.users

''' this route loads the homepage along with the reviews'''


@app.route("/")
@app.route("/home")
def home():
    reviews = mongo.db.reviews.find()
    return render_template("home.html", reviews=reviews)


"""gets the data from the database.
So once the image is clicked, the relevant review appears"""


@app.route("/movie_details/<review_id>", methods=["GET", "POST"])
def movie_details(review_id):
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    return render_template("movies.html", review=review)


'''This route is linked to the form, allows users to add a new review'''


@app.route("/new_reviews", methods=["GET", "POST"])
def new_reviews():
    if request.method == "POST":
        movie_reviews = {
            "movie_title": request.form.get("movie_title"),
            "year_released": request.form.get("year_released"),
            "director": request.form.get("director"),
            "age_rating": request.form.get("age_rating"),
            "run_time": request.form.get("run_time"),
            "genre": request.form.get("genre"),
            "description": request.form.get("description"),
            "user_rating": request.form.get("user_rating"),
            "image": request.form.get("image"),
            "author": session["user"]
        }

        mongo.db.reviews.insert_one(movie_reviews)
        flash("Review Added!")
        return redirect(url_for("home"))
    return render_template("new_review.html")


'''This route is linked to the form, allows users to edit an existing review'''


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    if request.method == "POST":
        submit = {
            "movie_title": request.form.get("movie_title"),
            "year_released": request.form.get("year_released"),
            "director": request.form.get("director"),
            "age_rating": request.form.get("age_rating"),
            "run_time": request.form.get("run_time"),
            "genre": request.form.get("genre"),
            "description": request.form.get("description"),
            "user_rating": request.form.get("user_rating"),
            "image": request.form.get("image")
        }

        mongo.db.reviews.update({"_id": ObjectId(review_id)}, submit)
        flash("Review Updated!")

    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    return render_template("edit_review.html", review=review)


"""This route is linked to the form.
Allows users to delete a review they have created"""


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    flash("Review Deleted!")
    return redirect(url_for("home"))


'''This route is linked to the search bar, users can search for a movie'''


@app.route("/search_movie", methods=["GET", "POST"])
def search_movie():
    data = request.form.get("data")
    reviews = mongo.db.reviews.find({"$text": {"$search": data}})
    return render_template("home.html", reviews=reviews)


'''This following 3 routes are for user authentication'''


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("signup"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful - Welcome!")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
            else:

                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:

            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
