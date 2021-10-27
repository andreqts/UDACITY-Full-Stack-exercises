# Full Stack API Final Project

## Introduction

### Full Stack Trivia

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game. The backend API, which makes the interface with the database, was left to the students to complete. Here I present my version of the game with my backend, including some small changes to the React frontend as well.

This application includes the following features:

1. Display questions - both all questions and by category. Questions should show the question, category, and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include a question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.

## Getting Started

The frontend application is implemented in React. All persistent data is stored in the backend server, in a Postgresql database. The backend server is implemented using Flask, in Python, and SQLAlchemy ORM.
The frontend communicates asynchronously with the backend, using AJAX, through a well-defined backend API, whose endpoints are documented in the [./backend](https://github.com/udacity/FSND/blob/master/projects/02_trivia_api/starter/backend/README.md) directory.
The application was designed to be tested running in localhost. The **backend** runs by default on **TCP port 5000**, while the **frontend** runs on **TCP port 3000**.
Data exchanged between the frontend and backend applications is always in **JSON format**.
Test codes are provided in Python for the backend and React for the frontend, covering all essential functionality.
For the backend, unit tests cover every endpoint and its most likely possible error handling.

### Installation

To be able to run this application locally, you can proceed with the following steps:
1. Fork this repo
2. Clone it
3. Create a new python environment to this application.
4. Install the requirements from the `requirements.txt` file in the `backend` folder, running the following command in your command line:
    `pip install -r requirements.txt`.       
5. Set the environment variable `FLASK_APP` as `flaskr`, and optionally you can set `FLASK_ENV` as `development` to run in debug mode. Look at your operating system documentation to see how to set those variables (hint: you can use the `export` command in Linux, and the `set` command in Windows).
6. Go to the backend folder and start the backend application with the following command: `flask run`.
7. Go to the frontend folder and start the frontend application by running the following command: `npm start`.

### Running tests

After installation, you can run the complete **backend test suite** from the `/backend` folder, by running: `python test_flaskr.py`.
To execute the **front end** test suite, go to the `/frontend` folder and run `npm test`.

To test the response of the backend, you can use the [curl command line tool](https://curl.se/). For instance, if you what to get the first page of the whole list of questions (the return is paginated with 10 questions per page), having the flask backend app running, you can run from the command line:

`curl -XGET localhost:5000/questions`

The command above must return the first page of questions, with 10 questions' objects formatted as JSON.

## About the Stack

This full stack application is designed with some key functional areas:

### Backend

The [./backend](https://github.com/udacity/FSND/blob/master/projects/02_trivia_api/starter/backend/README.md) directory contains a complete Flask and SQLAlchemy server. The file `__init__.py` defines the backend endpoints and can reference models.py for DB and SQLAlchemy setup.

### Frontend

The [./frontend](https://github.com/udacity/FSND/blob/master/projects/02_trivia_api/starter/frontend/README.md) directory contains a complete React frontend to consume the data from the Flask server.
These are the files you may want to check:

1. *./frontend/src/components/QuestionView.js*
2. *./frontend/src/components/FormView.js*
3. *./frontend/src/components/QuizView.js*

>View the [README within ./frontend for more details.](./frontend/README.md)
