from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, request, abort, make_response
import sqlalchemy


tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# Validate there are title and description when creating or updating task
def validate_create_or_put():
    request_body = request.get_json()
    try:
        new_task = Task(title=request_body["title"],
                    description=request_body["description"])
    except:
        rsp = {
            "details": "Invalid data"
        }
        abort(make_response(jsonify(rsp), 400))
    return new_task

@tasks_bp.route('', methods=['POST'])
def create_one_task():
    new_task = validate_create_or_put()
    
    db.session.add(new_task)
    db.session.commit()

    return { "task": {
        "id": new_task.task_id,
        "title": new_task.title,
        "description": new_task.description,
        "is_complete": False
    }}, 201

@tasks_bp.route('', methods=['GET'])
def get_all_tasks():
    tasks = Task.query.all()
    sort_params = request.args.get("sort")

    if sort_params == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_params == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
        
    rsp = []
    # refactor opporunity when appending tasks to rsp
    for task in tasks:
        rsp.append({
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        })

    return jsonify(rsp), 200

def get_task_or_abort(task_id):
    try:
        task_id = int(task_id)
    except ValueError:
        rsp = {"msg": f"Invalid id: {task_id}"}
        abort(make_response(jsonify(rsp), 400))
    chosen_task = Task.query.get(task_id)
    if chosen_task is None:
        rsp = {"msg": f"Could not find task with id {task_id}"}
        abort(make_response(jsonify(rsp), 404))
    return chosen_task

@tasks_bp.route('/<task_id>', methods=['GET'])
def get_one_task(task_id):
    chosen_task = get_task_or_abort(task_id)

    rsp = { "task": 
        {
            "id": chosen_task.task_id,
            "title": chosen_task.title,
            "description": chosen_task.description,
            "is_complete": False
        }
    }
    return jsonify(rsp), 200

@tasks_bp.route("/<task_id>", methods=['PUT'])
def put_one_task(task_id):
    chosen_task = get_task_or_abort(task_id)
    new_task = validate_create_or_put()

    chosen_task.title = new_task.title
    chosen_task.description = new_task.description
    
    db.session.commit()    
    
    rsp = { "task": 
        {
            "id": chosen_task.task_id,
            "title": chosen_task.title,
            "description": chosen_task.description,
            "is_complete": False
        }
    }
    return jsonify(rsp), 200

@tasks_bp.route("/<task_id>", methods=['DELETE'])
def delete_one_task(task_id):
    chosen_task = get_task_or_abort(task_id)

    db.session.delete(chosen_task)
    db.session.commit()
    rsp = {
        "details": f'Task {task_id} "{chosen_task.title}" successfully deleted'
    }
    return jsonify(rsp), 200
