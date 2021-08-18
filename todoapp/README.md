André's UDACITY Todoapp
-----

## Introduction

This app has been developped by me, with the sole purpose of acomplishing the first proposed home work of the Udacity's Full Stack online course, which I attended in 2021.
It has been pushed here so as to keep a record of my progress throughout the course, so I can lately check my progress, and how I had solved every proposed challenge.
It implements a simple web todolists' manager.

## Overview

The app is composed of two divs. The first one, on the left, presents the list of todolists, and allows the user to create, delete and select different lists. The lists are shown as links. The user can select a list by clicking on it. The list selected is shown in bold.

The div on the right presents the list of tasks associated with the selected task list. It also allows the user to delete and create tasks. Each task has an associated checkbox, allowing the user to check it, indicating it has been completed.

## Tech Stack (Dependencies)

### 1. Backend Dependencies
Our tech stack will include the following:
 * **virtualenv** as a tool to create isolated Python environments
 * **SQLAlchemy ORM** to be our ORM library of choice
 * **PostgreSQL** as our database of choice
 * **Python3** and **Flask** as our server language and server framework
 * **Flask-Migrate** for creating and running schema migrations
You can download and install the dependencies mentioned above using `pip` as:
```
pip install virtualenv
pip install SQLAlchemy
pip install postgres
pip install Flask
pip install Flask-Migrate
```
> **Note** - If we do not mention the specific version of a package, then the default latest stable package will be installed. 

### 2. Frontend Dependencies
You must have the **HTML**, **CSS**, and **Javascript** for our website's frontend.

## Main Files: Project Structure

  ```sh
  ├── README.md
  ├── app-AJAX.py *** the main driver of the app. Includes your SQLAlchemy models.
                    "python app.py" to run after installing dependencies
  ├── config.py *** Database URLs, CSRF generation, etc
  ├── error.log
  ├── forms.py *** Your forms
  ├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
  ├── migrations
  │   ├── README
  │   ├── alembic.ini
  │   ├── env.py
  │   ├── script.py.macro
  │   └── versions
  |         └── edeb655597c0_.py: first migration to build the tables with default data
  └── templates
      └── index-AJAX.html
  ```

Overall:
* Models and Controllers are located in `app-AJAX.py`.
* The web frontend is located in `templates/`.



3. **Initialize and activate a virtualenv using:**
```
python -m virtualenv env
source env/bin/activate
```
>**Note** - In Windows, the `env` does not have a `bin` directory. Therefore, you'd use the analogous command shown below:
```
source env/Scripts/activate
```

4. **Install the dependencies:**
```
pip install -r requirements.txt
```

5. **Run the development server:**
```
export FLASK_APP=myapp
export FLASK_ENV=development # enables debug mode
python3 app.py
```

6. **Verify on the Browser**<br>
Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000](http://localhost:5000) 

