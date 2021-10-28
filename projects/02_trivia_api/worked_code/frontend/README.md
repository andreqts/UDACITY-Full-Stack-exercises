# Frontend - Full Stack Trivia API 

### Getting Setup

> _tip_: this frontend is designed to work with [Flask-based Backend](../backend). It is recommended you stand up the backend first, test using Postman or curl, update the endpoints in the frontend, and then the frontend should integrate smoothly.

### Installing Dependencies

1. **Installing Node and NPM**<br>
This project depends on Nodejs and Node Package Manager (NPM). Before continuing, you must download and install Node (the download includes NPM) from [https://nodejs.com/en/download](https://nodejs.org/en/download/).

2. **Installing project dependencies**<br>
This project uses NPM to manage software dependencies. NPM Relies on the package.json file located in the `frontend` directory of this repository. After cloning, open your terminal and run:
```bash
npm install
```
>_tip_: **npm i** is shorthand for **npm install**

# Required Tasks

### Running Your Frontend in Dev Mode

The frontend app was built using create-react-app. In order to run the app in development mode use ```npm start```. You can change the script in the ```package.json``` file. 

Open [http://localhost:3000](http://localhost:3000) to view it in the browser. The page will reload if you make edits.<br>

```bash
npm start
```

### Game Play Mechanics Improvements

In the UDACITY starting scratch code, when a user played the game they played up to five questions of the chosen category. If there were fewer than five questions in a category, the game would end suddenly when there are no more questions in that category.

**The game play mechanics have been improved to inform the player on the maximum number of questions in each play**, considering the maximum number of questions of the selected category in the database.
The frontend has also been improved to inform the user about his/her score during the play.


**Here are the expected endpoints and behavior**:


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
