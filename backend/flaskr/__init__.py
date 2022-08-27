from crypt import methods
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,selection):
    page = request.args.get('page',1,type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_selection = [question.format() for question in selection]
    current_selection = formatted_selection[start:end]

    return current_selection

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins" : "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers","Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods","GET,PUT,POST,DELETE,OPTIONS")
        return response
    

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.all()
            formatted_categories = {category.id:category.type for category in categories}
            total_categories = len(formatted_categories)
            
            if total_categories == 0:
                abort(404)
                
            return jsonify({
                'success':True,
                'categories': formatted_categories,
                'total_categories':total_categories
                })
        except:
            abort(500)

    

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        try:
            questions = Question.query.all()
            categories = Category.query.all()
            total_questions = len(questions)

            current_questions = paginate_questions(request, questions)
            
            formatted_categories = {category.id:category.type for category in categories}
            category_length = len(formatted_categories)

            random_category_id = random.randint(1,category_length)
            category = Category.query.get(random_category_id)
            current_category = category.type

            if len(current_questions) == 0:
                abort(404)

            return jsonify({
                'success':True,
                'questions':current_questions,
                'categories':formatted_categories,
                'current_category':current_category,
                'total_questions': total_questions,
            })

        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            questions = Question.query.all()
            question = Question.query.filter(Question.id == question_id).one_or_none()
            total_questions = len(questions)

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id,
                'total_questions': total_questions
            })

        except:
            db.session.rollback()
            abort(422)
        
        finally:
            db.session.close()
        
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def create_qustions():
        try:
            body = request.get_json()
            question = body.get("question", None)
            answer = body.get("answer", None)
            category = body.get("category", None)
            difficulty = body.get("difficulty", None)
            search_term = body.get("searchTerm", None)

            # Search Functionality
            if search_term:
                searched_questions = Question.query.filter(Question.question.ilike(f"%{search_term}%"))
                formatted_questions = [question.format() for question in searched_questions]
                total_questions = len(formatted_questions)  
                

                return jsonify({
                    'success': True,
                    'questions': formatted_questions,
                    'total_questions': total_questions
                })
        
            new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            new_question.insert()

            return jsonify({
                'success': True,
                'question': question
            })

        except:
            # except Exception as e:
            # print(str(e))
            db.session.rollback()
            abort(405)

        finally:
            db.session.close()

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<string:category_id>/questions')
    def get_category_questions(category_id):
        questions = Question.query.filter(Question.category == category_id)
        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'category': category_id
        })
        
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    return app

