from . import api
from ..models import Task
from flask_restful import Resource, reqparse, fields, marshal
from .decorators import auth
from flask import g, abort
from .. import db
from datetime import datetime
import copy


task_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'done': fields.Boolean,
    'date': fields.DateTime(dt_format='iso8601'),  # "2020-02-25T22:31:33"
    'deadline': fields.DateTime(dt_format='iso8601'),
    'url': fields.Url('.task', absolute=True)
    # field.Url 要求get(self, id)，<int:id>的参数名与数据库一致
}
response_template = {'code': 0, 'message': "", 'data': {}}


class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('state', type=int, required=False, location='args')
        super().__init__()  # "2020-02-25 14:19:45"

    def get(self):  # 获取所有事项
        args = self.reqparse.parse_args()
        tasks = g.current_user.task

        if args['state'] is not None:  # 1表示done, 0表示pending
            tasks = tasks.filter_by(done=bool(args['state']))
        tasks = tasks.all()

        # response['data'] = [marshal(tasks, task_fields), len(tasks)][args['content'] == 'count']
        response = copy.deepcopy(response_template)
        response['data']['count'] = len(tasks)
        response['data']['tasks'] = marshal(tasks, task_fields)
        return response, 200

    def post(self):  # 创建一条新事项
        self.reqparse.add_argument('text', type=str, required=True, location='json')
        self.reqparse.add_argument('deadline', type=str, required=True, location='json')
        args = self.reqparse.parse_args()
        try:
            datetime.strptime(args['deadline'], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            abort(400)

        task = Task(text=args['text'], deadline=args['deadline'], author=g.current_user)
        db.session.add(task)
        db.session.commit()
        response = copy.deepcopy(response_template)
        response['data']['count'] = 1
        response['data']['tasks'] = marshal(task, task_fields)
        return response, 201

    def put(self):  # 修改所有事项
        self.reqparse.add_argument('done', type=bool, required=True, location='json')
        args = self.reqparse.parse_args()
        tasks = g.current_user.task

        if args['state'] is not None:
            tasks = tasks.filter_by(done=bool(args['state']))
        tasks = tasks.all()
        tasks = list(map(lambda t: t.alter(done=args['done']), tasks))  # 全体修改只允许done

        db.session.add_all(tasks)
        db.session.commit()
        response = copy.deepcopy(response_template)
        response['data']['count'] = len(tasks)
        response['data']['tasks'] = marshal(tasks, task_fields)
        return response, 200

    def delete(self):
        args = self.reqparse.parse_args()
        tasks = g.current_user.task

        if args['state'] is not None:  # 1表示done, 0表示pending
            tasks = tasks.filter_by(done=bool(args['state']))
        tasks = tasks.all()

        for t in tasks:
            db.session.delete(t)
        db.session.commit()
        response = copy.deepcopy(response_template)
        response['data']['count'] = len(tasks)
        response['data']['tasks'] = marshal(tasks, task_fields)
        return response, 200


class TaskAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super().__init__()

    def get(self, id):
        # task = g.current_user.task.filter_by(id=tid).first_or_404()
        task = Task.query.filter_by(id=id).first_or_404()
        if task.author_id != g.current_user.id:
            abort(403)
        response = copy.deepcopy(response_template)
        response['data']['count'] = 1
        response['data']['tasks'] = marshal(task, task_fields)
        return response, 200

    def put(self, id):
        self.reqparse.add_argument('done', type=bool, required=False, location='json')
        self.reqparse.add_argument('text', type=str, required=False, location='json')
        self.reqparse.add_argument('deadline', type=str, required=False, location='json')
        args = self.reqparse.parse_args()
        task = Task.query.filter_by(id=id).first_or_404()
        if task.author_id != g.current_user.id:
            abort(403)
        task = task.alter(**args)

        db.session.add(task)
        db.session.commit()
        response = copy.deepcopy(response_template)
        response['data']['count'] = 1
        response['data']['tasks'] = marshal(task, task_fields)
        return response, 200

    def delete(self, id):
        task = Task.query.filter_by(id=id).first_or_404()
        if task.author_id != g.current_user.id:
            abort(403)
        db.session.delete(task)
        db.session.commit()
        response = copy.deepcopy(response_template)
        response['data']['count'] = 1
        response['data']['tasks'] = marshal(task, task_fields)
        return response, 200


# api = Api(v1)
api.add_resource(TaskListAPI, '/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/tasks/<int:id>', endpoint='task')
