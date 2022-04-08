from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, validators
import requests


# INITIALIZE SERVER
app = Flask(__name__)

# INITIALIZE BOOTSTRAP
app.config['SECRET_KEY'] = 'secret key'
Bootstrap(app)

# INITIALIZE DATABASE
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# CREATE DATABASE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(100), nullable=True)
    img_url = db.Column(db.String(100), nullable=False)
# db.create_all()


# UPDATE FORM
class RateMovieForm(FlaskForm):
    updated_rating = FloatField("Your rating out of 10", [validators.DataRequired()])
    updated_review = StringField("Your Review", [validators.DataRequired(), validators.length(max=50)])
    submit = SubmitField("Update")


# ADD MOVIE FORM
class AddMovie(FlaskForm):
    movie_title = StringField("Movie Title", [validators.DataRequired()])
    submit = SubmitField("Add Movie", [validators.DataRequired()])


# HOME PAGE
@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    return render_template("index.html", movies=all_movies)


# ADD MOVIES PAGE
@app.route('/add', methods=["GET", "POST"])
def add():
    form = AddMovie()
    if form.validate_on_submit():
        response = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key=HEHEHEHE&query={form.movie_title.data}")
        movie_results = response.json()["results"]
        return render_template('select.html', movie_results=movie_results)
    return render_template("add.html", form=form)


# EDIT EXISTING MOVE PAGE
@app.route("/edit/<int:index>", methods=["POST", "GET"])
def edit(index):
    edit_form = RateMovieForm()
    movie_to_update = Movie.query.get(index)
    if edit_form.validate_on_submit():
        movie_to_update.rating = edit_form.updated_rating.data
        movie_to_update.review = edit_form.updated_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", edit_form=edit_form, movie=movie_to_update)


# DELETE MOVIE
@app.route("/delete/<int:index>")
def delete(index):
    movie_to_delete = Movie.query.get(index)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


# UPDATE DATABASE TO INCLUDE SELECTED MOVIE
@app.route("/update/<int:movie_id>")
def update(movie_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=HEHEHEHEHEHEHEH&language=en-US")
    movie = Movie(
        title=response.json()["original_title"],
        description=response.json()["overview"],
        year=response.json()["release_date"].split("-")[0],
        rating=0,
        ranking=0,
        review="None",
        img_url=f'https://image.tmdb.org/t/p/w500{response.json()["poster_path"]}'
    )
    db.session.add(movie)
    db.session.commit()
    return redirect(url_for("edit", index=movie.id))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
