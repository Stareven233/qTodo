from . import api
from flask_restful import Resource, reqparse, fields, marshal
from ..models import User
from flask import abort, g
from .. import db
from .decorators import auth
import copy

user_fields = {
    'id': fields.Integer,
    'username': fields.String
}
response_template = {'code': 0, 'message': "", 'data': {}}


class RegisterAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True, help='用户名不能为空', location='json')
        self.reqparse.add_argument('password', type=str, required=True, help='密码不能为空', location='json')
        super().__init__()

    def post(self):
        args = self.reqparse.parse_args()  # 返回Namespace，行为类似字典
        # print(type(args), args['password'], args.get('passwor', '79'))
        username = args['username']
        password = args['password']
        if User.query.filter_by(username=username).first():
            abort(400)
        user = User(username=username)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        response = copy.deepcopy(response_template)
        response['data']['count'] = 1
        response['data']['users'] = marshal(user, user_fields)
        return response, 201


class LoginAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True, help='用户名不能为空', location='json')
        self.reqparse.add_argument('password', type=str, required=True, help='密码不能为空', location='json')
        super().__init__()

    def post(self):
        args = self.reqparse.parse_args()
        username = args['username']
        password = args['password']
        user = User.query.filter_by(username=username).first()
        if not user or not user.verify_pw(password):
            abort(400)
        g.current_user = user
        response = copy.deepcopy(response_template)
        response.update({'data': marshal(user, user_fields)})
        return response, 200


class TokenAPI(Resource):
    decorators = [auth.login_required]

    def get(self):
        # 双令牌无感知刷新
        access_token = g.current_user.generate_auth_token(expiration=30*60)
        refresh_token = g.current_user.generate_auth_token(expiration=25*60*60)
        response = copy.deepcopy(response_template)
        response['data']['access_token'] = access_token.decode('ascii')
        response['data']['refresh_token'] = refresh_token.decode('ascii')
        return response, 200


class SetPasswordAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('password', type=str, required=True, help='密码不能为空', location='json')
        self.reqparse.add_argument('password2', type=str, required=True, help='新密码不能为空', location='json')
        super().__init__()

    def put(self):
        args = self.reqparse.parse_args()
        user = g.current_user
        if not user.verify_password(args['password']):
            abort(401)
        user.hash_password(args['password2'])
        db.session.add(user)
        db.session.commit()
        response = copy.deepcopy(response_template)
        response['data']['count'] = 1
        response['data']['users'] = marshal(user, user_fields)
        return response, 200

# class LogoutAPT(Resource):
#   登出由前端删除所持有的token实现


# api = Api(v1)
api.add_resource(RegisterAPI, '/user/register', endpoint='register')
# api.add_resource(LoginAPI, '/user/login', endpoint='login')
api.add_resource(TokenAPI, '/user/token', endpoint='token')
api.add_resource(SetPasswordAPI, '/user/setpassword', endpoint='setpassword')
