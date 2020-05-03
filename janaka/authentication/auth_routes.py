from flask import request
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (create_access_token, create_refresh_token, 
                                jwt_refresh_token_required, jwt_required,
                                get_jwt_identity, get_raw_jwt)
from bson.json_util import dumps
from json import loads

from janaka.db import db
from janaka.authentication import auth_api 
from . import helper_functions as hf
from .models import User

@auth_api.resource('/register')
class Register(Resource):
    def post(self):
        try:
            user_count=db.user.count_documents({})
            assert user_count==0, "Admin user already exists."
            data = request.get_json()
            hf.is_valid_data_keys(data=data, required_keys=['email', 'password1', 'password2'])
            assert data['password1']==data['password2'], "Passwords do not match."
            user = User(email=data['email'], password=generate_password_hash(data['password1']))
            saved_instance = user.save()
            return {
                'operation':'register_admin',
                'success':True,
                '_id':loads(dumps(saved_instance.inserted_id)),
                'message':'Admin user registered successfully.'
            }

        except Exception as e:
            return hf.failure_message(operation='register_admin', msg=str(e))

@auth_api.resource('/login')
class Login(Resource):
    def post(self):
        try:
            data=request.get_json()
            hf.is_valid_data_keys(data=data, required_keys=['email', 'password'])
            user_instance = db.user.find_one({'email':data['email']})
            if check_password_hash(user_instance['password'], data['password']):
                access_token = create_access_token(identity=data['email'])
                refresh_token = create_refresh_token(identity=data['email'])
            else:
                raise Exception("Incorrect Password.")

            return {
                'operation':'login_admin',
                'success':True,
                'access_token':access_token,
                'refresh_token':refresh_token,
                'message':'Admin user logged in successfully.'
            }
        except Exception as e:
            return hf.failure_message(operation='login_admin', msg=str(e))

@auth_api.resource('/refresh')
class Refresh(Resource):
    @jwt_refresh_token_required
    def get(self):
        try:
            current_user = get_jwt_identity()
            return {
                'operation':'refresh_token',
                'success':True,
                'access_token':create_access_token(identity=current_user)
            }
        except Exception as e:
            return hf.failure_message(operation='refresh_token', msg=str(e))

@auth_api.resource('/logout')
class AccessLogOut(Resource):
    @jwt_required
    def get(self):
        try:
            jti = get_raw_jwt()['jti']
            db.revoked_tokens.insert_one({'jti':jti})
            return {
                'operation':'logout_admin',
                'success':True,
                'message':'Admin user logged out successfully.'
            }
        except Exception as e:
            return hf.failure_message(operation='logout_admin', msg=str(e))

@auth_api.resource('/refresh_revoke')
class RefreshLogOut(Resource):
    @jwt_refresh_token_required
    def get(self):
        try:
            jti = get_raw_jwt()['jti']
            db.revoked_tokens.insert_one({'jti':jti})
            return {
                'operation':'refresh_revoke',
                'success':True,
                'message':'Refresh token revoked successfully.'
            }
        except Exception as e:
            return hf.failure_message(operation='refresh_revoke', msg=str(e))


@auth_api.resource('/change_password')
class ChangePassword(Resource):
    @jwt_required
    def put(self):
        try:
            data=request.get_json()
            hf.is_valid_data_keys(data, ['new_password', 'current_password'])
            current_user=get_jwt_identity()
            user_instance=db.user.find_one({'email':current_user})
            assert check_password_hash(user_instance['password'], data['current_password']), "Incorrect current password provided."
            db.user.update_one({'email':current_user}, {'$set':{'password':generate_password_hash(data['new_password'])}})
            return {
                'operation':'change_password',
                'success':True,
                'message':'Password changed successfully.'
            }

        except Exception as e:
            return hf.failure_message(operation='change_password', msg=str(e))
