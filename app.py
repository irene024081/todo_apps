from email.policy import default
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:024081@localhost:5432/todoapp'
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey(
        "todolists.id"), nullable=False)

    def __repr__(self):
        return f'todo {self.id} {self.description}'


class TodoList(db.Model):
    __tablename__ = "todolists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable = False, default = False)
    todo_relation = db.relationship(Todo, backref="todolist", lazy=True)

# db.create_all()


@app.route("/todos/create", methods=['POST'])
def create():
    body = {}
    error = False
    try:
        #description = request.form.get("description"," ")
        description = request.get_json()['description']
        todo = Todo(description=description, completed=False)
        list_id = request.get_json()['list_id']
        active_list = TodoList.query.get(list_id)
        todo.todolist = active_list
        db.session.add(todo)
        db.session.commit()
        #body['id'] = todo.id
        #body['completed'] = todo.completed
        body['list_id'] = list_id
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
#   if use Ajax
    if error:
        abort(400)
    else:
        return jsonify(body)
#    if refresh every time
#    return redirect(url_for('index'))


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})


@app.route("/todos/<todo_id>/set-complete", methods=['POST'])
def set_completed(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
#    if refresh every time
    return redirect(url_for('index'))


@app.route('/list/<list_id>')
def get_list(list_id):
    return render_template('index.html', 
    lists = TodoList.query.all(),
    active_list = TodoList.query.get(list_id),
    data = Todo.query.filter_by(
        list_id = list_id).order_by('id').all())

@app.route('/')
def index():
    return redirect(url_for('get_list', list_id = 1))


@app.route("/list/create", methods=['POST'])
def create_list():
    body = {}
    error = False
    try:
        #description = request.form.get("description"," ")
        name = request.get_json()['name']
        list = TodoList(name = name)
        db.session.add(list)
        db.session.commit()
        #body['id'] = todo.id
        #body['completed'] = todo.completed
        body['list_id'] = list.id
        body['name'] = list.name
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
#   if use Ajax
    if error:
        abort(400)
    else:
        return jsonify(body)

@app.route('/list/<list_id>/delete', methods = ['DELETE'])
def delete_list(list_id):
    try:
        list = Todo.query.get(list_id)
        for todo in list.todo_relation:
            db.session.delete(todo)
        db.session.delete(list)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})

@app.route('/list/<list_id>/complete', methods = ['POST'])
def complete_list(list_id):
    try:
        completed = request.get_json()['complete']
        Todo.query.filter_by(list_id=list_id)['completed'] = completed
        list = Todo.query.get(list_id)
        for todo in list.todo_relation:
            todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
