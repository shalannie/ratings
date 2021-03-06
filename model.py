"""Models and database functions for Ratings project."""

from correlation import pearson
from flask_sqlalchemy import SQLAlchemy


# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

# Behavior of the Eye:
# When a user views a movie they haven’t rated, the Eye predicts how that user will rate that movie.
# Once a user has either rated the movie or received a prediction, the Eye will find its own rating score for that movie, predicting the number if it has to.
# The Eye will take the difference of the two ratings, and criticize the user for their tastes.


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(150), nullable=True)
    password = db.Column(db.String(150), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%d email=%s>" % (self.user_id, self.email)

    def similarity(self, other):
        """Return the pearson rating for a user compared to another user"""

        user_ratings = {}
        paired_ratings = []

        for rating in self.ratings:
            user_ratings[rating.movie_id] = rating

        for r in other.ratings:
            u_r = user_ratings.get(r.movie_id)

            if u_r is not None:
                paired_ratings.append((u_r.score, r.score))

        if paired_ratings:
            return pearson(paired_ratings)
        else:
            return 0.0




# Put your Movie and Rating model classes here.

class Movie(db.Model):
    """Movie of ratings website."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(400))
    released_at = db.Column(db.DateTime)
    imdb_url = db.Column(db.String(400))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Movie movie_id=%d title=%s>" % (self.movie_id, self.title)


class Rating(db.Model):
    """Rating of a movie by a user."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    score = db.Column(db.Integer)
   
    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("ratings", order_by=rating_id))

    # Define relationship to movie
    movie = db.relationship("Movie",
                            backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Rating rating_id=%d movie_id=%d user_id=%d score=%d>" % (
            self.rating_id, self.movie_id, self.user_id, self.score)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
