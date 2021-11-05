import os, sys
import logging
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from  sqlalchemy.sql.expression import func

from models import setup_db, Question, Category
from sqlalchemy.sql.expression import null

QUESTIONS_PER_PAGE = 10

def get_paginated_questions(request, selection):
  page = request.args.get("page", 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

 
def categories_to_dict(categories_selection):
  categories = [cat.format() for cat in categories_selection]

  categories_dict = {}
  for cat in categories:
    categories_dict[cat['id']] = cat['type']

  return categories_dict


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  app.db = SQLAlchemy(app)

  if test_config == None:
    setup_db(app) # create only if it is not a unit test

  logging.basicConfig(filename='backend_errors.log', format='%(asctime)s %(message)s', level=logging.ERROR)
  
  CORS(app)

  # CORS Headers 
  @app.after_request
  def after_request(response):   
    response.headers.add('Access-Control-Allow-Origin', '*') 
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/api/v1.0/questions')
  def get_questions():
    try:
      selection = Question.query.order_by(Question.id).all()
      current_questions = get_paginated_questions(request, selection)

      if len(current_questions) == 0:
        page = request.args.get('page', 1, type=int)
        msg = f'Page {page} not found in the database'
        abort(404, msg)
    
      #with_entities returns the fields in a tuple
      categories_selection = Category.query.order_by(Category.id).all()
      categories_dict = categories_to_dict(categories_selection)

      return jsonify({
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': categories_dict,
            'current_category': '',
            'success': True,
      })
    except HTTPException:
      raise
    except:
      abort(422, sys.exc_info())
    

  @app.route('/api/v1.0/questions/<int:question_id>', methods = ['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter_by(id=question_id).one_or_none()

      if question is None:
        msg = f'Question {question_id} not found in the database'
        abort(404, msg)

      question.delete()

      total_questions = len(Question.query.all())
      
      return jsonify(
        {
            "success": True,
            "deleted": question_id,
            "total_questions": total_questions,
        }
      )
    except HTTPException:
      raise
    except:
      abort(422, sys.exc_info())

  @app.route('/api/v1.0/questions', methods=['POST'])
  def add_question():
    try:
      body = request.get_json()

      new_question = body.get('question', '')
      new_answer = body.get('answer', '')
      new_difficulty = body.get('difficulty', 0)
      new_category = body.get('category', 0)

      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()

      selection = Question.query.all()

      return jsonify({
        'success': True,
        'created_id': question.id,
        'total_questions': len(selection),
      })
    except HTTPException:
      raise
    except:
      abort(422, sys.exc_info())

  @app.route('/api/v1.0/categories')
  def get_categories():
    try:
      selection = Category.query.all()
      
      categories_dict = categories_to_dict(selection)

      return jsonify({
        'success': True,
        'categories': categories_dict,
        'total_categories': len(selection),
      })

    except HTTPException:
      raise
    except:
      abort(422, sys.exc_info())
  
  
  @app.route('/api/v1.0/categories/<int:cat_id>/questions')
  def get_questions_by_category(cat_id):
    category = []
    try:
      category = Category.query.get(cat_id)

      if (category is None):
        msg = f'Category {cat_id} not found in the database'
        abort(404, msg)

      selection = Question.query.filter_by(category=cat_id).all()

      total_questions = len(selection)
      assert(total_questions <= QUESTIONS_PER_PAGE)
      
      questions = [question.format() for question in selection]

      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': len(Question.query.all()),
        'current_category': category.type,
      })
    except HTTPException:
      raise
    except:
      abort(422, sys.exc_info())

  @app.route('/api/v1.0/questions/search', methods=['POST'])
  def search_questions():
    try:
      body = request.get_json()
      str_to_search = body.get('searchTerm', '')
      selection = Question.query.filter(Question.question.ilike(f'%{str_to_search}%')).all()
      questions_found = [question.format() for question in selection]

      return jsonify({
        'success': True,
        'questions': questions_found,
        'total_questions': len(Question.query.all()),
        'current_category': '',
      })
    except HTTPException:
      raise
    except:
      abort(422, sys.exc_info())
  
  @app.route('/api/v1.0/quizzes', methods=['POST'])
  def get_quizzes():
    try:
      body = request.get_json()
      prev_question = body.get('previous_questions', '')
      quiz_category = body.get('quiz_category', '')

      select = None
      category_id = int(quiz_category['id'])

      if (category_id > 0):
        category = app.db.session().query(Category).get(category_id)
        if (category == None):
          msg = f'Category "{quiz_category["type"]}" (id={category_id}) not found in the database!'
          abort(404, msg)
        
      total_quizz_questions = -1
      if category_id == 0: # All categories
        select = Question.query.filter(~Question.id.in_(prev_question)).order_by(func.random()).all()
        total_quizz_questions = len(Question.query.all())
      else:
        select = Question.query.filter(Question.category == category_id, ~Question.id.in_(prev_question)).order_by(func.random()).all()
        total_quizz_questions = len(Question.query.filter_by(category=category_id).all())

      next_question = select[0].format() if len(select) else ''
    
      return jsonify({
        'success': True,
        'question': next_question,
        'current_category': quiz_category,
        'total_quizz_questions': total_quizz_questions,
      })
    except HTTPException:
      raise
    except:
      abort(422, sys.exc_info())

  # DEFAULT ERROR HANDLERS
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

  return app

    