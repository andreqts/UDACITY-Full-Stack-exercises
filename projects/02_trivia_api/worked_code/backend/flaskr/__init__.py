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
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers 
  @app.after_request
  def after_request(response):   
    response.headers.add('Access-Control-Allow-Origin', '*') 
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = get_paginated_questions(request, selection)

    if len(current_questions) == 0:
          page = request.args.get('page', 1, type=int)
          msg = f'Page {page} not found in the database'
          return jsonify({
            'success': False,
            'error': 404,
            'message': msg,
          })
  
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



  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods = ['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter_by(id=question_id).one_or_none()

      if question is None:
        msg = f'Question {question_id} not found in the database'
        return jsonify({
          'success': False,
          'error': 404,
          'message': msg,
        })

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


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
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
      return jsonify({
        'success': False,
        'error': 404,
        'message': msg,
      })

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

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


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
      return jsonify({ #TODOAQ: return with abort instead?
        'success': False,
        'error': 404,
        'msg': 'Category "{}" (id={}) not found in the database!'.format(
          quiz_category['type'],
          quiz_category['id'],
        ),
      })

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

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    