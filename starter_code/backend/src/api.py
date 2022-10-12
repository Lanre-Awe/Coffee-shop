# from crypt import methods
import os
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def getAllDrinks():
    get_drinks = Drink.query.all()

    drinks = [drink.short() for drink in get_drinks]

    return jsonify({
        'success': True,
        'drinks': drinks

    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    get_long_drink = Drink.query.all()

    drinks = [drink.long() for drink in get_long_drink]

    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    body = request.get_json()

    try:
        title = body['title']
        recipe = body['recipe']

        new_drink = Drink(title=title, recipe=recipe)

        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        })

    except Exception:
        abort(422)

    

@app.route('/drinks/<int:id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(id, payload):
    body = request.get_json()

    try:
        get_drink = Drink.query.filter(Drink.id == id).one_or_none()

        if get_drink is None:
            abort(404)

        get_drink.title = body['title']
        get_drink.recipe = body['recipe']

        get_drink.update()


        return jsonify({
            'success': True,
            'drinks': [get_drink.long()]
        })

    except Exception:
        abort(422)

        

@app.route('/drinks/<int:id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id, payload):
    get_drink = Drink.query.filter(Drink.id == id).one_or_none()

    try:

        if get_drink is None:
            abort(404)

        get_drink.delete()

        return jsonify({
            'success': True,
            'delete': get_drink.id
        })

    except Exception:
        abort(422)

    

# Error Handling



@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(auth_error):
    return jsonify({
        'success': False,
        'error': auth_error.status_code,
        'message': auth_error.error
    }), 401

if __name__ == "__main__":
    app.debug = True
    app.run()
