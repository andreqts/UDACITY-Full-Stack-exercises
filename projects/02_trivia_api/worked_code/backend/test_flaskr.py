import os
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
        testConfig = {} # for now it is just used to allow skiping config
                        # stuff that is not used when testing

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
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_first_page_of_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_books"])
        self.assertTrue(len(data["books"]) == QUESTIONS_PER_PAGE)

    def test_get_page_1_of_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_books"])
        self.assertTrue(len(data["books"]) == QUESTIONS_PER_PAGE)

    def test_get_page_2_of_questions(self):
        res = self.client().get("/questions?page=2")
        data = json.loads(res.data)

        QUESTIONS_PAGE2 = QUESTIONS_TOTAL - QUESTIONS_PER_PAGE

        # test is prepared to have just two pages in DB
        assert(QUESTIONS_PAGE2 <= QUESTIONS_PER_PAGE)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_books"])
        self.assertTrue(len(data["books"]) == QUESTIONS_PAGE2)
    
    def test_404_get_nonexistant_page_of_questions(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()