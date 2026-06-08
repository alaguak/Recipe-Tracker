from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__, template_folder='templates')

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'recipes.json')


def load_recipes():
    """Load recipes from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def save_recipes(recipes):
    """Save recipes to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)


@app.route('/')
def index():
    """Redirect to add recipe page"""
    return redirect(url_for('add_recipe'))


@app.route('/addrecipe', methods=['GET'])
def add_recipe():
    """Display the recipe form"""
    return render_template('addrecipe.html')


@app.route('/save', methods=['POST'])
def save_recipe():
    """Handle recipe form submission"""
    recipe_name = request.form.get('rname', '').strip()
    ingredients = request.form.getlist('iname')
    steps = request.form.get('steps', '').strip()

    # Validate recipe name
    if not recipe_name:
        return "Recipe name is required!", 400

    # Filter out empty ingredients
    clean_ingredients = [ing.strip() for ing in ingredients if ing and ing.strip()]

    # Create recipe object
    recipe = {
        'id': len(load_recipes()) + 1,
        'name': recipe_name,
        'ingredients': clean_ingredients,
        'steps': steps
    }

    # Load existing recipes and add new one
    recipes = load_recipes()
    recipes.append(recipe)
    save_recipe(recipes)

    return redirect(url_for('add_recipe'))


@app.route('/recipes', methods=['GET'])
def get_recipes():
    """API endpoint to retrieve all recipes as JSON"""
    return jsonify(load_recipes())


@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """API endpoint to retrieve a specific recipe"""
    recipes = load_recipes()
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    if recipe:
        return jsonify(recipe)
    return jsonify({'error': 'Recipe not found'}), 404


@app.route('/delete/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    """Delete a recipe by ID"""
    recipes = load_recipes()
    recipes = [r for r in recipes if r['id'] != recipe_id]
    save_recipes(recipes)
    return redirect(url_for('add_recipe'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
