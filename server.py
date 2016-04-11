"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()

    return render_template("user_list.html", users=users)


@app.route("/users/<int:user_id>")
def show_user_details(user_id):
    """Show user details."""

    user = User.query.get(user_id)

    return render_template("user_details.html",
                            user=user)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<int:movie_id>")
def show_movie_details(movie_id):
    """Show movie details."""

    movie = Movie.query.get(movie_id)

    return render_template("movie_details.html",
                            movie=movie)


@app.route("/movies/<int:movie_id>/show-rating-form")
def show_rating_form(movie_id):
    """Show rating form to add or update movie rating."""

    # If user is logged in, render rating_form.html.
    # Otherwise, redirect to login page.
    
    movie = Movie.query.get(movie_id)    

    if session:
        return render_template("rating_form.html",
                                movie=movie)
    else:
        flash("Please login to add or update a movie rating.")
        return redirect("/login")


@app.route("/movies/<int:movie_id>/new-update-rating", methods=["POST"])
def process_rating(movie_id):
    """Update or add new user rating."""

    user_id = session.get("user_id")
    score = request.form.get("rating")

    rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id)
    
    if rating:
        # Update rating        
        rating.score = score
        # print "SCORE", score
        # print "RATING.SCORE", rating.score
        ################################################################
        # Flash message works. score & rating.score is correct
        # But score is not updating on movie details page.
        flash("Thank you. Your rating has been updated for this movie.")
        return redirect("/movies")
    else:
        # Add rating
        rating = Rating(user_id=user_id, 
                        movie_id=movie_id,
                        score=score)
        
        db.session.add(rating)
        db.session.commit()

        flash("Thank you. Your rating has been added.")
        return redirect("/movies")


@app.route("/login")
def show_login_form():
    """Show login form."""

    return render_template("login.html")


@app.route("/process-login", methods=["POST"])
def process_user_login():
    """Log in existing users, otherwise redirect to sign up page."""

    email = request.form.get("email")
    password = request.form.get("password")
    
    # Grab the user object that matches the email and password values.
    user = User.query.filter_by(email=email, password=password).first()

    # If the user object exists, then add the user_id to the session (logged in).
    # Otherwise, redirect to sign up form to create a new user account.
    if user:
        user_id = user.user_id
        session["user_id"] = user_id
        flash("Logged In")
        user_details = "/users/%d" % (user_id)
        return redirect(user_details)
    else:
        flash("Sorry, you're not a registered user. Please sign up.")
        return redirect("/sign-up-form")

        
@app.route("/sign-up-form")
def show_sign_up_form():
    """Show sign up form for new users."""

    return render_template("sign_up_form.html")

    
@app.route("/sign-up", methods=["POST"])
def sign_up_new_user():
    """Add a new user to the database and session."""

    email = request.form.get("email")
    password = request.form.get("password")
    age = int(request.form.get("age"))
    zipcode = request.form.get("zipcode")
    
    # Creating new user in our database based on email, password, age, and zipcode. 
    new_user = User(email=email, password=password, age=age, zipcode=zipcode)
    db.session.add(new_user)
    db.session.commit()

    new_user_id = new_user.user_id
    # Add the new user to the session. 
    session["user_id"] = new_user_id
    flash("Thank you. Your account has been created.")  

    new_user_details = "/users/%d" % (new_user_id)
    return redirect(new_user_details)


@app.route("/logout")
def log_out_user():
    """Logging out user and redirecting to homepage."""

    del session["user_id"]
    flash("Logged out")
    return redirect("/")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
