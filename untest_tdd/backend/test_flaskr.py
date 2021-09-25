import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Book


class BookTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        self.new_book = {"title": "Anansi Boys", "author": "Neil Gaiman", "rating": 5}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_books(self):
        res = self.client().get("/books")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_books"])
        self.assertTrue(len(data["books"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/books?page=1000", json={"rating": 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_search_book_by_title(self):
        test_searchterm = 'novel'
        res = self.client().get("/books?searchterm={}".format(test_searchterm))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

        bookslst = data["books"]
        self.assertTrue(len(bookslst)==3)
        self.assertTrue(str(bookslst) == "[{'author': 'Lisa Halliday', 'id': 2, 'rating': 4, 'title': 'Asymmetry: A Novel'}, {'author': 'Gina Apostol', 'id': 9, 'rating': 5, 'title': 'Insurrecto: A Novel'}, {'author': 'Jojo Moyes', 'id': 5, 'rating': 5, 'title': 'Still Me: A Novel'}]")

    def test_search_book_by_author(self):
        test_searchterm = 'neil'
        res = self.client().get("/books?searchterm={}".format(test_searchterm))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

        bookslst = data["books"]
        self.assertTrue(len(bookslst)==2)
        print('Books found searching for "Neil": "{}"'.format(str(bookslst)))
        self.assertTrue(str(bookslst) == "[{'author': 'Neil Gaiman', 'id': 23, 'rating': 5, 'title': 'Anansi Boys'}, {'author': 'Neil Gaiman', 'id': 24, 'rating': 5, 'title': 'Anansi Boys'}]")

    def test_404_search_nonexistent_book(self):
        test_searchterm = 'anythingnonexistent'
        res = self.client().get("/books?searchterm={}".format(test_searchterm))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_update_book_rating(self):
        res = self.client().patch("/books/5", json={"rating": 1})
        data = json.loads(res.data)
        book = Book.query.filter(Book.id == 5).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(book.format()["rating"], 1)

    def test_400_for_failed_update(self):
        res = self.client().patch("/books/5")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_delete_book(self):
        res = self.client().delete("/books/1")
        data = json.loads(res.data)

        book = Book.query.filter(Book.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertTrue(data["total_books"])
        self.assertTrue(len(data["books"]))
        self.assertEqual(book, None)

    def test_404_if_book_does_not_exist(self):
        res = self.client().delete("/books/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_create_new_book(self):
        res = self.client().post("/books", json=self.new_book)
        data = json.loads(res.data)
        pass

    def test_422_if_book_creation_fails(self):
        res = self.client().post("/books", json=self.new_book)
        data = json.loads(res.data)
        pass


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
