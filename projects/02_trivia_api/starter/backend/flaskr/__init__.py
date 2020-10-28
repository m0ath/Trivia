import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
import random

from models import setup_db, Question, Category

# number of questions per page
QUESTIONS_PER_PAGE = 10

# function to controll questions per page


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow '*' for origins.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Headers',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    #   Create an endpoint to handle GET requests
    #   for all available categories.
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        array_categories = {}
        for category in categories:
            array_categories[category.id] = category.type

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': array_categories
        })

  #   Create an endpoint to handle GET requests for questions,
  #   including pagination (every 10 questions).
  #   This endpoint should return a list of questions,
  #   number of total questions, current category, categories.
    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        array_categories = {}

        for category in categories:
            array_categories[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': array_categories,
            'total_questions': len(Question.query.all()),
        })

    #  Create an endpoint to DELETE question using a question ID.
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except BaseException:
            abort(422)

    #   Create an endpoint to POST a new question,
    #   which will require the question and answer text,
    #   category, and difficulty score.
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except BaseException:
            abort(422)

    #   Create a POST endpoint to get questions based on a search term.
    #   It should return any questions for whom the search term
    #   is a substring of the question.
    @app.route('/search', methods=['POST'])
    def search():
        body = request.get_json()
        search = body.get('searchTerm', None)

        if search == '':
            abort(422)

        try:
            selection = Question.query.order_by(
                Question.id).filter(
                Question.question.ilike(
                    '%{}%'.format(search))).all()
            current_questions = paginate_questions(request, selection)

            if len(selection) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except BaseException:
            abort(404)

    # Create a GET endpoint to get questions based on category.
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def categories_with_questions(category_id):
        category = Category.query.filter(
            Category.id == category_id).one_or_none()

        if category is None:
            abort(404)

        try:
            selection = Question.query.order_by(
                Question.id).filter_by(
                category=category_id).all()
            current_questions = paginate_questions(request, selection)

            if len(selection) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'id_category': category.id,
                'current_category': category.type,
                'total_questions': len(selection),
            })

        except BaseException:
            abort(404)

    #   Create a POST endpoint to get questions to play the quiz.
    #   This endpoint should take category and previous question parameters
    #   and return a random questions within the given category,
    #   if provided, and that is not one of the previous questions.
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        body = request.get_json()

        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')
        category_id = quiz_category['id']

        try:
            if category_id == 0:
                selection = Question.query.order_by(func.random())
            else:
                selection = Question.query.filter(
                    Question.category == category_id).order_by(
                    func.random())

            all_selection = len(selection.all())
            if all_selection == 0:
                abort(404)
            else:
                current_questions = selection.filter(
                    Question.id.notin_(previous_questions)).first()

            if current_questions is None:
                return jsonify({
                    'success': False,
                    'all_selection': len(selection.all()),
                })

            return jsonify({
                'success': True,
                'question': current_questions.format(),
                'category_id': category_id,
                'all_selection': len(selection.all()),
            })

        except BaseException:
            abort(422)

    #   Create error handlers for all expected errors
    #   including 404, 405 and 422.
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Opss! Not found it'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable, try one more time :D'
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not Allowed here :('
        }), 405

    return app
