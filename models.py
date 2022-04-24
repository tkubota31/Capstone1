from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import PrimaryKeyConstraint

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.Text, nullable=False, unique=True)

    recipe = db.relationship('Favorite', backref = 'user')

    favorites = db.relationship("Recipe", secondary = "favorite")

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Recipe(db.Model):
    __tablename__ = "recipe"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.Text)

    ingredients = db.Column(db.Text)

    image_url = db.Column(db.Text)

    recipe_url = db.Column(db.Text)

    recipe_id = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False,)
    # user = db.relationship('User')

    fav_recipes = db.relationship('Favorite', backref = 'recipes')

class Favorite(db.Model):
    __tablename__ = "favorite"

    # id = db.Column(db.Integer, primary_key = True)

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'),primary_key = True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key = True)

    # PrimaryKeyConstraint('recipe_id', 'user_id', name = "combo_id")


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
