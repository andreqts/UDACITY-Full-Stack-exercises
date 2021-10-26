import os, sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random as rnd

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

  if test_config == None:
    setup_db(app) # create only if it is not a unit test
  
  CORS(app)

  # CORS Headers 
  @app.after_request
  def after_request(response):   
    response.headers.add('Access-Control-Allow-Origin', '*') 
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/questions')
  def get_questions():
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

  @app.route('/questions/<int:question_id>', methods = ['DELETE'])
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
        abort(422)

  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()

    new_question = body.get('question', '')
    new_answer = body.get('answer', '')
    new_difficulty = body.get('difficulty', 0)
    new_category = body.get('category', 0)

    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()

      selection = Question.query.all()

      return jsonify({
        'success': True,
        'created_id': question.id,
        'total_questions': len(selection),
      })

    except:
      abort(422)

  
  @app.route('/categories')
  def get_categories():
    try:
      selection = Category.query.all()
      
      categories_dict = categories_to_dict(selection)

      return jsonify({
        'success': True,
        'categories': categories_dict,
        'total_categories': len(selection),
      })

    except:
      abort(422)
  
  
  @app.route('/categories/<int:cat_id>/questions')
  def get_questions_by_category(cat_id):
    category = []
    try:
      category = Category.query.get(cat_id)
    except:
      abort(422)

    if (category is None):
      msg = f'Category {cat_id} not found in the database'
      abort(404, msg)

    selection = []
    try:
      selection = Question.query.filter_by(category=cat_id).all()

      total_questions = len(selection)
      assert(total_questions <= QUESTIONS_PER_PAGE)
    except HTTPException:
        raise
    except:
        abort(422)
     
    questions = [question.format() for question in selection]

    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': len(Question.query.all()),
      'current_category': category.type,
    })

  @app.route('/questions/search', methods=['POST'])
  def search_venues():
    try:
      body = request.get_json()
      str_to_search = body.get('searchTerm', '')
      selection = Question.query.filter(Question.question.ilike(f'%{str_to_search}%')).all()
      questions_found = [question.format() for question in selection]
    except:
      print(sys.exc_info())
      abort(422)

    return jsonify({
      'success': True,
      'questions': questions_found,
      'total_questions': len(Question.query.all()),
      'current_category': '',
    })
  
  @app.route('/quizzes', methods=['POST'])
  def get_quizzes():
    body = request.get_json()
    prev_question = body.get('previous_questions', '')
    quiz_category = body.get('quiz_category', '')

    select_cat = None
    try:
      if quiz_category['id'] == 0: # All categories
        select_cat = Question.query.all()
      else:
        select_cat = Question.query.filter_by(category=quiz_category['id']).all()
    except:
      print(sys.exc_info())
      abort(422)

    if len(select_cat) == 0:
      msg = 'Category "{}" (id={}) not found in the database!'.format(
        quiz_category['type'],
        quiz_category['id'],
      )
      abort(404, msg)


    allowed_questions = [q for q in select_cat if (q.id not in prev_question)]
    allowed_questions_cnt =len(select_cat)

    if allowed_questions_cnt > 0:
      rnd.shuffle(allowed_questions)

      chosen_question = null
      for q in allowed_questions:
        if q.id not in prev_question:
          chosen_question = q
          break

    next_question = chosen_question.format() if chosen_question != null else ''
  
    return jsonify({
      'success': True,
      'question': next_question,
      'current_category': quiz_category,
    })

  @app.errorhandler(404)
  def not_found(error):
    default_msg = "resource not found in the server's database"
    message = error.description if len(error.description) else default_msg
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
    return (
      jsonify({
        'success': False,
        'error': 422,
        'message': f"unprocessable entity - {message}"
      }),
      422,
    )

  return app

    