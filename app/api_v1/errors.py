from . import v1
from .decorators import basic_auth, token_auth
from flask import make_response, jsonify

response = {'code': 0, 'message': ""}


@basic_auth.error_handler
def unauthorized():
    response['code'] = 1001
    response['message'] = "认证失败"
    return make_response(jsonify(response), 401)


@token_auth.error_handler
def token_expired():
    response['code'] = 1002
    response['message'] = "授权过期"
    return make_response(jsonify(response), 401)


@v1.app_errorhandler(401)
def authorize_failed(e):
    # Flask_RESTful Api 传的参数，exception类型
    response['code'] = 1001
    response['message'] = "认证失败"
    return make_response(jsonify(response), 401)


@v1.app_errorhandler(403)
def forbidden(e):
    response['code'] = 1003
    response['message'] = "禁止访问"
    return make_response(jsonify(response), 403)


@v1.app_errorhandler(404)
def not_found(e):
    response['code'] = 2001
    response['message'] = "资源不存在"
    return make_response(jsonify(response), 404)


@v1.app_errorhandler(400)
def bad_request(e):
    response['code'] = 2002
    response['message'] = "请求参数错误"
    return make_response(jsonify(response), 400)


@v1.app_errorhandler(500)
def server_error(e):
    response['code'] = 3001
    response['message'] = "服务器错误"
    return make_response(jsonify(response), 500)
