from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, InputRequired, Optional



class NewUser(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('E-mail', validators=[InputRequired(), Email()])



class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class IngredientForm(FlaskForm):
    """Enter ingredients available"""

    ingredient_one = StringField('First Ingredient', validators=[InputRequired()])
    ingredient_two = StringField('Second Ingredient')
    ingredient_three = StringField('Third Ingredient')
    ingredient_four = StringField('Fourth Ingredient')
    ingredient_five = StringField('Fifth Ingredient')
