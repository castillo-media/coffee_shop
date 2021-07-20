import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
    @TODO uncomment the following line to initialize the datbase
    !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN ONLY
    !! (AFTER THAT COMMENT AGAIN)
    !! Running this funciton will add one
    '''
    # db_drop_and_create_all()

    # ROUTES

    @app.route('/')
    def helloWorld():
        return jsonify("hello world")

    '''
    @TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
            returns status code 200 and
            json {"success": True, "drinks": drinks}
            where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''

    @app.route('/drinks')
    def getDrinks():
        error = False
        try:
            all_drinks = Drink.query.all()
            all_drinks_list = []
            for drink in all_drinks:
                drink_details = {
                    "id": drink.id,
                    "title": drink.title,
                    "recipe": [{'color': r['color'], 'parts': r['parts']}
                               for r in json.loads(drink.recipe)]
                }
                all_drinks_list.append(drink_details)
        except:
            error = True
        finally:
            if not error:
                return jsonify({
                    'success': True,
                    'drinks': all_drinks_list
                })

            elif error:
                abort(422)

    '''
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
            returns status code 200 & json {"success": True, "drinks": drinks}
            where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''

    @app.route('/drinks-detail')
    def getDrinksDetails():
        try:
            drinks = Drink.query.order_by(Drink.id).all()
            result = [drink.long() for drink in drinks]
            if len(result) == 0:
                abort(404)  # Not found - when there are no drink
            return jsonify({'success': True, 'drinks': result})
        except AuthError:
            abort(422)

    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''

    @app.route('/drinks', methods=['POST'])
    def postDrinkDetails():
        body = request.get_json()
        new_title = body['title']
        new_recipe = body['recipe']
        error = False

        try:
            drink = Drink(
                title=str(new_title),
                recipe=json.dumps(new_recipe)
            )

            drink.insert()
        except:
            error = True
        finally:
            if not error:
                return jsonify({
                    "success": True,
                    "drinks": [body]
                })
            elif error:
                abort(422)

    '''
    @TODO implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks/<int:drink_id>', methods=['PATCH'])
    def editDrink(drink_id):
        body = request.get_json()
        new_title = body['title']
        new_recipe = body['recipe']
        error = False
        try:
            drinkToEdit = Drink.query.filter(Drink.id == drink_id)\
                          .one_or_none()
        except:
            error = True
        finally:
            if not error:
                drinkToEdit.title = new_title
                drinkToEdit.recipe = json.dumps(new_recipe)
                drinkToEdit.update()

                return jsonify({
                    'success': True,
                    'drinks': [{
                        "id": drinkToEdit.id,
                        "title": drinkToEdit.title,
                        "recipe": drinkToEdit.recipe}]
                })

            elif error:
                abort(422)

    '''
    @TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''

    @app.route('/drinks/<int:drink_id>', methods=['DELETE'])
    def deleteDrink(drink_id):
        error = False
        try:
            drink_to_delete = Drink.query.filter(Drink.id == drink_id)\
                              .one_or_none()
        except:
            error = True
        finally:
            if not error:
                drink_to_delete.delete()
                return jsonify({
                    'success': True,
                    'delete': drink_id
                })

            elif error:
                abort(404)

    # Error Handling
    '''
    Example error handling for unprocessable entity
    '''

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    '''
    @TODO implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                jsonify({
                        "success": False,
                        "error": 404,
                        "message": "resource not found"
                        }), 404

    '''

    '''
    @TODO implement error handler for 404
        error handler should conform to general task above
    '''

    @app.errorhandler(404)
    def resourceNotFound(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    '''
    @TODO implement error handler for AuthError
        error handler should conform to general task above
    '''
    return app
