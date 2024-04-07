from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recipes.db"
db = SQLAlchemy(app)

recipe_ingredient_association = db.Table(
    "recipe_ingredient",
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipe.id")),
    db.Column("ingredient_id", db.Integer, db.ForeignKey("ingredient.id"))
)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.relationship("Ingredient",
                                  secondary=recipe_ingredient_association,
                                  backref="recipes")


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add_recipe", methods=["POST"])
def add_recipe():
    name = request.form["name"]
    ingredients = request.form.getlist("ingredients")
    new_recipe = Recipe(name=name)
    for ingredient_name in ingredients:
        ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
        if not ingredient:
            ingredient = Ingredient(name=ingredient_name)
            db.session.add(ingredient)
        new_recipe.ingredients.append(ingredient)
    db.session.add(new_recipe)
    db.session.commit()
    return f"Recipe {new_recipe.name} created successfully"


@app.route("/add_ingredient", methods=["POST"])
def add_ingredient():
    name = request.form["name"]
    new_ingredient = Ingredient(name=name)
    db.session.add(new_ingredient)
    db.session.commit()
    return f"Ingredient {new_ingredient.name} added"


@app.route("/pair_recipe_ingredient", methods=["POST"])
def pair_recipe_ingredient():
    recipe_id = request.form["recipe_id"]
    ingredient_id = request.form["ingredient_id"]
    recipe = Recipe.query.get(recipe_id)
    ingredient = Ingredient.query.get(ingredient_id)
    recipe.ingredients.append(ingredient)
    db.session.commit()
    return f"Ingredient {ingredient.name} added to {recipe.name}"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
