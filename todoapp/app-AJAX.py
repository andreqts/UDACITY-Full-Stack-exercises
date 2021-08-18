from flask import Flask, render_template, request, redirect, url_for, jsonify, json, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

dbuser = 'andrequites'
dbpassword = '*#N-w3is7u&%' #NOTE: this code is meant only as a didactic tool. Please don't do it in production code
dbhost = 'localhost' 
dbname = 'todoapp'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}/{}'.format(dbuser, dbpassword, dbhost, dbname)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable = False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False);
    
    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

class Todolist(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)
    
    
page_title = "Andre's UDACITY Sample Todo app"
 
@app.route('/') # or @app.route('/<data>')
def index(): # or def index(data)
    print('returning template')
    
    first_list = Todolist.query.first()
    print(first_list)
    
    return redirect(url_for('get_todo_list', plist_id=first_list.id))
                          
@app.route('/todos/list/<plist_id>')
def get_todo_list(plist_id):
    print('returning template for list {}...'.format(plist_id))
    
    print('todos: {}'.format(Todo.query.filter_by(list_id=plist_id).order_by(Todo.id).all()))
    
    return render_template('index-AJAX.html', 
                            todos = Todo.query.filter_by(list_id=plist_id).order_by(Todo.id).all(),
                            datalists=Todolist.query.order_by(Todolist.id).all(),
                            actlistid = int(plist_id),
                            actlistname = Todolist.query.get(plist_id).name,
                            pgtitle = page_title,
                          )

#@app.route('/todos/create', methods = ['GET'])
@app.route('/todos/list/create_todo', methods = ['POST'])
def create_todo():
    try:
        print('create json = {}'.format(request.get_json()))
        new_todo_desc = request.get_json()['newtk']
        new_list_id = request.get_json()['newtk-listid']
        print(f'new_todo_desc "{new_todo_desc}" in lisd id {new_list_id}')
        newtask = Todo(description = new_todo_desc, list_id=new_list_id)    
        session = db.session()
        session.add(newtask)
        tadded = Todo.query.filter_by(description = f'{new_todo_desc}').first()
        print('=> New task added with id = {}'.format(tadded.id))
        respmap = {'newdesc': newtask.description, 'newid': tadded.id }
        session.commit()
    except:
        print('except')
        db.session.rollback()
        print(sys.exc_info())
        abort(500)
        assert(False)
    finally:
        print('finally closing...')
        db.session().close()

    return jsonify(respmap)
    
@app.route('/todos/list/create_list', methods = ['POST'])
def create_list():
    try:
        print('create json = {}'.format(request.get_json()))
        new_desc = request.get_json()['newlis']

        print(f'new_todo_desc "{new_desc}"')
        newlist = Todolist(name = new_desc)
        session = db.session()
        session.add(newlist)
        tadded = Todolist.query.filter_by(name = f'{new_desc}').first()
        print('=> New task added with id = {}'.format(tadded.id))
        respmap = {'newdesc': newlist.name, 'newid': tadded.id }
        session.commit()
    except:
        print('except')
        db.session.rollback()
        print(sys.exc_info())
        abort(500)
        assert(False)
    finally:
        print('finally closing...')
        db.session().close()

    return jsonify(respmap)


@app.route('/todos/list/<todo_id>/set-tkcompleted', methods = ['POST'])
def set_completed_todo(todo_id):
    print('set-completed{}...'.format(todo_id))
    try:
        completed = request.get_json()['tk-completed']
        print(f'completed = {completed}')
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(400)

    finally:
        db.session.close()

    return redirect(url_for('index'))


@app.route('/todos/list/<todo_id>/tk-deleted', methods = ['DELETE'])
def delete_task(todo_id):
    try:
        assert(Todo.query.filter_by(id = todo_id).count() == 1)
        del_op = Todo.query.get(todo_id)
        print('delete id = {} - task...'.format(todo_id))
        print(del_op)
        db.session.delete(del_op)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(400)

    finally:
        db.session.close()

    return jsonify({ 'success': True })
    
@app.route('/todos/list/<todolist_id>/lis-deleted', methods = ['DELETE'])
def delete_tasklist(todolist_id):
    try:
        #firstly, lets delete every task associated with the list to be deleted
        db.session.query(Todo).filter_by(list_id = todolist_id).delete()

        #now deletes the todolist from the DB
        del_op = Todolist.query.get(todolist_id)
        print('delete id = {} - list...'.format(todolist_id))
        print(del_op)
        db.session.delete(del_op)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(400)

    finally:
        db.session.close()

    return jsonify({ 'success': True })
    
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5000)