# Backend - Full Stack Trivia API 

### Installing Dependencies for the Backend

1. **Python 3.8** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by navigating to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## Resource endpoint library

The documentation of the backend application endpoints are described below:

### Endpoints

```js
GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Parameters: None
- Returns: A JSON object with a single key, categories, containing an object of id: category_string key:value pairs. 
{
    'categories': { '1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports" }
    'total_categories': total number of categories,
    'success': True,
}
```

```js
GET '/questions?page=<page>
- Fetches a paginated set of questions, with a maximum of 10 questions per page, a total number of questions, all categories
and current category string. 
- Request Parameters: page - integer indicating the page to be returned
- Returns: A JSON object with 10 paginated questions, total questions, object including all categories, a current category
string, and a success key indicating no error has occurred.
{
    'questions': [
        {
            'id': 1,
            'question': 'This is a question',
            'answer': 'This is an answer', 
            'difficulty': 5,
            'category': 2
        },
        ...
    ],
    'total_questions': 100,
    'categories': { '1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports" },
    'current_category': 'History',
    'success': True,
}
```


```js
GET /api/v1.0/categories/<cat_id>/questions
- Fetches a dictionary of questions from a specific category
- Request Parameters: cat_id - integer value indicating category id of the questions to be returned
- Returns: A JSON object with the categories key, that contains an object of id: category_string key:value pairs, 
plus a total_categories key, with the total number of stored categories, and a boolean success key, indicating the 
operation has not failed.
{
    'questions':[
        {
            'id': 1,
            'question': 'This is a question',
            'answer': 'This is an answer', 
            'difficulty': 5,
            'category': 4 //supposing cat_id = 4
        },
        ...
    ]
    'total_questions': total number of questions,
    'current_category': 'History',
    'success': True,
}
```


```js
POST /api/v1.0/questions/search
- Fetches a dictionary of questions matching a given search term
- Request Parameters: search_term - string to search in the question field of the question objects. The search is
case insensitive.
- Returns: A JSON object with the questions key, that contains an array of question objects whose question field matches
the search_term, the total number of categories and a boolean success field that is true if there were no erros.
{
    'questions': [  {
            'id': 1,
            'question': 'This is a question',
            'answer': 'This is an answer', 
            'difficulty': 5,
            'category': 2
        },
    'total_categories': total number of categories,
    'success': True,
}
```


```js
POST /api/v1.0/quizzes
- Fetches a random question of the defined categories to the quiz play, that is not inside the previous questions array
- Request Parameters:
    1. <previous_questions> - array with a list of integer questions' ids of questions that cannot be returned.
    2. <quiz_category> - JSON object with keys id and type, containing respectively the integer id and the string 
    description of the category of the question to be returned, or { 'id': 0, 'type': 'All' } in case any category
    can be returned.
- Returns: A JSON object with the questions key, that contains the random question object of the specified category,
or any category in case quiz_categories parameter is { 'id': 0, 'type': 'All' }, the object representing the current
category, used as a filter for the randomly selected question, and also the total_quizz_questions, an integer value
that represents the total number of questions of the selected category (or categories) in the database.
The boolean success field is True if no errors have occurred.
{
    'question': [  {
            'id': 1,
            'question': 'This is a question',
            'answer': 'This is an answer', 
            'difficulty': 5,
            'category': 4 //supposing History category has been requested
        },
    'current_category': { 'id': 4, 'type': 'History' },
    'total_quizz_questions': 4,
    'success': True,
}
```


## Error Handling

The backend API returns errors always as JSON objects, having the following fields:

```js
{
  'success': False, // always false, indicating it is an error
  'error':   404, // HTTP error code
  'message': <string>, // string with the description of the error
}
```

The following error codes may be returned by the above endpoints:
1. **404:** means some required resource has not been found in the database. It may be, for instance a specific question of and unexistant page of questions. The 'message' field can describe which resource was missing.
2. **422:** the received request is correct but the server is unable to process it. The 'message' field describes what has happened.
3. **Others:** any other exception that may happen in the backend application or its components will be returned with appropriate information, in the format described above.

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
