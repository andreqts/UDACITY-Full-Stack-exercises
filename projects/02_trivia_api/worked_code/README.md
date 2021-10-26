# Full Stack API Final Project


## Full Stack Trivia

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game.

This application includes the following features:

1. Display questions - both all questions and by category. Questions should show the question, category, and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include a question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.

## Installation

To be able to run this application locally, you can proceed with the following steps:
1. Fork this repo
2. Clone it
3. Create a new python environment to this application.
4. Install the requirements from the `requirements.txt` file in the `backend` folder, running the following command in your command line:
    `pip install -r requirements.txt`.       
5. Set the environment variable `FLASK_APP` as `flaskr`, and optionally you can set `FLASK_ENV` as `development` to run in debug mode. Look at your operating system documentation to see how to set those variables (hint: you can use the `export` command in Linux, and the `set` command in Windows).
6. Go to the backend folder and start the backend application with the following command: `flask run`.
7. Go to the frontend folder and start the frontend application by running the following command: `npm start`.

## About the Stack

This full stack application is designed with some key functional areas:

### Backend
The [./backend](https://github.com/udacity/FSND/blob/master/projects/02_trivia_api/starter/backend/README.md) directory contains a complete Flask and SQLAlchemy server. The file `__init__.py` defines the backend endpoints and can reference models.py for DB and SQLAlchemy setup.




### Frontend

The [./frontend](https://github.com/udacity/FSND/blob/master/projects/02_trivia_api/starter/frontend/README.md) directory contains a complete React frontend to consume the data from the Flask server. If you have prior experience building a frontend application, you should feel free to edit the endpoints as you see fit for the backend you design. If you do not have prior experience building a frontend application, you should read through the frontend code before starting and make notes regarding:

1. What are the end points and HTTP methods the frontend is expecting to consume?
2. How are the requests from the frontend formatted? Are they expecting certain parameters or payloads? 

Pay special attention to what data the frontend is expecting from each API response to help guide how you format your API. The places where you may change the frontend behavior, and where you should be looking for the above information, are marked with `TODO`. These are the files you'd want to edit in the frontend:

1. *./frontend/src/components/QuestionView.js*
2. *./frontend/src/components/FormView.js*
3. *./frontend/src/components/QuizView.js*


By making notes ahead of time, you will practice the core skill of being able to read and understand code and will have a simple plan to follow to build out the endpoints of your backend API. 



>View the [README within ./frontend for more details.](./frontend/README.md)
