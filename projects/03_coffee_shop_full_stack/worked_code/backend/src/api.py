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
                'drinks_short': drinks_short,
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
    print(f'jwt = "{jwt}"')

    drinks = Drink.query.order_by(Drink.id).all()

    drinks_detailed = [drink.long() for drink in drinks]

    return jsonify({
            'drinks_long': drinks_detailed,
            'total_drinks': len(drinks_detailed),
            'success': True,
      })


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
 
        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()

        selection = Drink.query.with_entities(func.count(Drink.id)).all()
        total_drinks = selection[0][0]

        return jsonify({
            'success': True,
            'created_id': new_drink.id,
            'total_drinks': total_drinks,
            #TODOAQ:
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


if __name__ == "__main__":
    app.debug = True
    app.run()


# DEFAULT ERROR HANDLERS
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


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

