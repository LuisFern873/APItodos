# Environment variables
# $env:FLASK_APP = "server"
# $env:FLASK_ENV = "development"
from flask import Flask, jsonify, abort, request
from flask_cors import CORS, cross_origin
from models import setup_db, Todo, TodoList

TODOS_PER_PAGE = 5

def paginate_todos(request, selection, isDescendent = False):
    if isDescendent:
        start = len(selection) - TODOS_PER_PAGE
        end = len(selection)
    else:
        page = request.args.get('page', 1, type = int)
        start = (page - 1)*TODOS_PER_PAGE
        end = start + TODOS_PER_PAGE
    
    todos = [todo.format() for todo in selection]
    current_todos = todos[start:end]
    return current_todos

def create_app(test_config = None):
  app = Flask(__name__)
  setup_db(app)

  CORS(app, origins = "http://127.0.0.1:5500/templates/index.html", max_age = 10)

  @app.after_request
  def after_resquest(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorizations, true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response


  @app.route("/todos", methods = ["GET"])
  @cross_origin()
  def get_todos():
    selection = Todo.query.order_by('id').all()
    todos = paginate_todos(request, selection)

    if(len(todos) == 0):
      abort(404)

    return jsonify({
      'success': True,
      'todos': todos,
      'total_todos': len(todos)
    })
  

  @app.route("/todos", methods = ["POST"])
  def create_todo():
    # JSON BODY
    body = request.get_json()
    
    description = body.get('description', None)
    completed = body.get('completed', None)
    list_id = body.get('list_id', None)

    todo = Todo(description = description, completed = completed, list_id = list_id)

    todo.insert()

    selection = Todo.query.order_by('id').all()

    current_todos = paginate_todos(request, selection)

    return jsonify({
        'success': True,
        'created': todo.format(),
        'todos': current_todos,
        'total_todos': len(selection)
    })

  @app.route("/todos/<todo_id>", methods = ["PATCH"])
  def update_todo(todo_id):
    todo = Todo.query.filter_by(id = todo_id).one_or_none()

    if todo == None:
      abort(404)

    body = request.get_json()

    if 'description' in body:
        todo.description = body.get('description')

    todo.update()

    return jsonify({
        'success': True,
        'id': todo_id
    })

  @app.route('/todos/<todo_id>', methods=['DELETE'])
  def delete_todo(todo_id):
      error_404 = False
      try:
          todo = Todo.query.filter(Todo.id == todo_id).one_or_none()
          if todo is None:
              error_404 = True
              abort(404)
          
          todo.delete()
          selection = Todo.query.order_by('id').all()
          todos = paginate_todos(request, selection, True)

          return jsonify({
              'success': True,
              'deleted': todo_id,
              'todos': todos,
              'total_todos': len(selection)
          })

      except Exception as exp:
          print(exp)

          if error_404:
              abort(404)
          else:
              abort(500)

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          'success': False,
          'code': 404,
          'message': 'resource not found'
      }), 404

  @app.errorhandler(500)
  def server_error(error):
      return jsonify({
          'success': False,
          'code': 500,
          'message': 'Internal Server Error'
      }), 404

  return app
