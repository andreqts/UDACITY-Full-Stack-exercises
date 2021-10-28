import os, sys
from re import search, sub
import subprocess
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
QUESTIONS_TOTAL = 19


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        # print('SETTING UP NEW TEST...')
        testConfig = {} # for now it is just used to allow skiping config
                        # stuff that is not used when testing

        
        # Does not work here, since I cant disconnect completely in tearDown
        #subprocess.call('./inittestdb.sh')

        self.app = create_app(testConfig)
        self.client = self.app.test_client

        database_name = "trivia_test"
        db_username = 'student'
        db_userpassword = 'UdacityExercises21'
        db_host = 'localhost'
        db_host_port = 5432

        self.database_path = "postgresql://{}{}{}@{}:{}/{}".format(
            db_username,
            ':' if len(db_userpassword) else '',
            db_userpassword,
            db_host,
            db_host_port,
            database_name
        )

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        # print('==> TEAR DOWN TEST CONNECTIONS...')
        pass

        # To make each test independent, I would like to reset the database here and
        # recreate it in setUp, but I could not manage to disconnect, and I have seen
        # in StackOverflow it is not easy to do:

        # with self.app.app_context():
        #     try:
        #         print('starting to close...')
        #         self.db.session.remove()
        #         print('session closed...')
        #     except:
        #         print(sys.exc_info())
        #         abort(500)
        #     try:
        #         self.db.engine.dispose()
        #         print('database connection disposed')
        #     except:
        #         print(sys.exc_info())
        #         abort(500)

    def test_get_first_page_of_questions(self):
        res = self.client().get("/api/v1.0/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]) == QUESTIONS_PER_PAGE)

    def test_get_page_1_of_questions(self):
        res = self.client().get("/api/v1.0/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]) == QUESTIONS_PER_PAGE)

    def test_get_page_2_of_questions(self):
        res = self.client().get("/api/v1.0/questions?page=2")
        data = json.loads(res.data)

        QUESTIONS_PAGE2 = QUESTIONS_TOTAL - QUESTIONS_PER_PAGE

        # test is prepared to have just two pages in DB
        assert(QUESTIONS_PAGE2 <= QUESTIONS_PER_PAGE)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]) == QUESTIONS_PAGE2)

    def test_get_questions_by_category(self):
        CATEGORY_TO_SEARCH = 2
        res = self.client().get("/api/v1.0/categories/{}/questions".format(
                CATEGORY_TO_SEARCH,
            ))
        EXPECTED_TOTAL_QUESTIONS = 4
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), EXPECTED_TOTAL_QUESTIONS)
        self.assertEqual(data["current_category"], "Art")


    def test_404_get_questions_of_nonexistent_category(self):
        CATEGORY_TO_SEARCH = 1000
        res = self.client().get("/api/v1.0/categories/{}/questions".format(
                CATEGORY_TO_SEARCH,
            ))
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 404)        
        self.assertEqual(data["message"], f'Category {CATEGORY_TO_SEARCH} not found in the database')

    def test_404_get_nonexistant_page_of_questions(self):
        nonexistent_page = 1000
        res = self.client().get("/api/v1.0/questions?page={}".format(nonexistent_page))
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 404)        
        self.assertEqual(data["message"], f'Page {nonexistent_page} not found in the database')

    def test_delete_question(self):
        question_id = 10

        prev_total = len(Question.query.all())
       
        res = self.client().delete(f"/api/v1.0/questions/{question_id}")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], question_id)
        self.assertEqual(data["total_questions"], prev_total - 1)

    def test_add_question(self):
        self.new_question = {
            "question": 'Who discovered the America?',
            "answer": 'Christopher Columbus',
            'difficulty': 4,
            'category': 4,
        }

        prev_total = len(Question.query.all())
        
        res = self.client().post(f"/api/v1.0/questions", json=self.new_question)
        data = json.loads(res.data)

        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["created_id"], 24)        
        self.assertEqual(data["total_questions"], prev_total + 1)

    def test_get_categories(self):
        res = self.client().get("/api/v1.0/categories")
        data = json.loads(res.data)

        CATEGORIES_TOTAL = 6
        categories = data['categories']
        categories_total = len(categories)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(categories_total, CATEGORIES_TOTAL)
        self.assertEqual(data["total_categories"], categories_total)
        self.assertEqual(categories["1"], 'Science')

    def test_search_questions(self):
        search_term = 'the'
        res = self.client().post("/api/v1.0/questions/search", json={ 'searchTerm': search_term })
        data = json.loads(res.data)
        EXPECTED_TOTAL_MIN = 10

        all_have_term = True
        for q in data['questions']:
            if search_term not in q['question'].lower():
                print('===> "{}" not found in "{}"'.format(search_term, q['question']))
                all_have_term = False

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]) > EXPECTED_TOTAL_MIN)
        self.assertTrue(all_have_term)
        self.assertEqual(data["total_questions"], len(Question.query.all()))

    def test_quizz(self):
        res = self.client().post("/api/v1.0/quizzes", json={
                'previous_questions': [ 9, 12, 23, 24 ], 
                'quiz_category': { 'id': 4, 'type': 'History' },
            })
        data = json.loads(res.data)

        total_hist_questions = len(Question.query.filter_by(category=4).all())

        self.assertTrue(data["success"])
        self.assertEqual(data['question']['id'], 5)
        self.assertEqual(data['current_category']['type'], 'History')
        self.assertEqual(data['total_quizz_questions'], total_hist_questions)

    def test_quiz_all_categories(self):
        res = self.client().post("/api/v1.0/quizzes", json={
                'previous_questions': [ 9, 12, 23, 24 ], 
                'quiz_category': { 'id': 0, 'type': 'All' },
            })
        data = json.loads(res.data)

        total_hist_questions = len(Question.query.all())

        self.assertTrue(data["success"])
        self.assertTrue(data['question']['id'] > 0)
        self.assertEqual(data['current_category']['type'], 'All')
        self.assertEqual(data['total_quizz_questions'], total_hist_questions)


    def test_error_404_quizz_with_nonexistent_category(self):
        res = self.client().post("/api/v1.0/quizzes", json={
                'previous_questions': [ 9, 12, 23, 24 ], 
                'quiz_category': { 'id': 1000, 'type': 'Nonexistent' },
            })
        data = json.loads(res.data)

        self.assertFalse(data["success"])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Category "Nonexistent" (id=1000) not found in the database!')


# Make the tests conveniently executable
if __name__ == "__main__":
    subprocess.call('./inittestdb.sh') # resets de database (does not work in setUp)
    unittest.main()