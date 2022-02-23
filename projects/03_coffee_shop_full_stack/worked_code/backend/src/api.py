import os, sys
import logging
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from  sqlalchemy.sql.expression import func

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
def drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()

        drinks_short = [drink.short() for drink in drinks]

        return jsonify({
                'drinks': drinks_short,
                'total_drinks': len(drinks_short),
                'success': True,
        })
    except HTTPException:
        raise
    except:
        abort(422, sys.exc_info())


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    try:
        drinks = Drink.query.order_by(Drink.id).all()

        drinks_detailed = [drink.long() for drink in drinks]

        return jsonify({
                'drinks': drinks_detailed,
                'total_drinks': len(drinks_detailed),
                'success': True,
        })
    except HTTPException:
        raise
    except:
        abort(422, sys.exc_info())


def check_post_data(new_title, new_recipe):
    """
    Returns the error description if post (or patch) parameters are invalid,
    or an empty string if they are valid
    """
    desc = ''
    if not (len(new_title) and len(new_recipe)):
        desc = '' if len(new_title) else 'title '
        is_plural = False
        if not len(new_recipe):
            if len(desc):
                is_plural = True
                desc += 'and recipe '
            else:
                desc += 'recipe '
        desc += 'fields are ' if is_plural else 'field is '
        desc += 'empty or missing'
        assert(len(desc)) #sanity
    return desc

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(jwt):
    try:
        body = request.get_json()

        new_title = body.get('title', '')
        new_recipe = body.get('recipe', '')
        error_desc = check_post_data(new_title, new_recipe)
        if len(error_desc):
            abort(400, error_desc)
 
        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()

        selection = Drink.query.with_entities(func.count(Drink.id)).all()
        total_drinks = selection[0][0]

        return jsonify({
            'success': True,
            'drinks': [ new_drink.long() ],
        })
    except HTTPException:
        raise
    except:
        abort(422, sys.exc_info())


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, drink_id):
    try:
        drink_to_patch = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink_to_patch is None:
            abort(404, f'drink id={drink_id} not found')

        body = request.get_json()

        new_title = body.get('title', '')
        new_recipe = body.get('recipe', '')
        error_desc = check_post_data(new_title, new_recipe)
        if len(error_desc):
            abort(400, error_desc)

        drink_to_patch.title = new_title
        drink_to_patch.recipe = json.dumps(new_recipe)
        drink_to_patch.update()

        return jsonify({
            'success': True,
            'drinks': drink_to_patch.long()
        })
    except HTTPException:
        raise
    except:
        abort(422, sys.exc_info())


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, drink_id):
    try:
        drink_to_delete = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink_to_delete is None:
            abort(404, f'drink id={drink_id} not found')

        drink_to_delete.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except HTTPException:
        raise
    except:
        abort(422, sys.exc_info())


if __name__ == "__main__":
    app.debug = True
    app.run()


# DEFAULT ERROR HANDLERS
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(400)
def bad_request(error):
    default_msg = "server received a bad request"
    message = '{}: {}'.format(default_msg, error.description)
    app.logger.error('{}{}'.format(error, ((':{}'.format(message)) if (not len(error.description)) else '')))
    return (
        jsonify({
        'success': False,
        'error': 400,
        'message': message
        }),
        400,
    )


@app.errorhandler(404)
def not_found(error):
    default_msg = "resource not found in the server's database"
    message = error.description if len(error.description) else default_msg
    app.logger.error('{}{}'.format(error, ((':{}'.format(message)) if (not len(error.description)) else '')))
    return (
        jsonify({
        'success': False,
        'error': 404,
        'message': message
        }),
        404,
    )


@app.errorhandler(422)
def unprocessable_entity(error):
    default_msg = "your request is correctly formated but the server is unable to process it"
    message = error.description if len(error.description) else default_msg
    app.logger.error('{}{}'.format(error, ((':{}'.format(message)) if (not len(error.description)) else '')))
    return (
        jsonify({
        'success': False,
        'error': 422,
        'message': f"unprocessable entity - {message}"
        }),
        422,
    )


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    app.logger.error(e)
    # replace the body with JSON
    return (
        jsonify({
            'success': False,
            'error': e.code,
            'message': f'{e.name}: {e.description}'
        }),
        e.code,
    )

