import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow '*' for origins.
    CORS(app, resources={'/': {'origins': '*'}})
    
    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        """ Set Access Control """

        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization, true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')

        return response

    @app.route('/categories')
    def get_all_categories():
        """Get categories endpoint

        This endpoint returns all categories or 
        status code 500 if there is a server error
        """

        try:
            categories = Category.query.all()
            return jsonify({
                'success' : True,
                'categories' : [category.format() for category in categories]
            }), 200
        except Exception:
            abort(500)



    '''
    @TODO: 
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions')
    def get_questions():
        """Get paginated questions

        This endpoint gets a list of paginated questions based
        on the page query string parameter and returns a 404
        when the page is out of bound

        QUESTIONS_PER_PAGE is a global variable
        """

        # get query string page to determine pagination
        page = request.args.get('page', 1, int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        # get paginated questions and categories
        questions = Question.query.order_by(Question.id).all()
        questions = [question.format() for question in questions ]
        total_questions = len(questions)
        categories = Category.query.order_by(Category.id).all()
        current_questions = questions[start:end]

        # return 404 if there are no questions for the page number
        if (len(current_questions) == 0):
            abort(404)

        # return values if there are no errors
        return jsonify({
            'success': True,
            'total_questions': total_questions,
            'categories': [category.format() for category in categories],
            'questions': current_questions
        }), 200



    '''
    @TODO: 
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        """Delete specific question

        This endpoint deletes a specific question by the 
        id given as a url parameter
        """
        try:
            question = Question.query.get(id)
            question.delete()

            return jsonify({
                'success': True,
                'message': "Question successfully deleted"
            }), 200
        except Exception:
            abort(422)


    '''
    @TODO: 
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        """This endpoint creates a question.
        
        A 422 status code is returned if the any of
        the json data is empty.
        """
        # Get json data from request
        data = request.get_json()

        # get individual data from json data
        question = data.get('question','')
        answer = data.get('answer','')
        difficulty = data.get('difficulty','')
        category = data.get('category','')

        # validate to ensure no data is empty
        if ((question == '') or (answer == '')
                or (difficulty == '') or (category == '')):
            abort(422)

        try:
            # Create a new question instance
            question = Question(
                question=question, 
                answer=answer,
                difficulty=difficulty, 
                category=category)
        
            # save question
            question.insert()

            # return success message
            return jsonify({
                'success': True,
                'message': 'Question successfully created!'
            }), 201

        except Exception:
            # return 422 status code if error 
            abort(422)        

    '''
    @TODO:
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """This endpoint returns questions from a search term. """

        # Get search term from request data
        data = request.get_json()
        search_term = data.get('searchTerm', '')

        # Return 422 status code if empty search term is sent
        if search_term == '':
            abort(422)

        try:
            # get all questions that has the search term substring
            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            # if there are no questions for search term return 404
            if len(questions) == 0:
                abort(404)

            # return response if successful
            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(Question.query.all())
            }), 200

        except Exception:
            # This error code is returned when 404 abort
            # raises exception from try block
            abort(404)

    '''
    @TODO: 
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        """This endpoint handles getting questions by category"""

        # get the category by id
        category = Category.query.filter_by(id=id).one_or_none()

        # abort 400 for bad request if category isn't found
        if (category is None):
            abort(422)

        questions = Question.query.filter_by(category=id).all()
        questions = [question.format() for question in questions]

        # return the results
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(questions),
            'current_category': category.type
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    # Error handler for resource not found (404)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    # Error handler for internal server error (500)
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'An error has occured, please try again'
        }), 500

    # Error handler for unprocesable entity (422)
    @app.errorhandler(422)
    def unprocesable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    return app

    