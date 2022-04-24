from flask import Flask, redirect, render_template, session, g, flash, abort, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
from models import db, connect_db, User, Recipe, Favorite
from forms import NewUser, LoginForm, IngredientForm
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',"postgresql:///capstone1")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

CURR_USER_KEY = "curr_user"

connect_db(app)

db.create_all()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'oyessecret')

api_key = 'f3e802864b7e4b9390937e35e4f69b19'
# api_key = '8621e9a5acdd46cca3210dbd0d5d5cf7'

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# debug = DebugToolbarExtension(app)

app.logger.info('-=-=-=-=-=-=-=-=-= UNKO -=-=-=-=-=-=-=-==')

app.logger.info('-=-=-=-=-=-=-=-=-= UNKO -=-=-=-=-=-=-=-==')



@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    print(session)
    if CURR_USER_KEY in session and session[CURR_USER_KEY] is not None:
        print(session[CURR_USER_KEY])
        g.user = User.query.get(session[CURR_USER_KEY])


    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = NewUser()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.add(user)
            db.session.commit()

        except IntegrityError as e:
            if "DETAIL:  Key (email)=" in str(e):
                flash("Email already registered",'danger')
            else:
                print('unko')
                flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)
        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    if g.user:
        return redirect("/search")
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            return redirect("/search")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    return redirect("/login")


###############################################################
##General Routes

@app.route('/')
def homepage():
    """show forms is logged in, if not, signup"""
    if g.user:
        return redirect("/search")
    else:
        return redirect('/signup')

@app.route('/search', methods=["GET","POST"])
def input_ingredients():
    """Show form to input ingredients and also the search results"""
    # if not g.user:
    #     flash("Not Valid User")
    #     return redirect('/')
    ingredient_param = request.args.get("includeIngredient")
    form = IngredientForm()
    if form.validate_on_submit():
        ingredient_one = form.ingredient_one.data
        ingredient_two = form.ingredient_two.data
        ingredient_three = form.ingredient_three.data
        ingredient_four = form.ingredient_four.data
        ingredient_five = form.ingredient_five.data

        allp= [ingredient_one, ingredient_two, ingredient_three, ingredient_four, ingredient_five]
        p = list(filter(None,allp))
        ingredient_string = ","
        all_ingredients= ingredient_string.join(p)
        # return redirect("/search", params = p)
        return redirect(url_for('input_ingredients', includeIngredient=all_ingredients))

    else:
        if ingredient_param is None:
            return render_template("/search.html", form=form)

        # ingredients_included = request.args.get("includeIngredient");
        # ingredient_string = ","
        # all_ingredients= ingredient_string.join(ingredients_included)
        p = {"includeIngredients":ingredient_param, "apiKey" : api_key, 'addRecipeInformation': 'true', 'ignorePantry' : 'false', 'instructionsRequired': 'true'}
        print(ingredient_param)
        response = requests.get('https://api.spoonacular.com/recipes/complexSearch',
                                    params= p)
        recipes = response.json()['results']
        print(recipes)
        formatted_recipe_list = []

        for recipe in recipes:
            # res = requests.get(f"https://api.spoonacular.com/recipes/{recipe['id']}/ingredientWidget.json?apiKey={api_key}")
            # ingredients = res.json()['ingredients']
            # ingredient_list = []

            # for ingredient in ingredients:
            #     ingredient_list.append(ingredient['name'])

            """somehow loop over each ingredients to list them all"""
            # formatted_recipe = Recipe(
            #     title = recipe['title'],
            #     ingredients = ingredient_list,
            #     image_url = recipe['image'],
            #     recipe_url = recipe['sourceUrl'],
            #     recipe_id = recipe['id']
            # )

            formatted_recipe = {
                'title' : recipe['title'],
                'image_url' : recipe['image'],
                'recipe_id' :recipe['id']
            }
            print(formatted_recipe)
            formatted_recipe_list.append(formatted_recipe)
            # db.session.add(formatted_recipe)
            # db.session.commit()


        return render_template("search.html", form=form, formatted_recipe_list=formatted_recipe_list)


# @app.route('/search/all_recipes')
# def show_all_recipes():
#     """Show list of all recipes"""

#     if not g.user:
#         flash("Not Valid User")
#         return redirect('/')

#     recipes = Recipe.query.all()
#     return render_template("all_recipes.html", recipes=recipes)


@app.route('/search/<int:recipe_id>')
def show_recipe(recipe_id):
    """Show specific recipe when clicked"""
    # if not g.user:
    #     flash("Not Valid User")
    #     return redirect('/')



    recipe_res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}")
    recipe = recipe_res.json()

    ingredients_res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/ingredientWidget.json?apiKey={api_key}")
    print(ingredients_res.json())
    ingredients = ingredients_res.json()['ingredients']
    print(ingredients)

    instruction_res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={api_key}")
    instructions = instruction_res.json()[0]['steps']
    print(recipe)

    favorite = Favorite.query.get((recipe_id,g.user.id))
    print("------------------")
    print(favorite)

    return render_template("recipe.html", ingredients=ingredients, instructions=instructions, recipe=recipe,favorite=favorite)


@app.route('/search/<int:recipe_id>/favorite', methods =['POST'])
def add_favorite(recipe_id):

    if not g.user:
        flash("Not Valid User")
        return redirect('/')

    recipe_res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}")
    recipe = recipe_res.json()
    ingredients = recipe_res.json()['extendedIngredients']
    ingredient_list = []

    for ingredient in ingredients:
        ingredient_list.append(ingredient['name'])

    if Favorite.query.get((recipe_id,g.user.id)):
        return abort(403)



    favorited_recipe = Recipe(
        title = recipe['title'],
        ingredients = ingredient_list,
        image_url = recipe['image'],
        recipe_url = recipe['sourceUrl'],
        recipe_id = recipe['id']
    )

    user_favorite = Favorite(
        recipe_id = recipe['id'],
        user_id = g.user.id
        )

    # favorited_recipe = Recipe.query.get(recipe_id)

    # if favorited_recipe.user_id == g.user.id:
    #     return abort(403)

    # user_favorites = g.user.favorites

    # if favorited_recipe in user_favorites:
    #     g.user.favorites = [fav for fav in user_favorites if fav != favorited_recipe]
    # else:
    #     g.user.favorites.append(favorited_recipe)
    db.session.add(favorited_recipe)
    db.session.commit()
    db.session.add(user_favorite)
    db.session.commit()
    return redirect(f"/search/{recipe_id}")

@app.route("/search/<int:recipe_id>/favorite/delete", methods=['POST'])
def delete_favorite(recipe_id):
    recipe = Recipe.query.filter(Recipe.recipe_id==recipe_id).delete()
    favorited_recipe = Favorite.query.get((recipe_id,g.user.id))
    db.session.delete(favorited_recipe)
    db.session.commit()

    return redirect(f"/search/{recipe_id}")


@app.route("/user/favorite")
def show_favorites():
    if not g.user:
        flash("Access unauthorized")
        return redirect("/")
    favorited_recipes = Favorite.query.filter(Favorite.user_id==g.user.id)
    print("---------------")
    recipes = Recipe.query.all()
    # recipes= Recipe.query.filter(favorited_recipe.user_id==g.user.id)
    return render_template("favorites.html",recipes=recipes,favorited_recipes=favorited_recipes)
    # else:
    #     return redirect(f"/search/{recipe_id}")
