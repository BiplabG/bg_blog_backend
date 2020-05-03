from flask import request
from flask_restful import Resource
from bson import ObjectId
from bson.json_util import dumps
from json import loads
import traceback
from flask_jwt_extended import jwt_required

from . import content_api
from .models import Blog
from janaka.db import db
from janaka.commons import helper_functions as hf

@content_api.resource('/blog')
class AllBlogs(Resource):
    def get(self):
        """
        Get Request that gives all the blogs or blogs for whom ids are passed.
        For selected blogs, this method expects json data with ObjectIds in string. Format 
        {"ids":["...", "..."]}
        """
        try:
            data = request.get_json()
            if data and 'ids' in data:
                data['ids'] = [ObjectId(id) for id in data['ids']]
                blogs = db.blog.find({'_id': {'$in':data['ids']}})
            else:
                blogs = db.blog.find()
            return ({
                'operation':'get_blogs',
                'success':True,
                'data': loads(dumps(blogs)),
                'message':"Fetched multiple blogs successfully.",
            })
        except Exception as e:
            return hf.failure_message(operation='get_blogs', msg=str(e))

    @jwt_required
    def post(self):
        """Post Request that handles creating new blog."""
        try:
            data = request.get_json()
            hf.is_valid_data_keys(
                            data=data, 
                            required_keys=['title', 'content', 'series_id'])
            blog_instance = Blog(
                            title=data['title'], 
                            content=data['content'], 
                            series_id=ObjectId(data['series_id']))
            saved_instance = blog_instance.save()
            db.series.update_one(
                            {'_id':ObjectId(data['series_id'])},
                            {'$push':{'blogs':saved_instance.inserted_id}})
            return({
                'operation':'create_blog',
                'success':True,
                '_id':loads(dumps(saved_instance.inserted_id)),
                'message':"Blog created successfully."
            })

        except Exception as e:
            return hf.failure_message(operation='create_blog', msg=str(e))

@content_api.resource('/blog/<string:blog_id>')
class OneBlog(Resource):
    def get(self, blog_id):
        """Get request that handles getting a blog from its id."""
        try:
            blog = db.blog.find_one({'_id':ObjectId(blog_id)})
            assert list(blog), f"No data retrieved from DB, buddy. Perhaps there is no blog of id {blog_id}."
            return({
                'operation':'get_blog',
                'success':True,
                'data':loads(dumps(blog)),
                'message':"Blog fetched successfully."
            })

        except Exception as e:
            return hf.failure_message(operation='get_blog', msg=str(e))

    @jwt_required
    def put(self, blog_id):
        """Put request that handles editing/updating a blog."""
        try:
            data = request.get_json()
            hf.is_valid_data_keys(
                            data=data, 
                            required_keys=['title', 'content', 'series_id'])
            blog_old = db.blog.find_one({'_id':ObjectId(blog_id)})
            blog_instance = Blog(
                            title=data['title'], 
                            content=data['content'], 
                            series_id=ObjectId(data['series_id']))
            blog_instance.update(ObjectId(blog_id))
            
            if blog_old['series_id'] != data['series_id']:
                db.series.update_one(
                                {'_id':blog_old['series_id']},
                                {'$pull':{'blogs':ObjectId(blog_id)}})
                db.series.update_one(
                                {'_id':ObjectId(data['series_id'])},
                                {'$push':{'blogs':ObjectId(blog_id)}})

            return ({
                'operation':'update_blog',
                'success':True,
                'message':'Blog updated successfully.'
            })

        except Exception as e:
            traceback.print_exc()
            return hf.failure_message(operation='update_blog', msg=str(e))

    @jwt_required
    def delete(self, blog_id):
        """Delete request that deletes an existing blog."""
        try:
            #TODO: Handle the deletion in the series of the section where blog lies.
            db.blog.delete_one({'_id':ObjectId(blog_id)})
            return({
                'operation':'delete_blog',
                'success':True,
                'message':'Blog deleted successfully.'
            })

        except Exception as e:
            return hf.failure_message(operation='delete_blog', msg=str(e))
    