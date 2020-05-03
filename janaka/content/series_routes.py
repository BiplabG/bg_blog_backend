from flask_restful import Resource
from flask import request
from bson import ObjectId
from bson.json_util import dumps
from json import loads

from janaka.content import content_api
from janaka.db import db
from .models import Series
from . import helper_functions as hf

@content_api.resource('/series')
class AllSeries(Resource):
    def get(self):
        """Get all or multiple series data. For selected data specify 'ids' array in the sent json"""
        try:
            data = request.get_json()
            if data and 'ids' in data:
                data['ids'] = [ObjectId(id) for id in data['ids']]
                series = db.series.find({'_id':{'$in':data['ids']}})
            else:
                series = db.series.find()

            return {
                'operation':'get_series_multiple',
                'success':True,
                'message':'Multiple series fetched successfully.',
                'data':loads(dumps(series))
            }
        except Exception as e:
            return hf.failure_message(operation='get_series_multiple', msg=str(e))

    def post(self):
        """Create a new Series."""
        try:
            data = request.get_json() #Receives dictionary with keys name, description and section_id
            hf.is_valid_data_keys(
                            data=data, 
                            required_keys=['name', 'description', 'section_id'])
            series_instance = Series(
                                name=data['name'], 
                                description=data['description'],
                                section_id=ObjectId(data['section_id']))
            saved_instance = series_instance.save()
            db.section.update_one(
                            {'_id':ObjectId(data['section_id'])}, 
                            {'$push':{'series':saved_instance.inserted_id}})

            return{
                'operation':'create_series',
                'success':True,
                'message':'Series created successfully.',
                '_id':loads(dumps(saved_instance.inserted_id)),
            }

        except Exception as e:
            return hf.failure_message(operation='create_series', msg=str(e))

@content_api.resource('/series/<string:series_id>')
class OneSeries(Resource):
    def get(self, series_id):
        try:
            series = db.series.find_one({'_id':ObjectId(series_id)})
            assert list(series), f"No data retrieved from DB, my friend. Perhaps there is no section with id {series_id}."
            return {
                'operation':'get_series',
                'success':True,
                'message':'Series fetched successfully.',
                'data':loads(dumps(series))
            }

        except Exception as e:
            return hf.failure_message(operation='get_series', msg=str(e))

    def put(self, series_id):
        try:
            data = request.get_json()
            hf.is_valid_data_keys(
                        data=data, 
                        required_keys=['name', 'description', 'section_id'])
            series_old = db.series.find_one({'_id':ObjectId(series_id)})
            series_instance = Series(
                        name=data['name'], 
                        description=data['description'], 
                        section_id=ObjectId(data['section_id']))
            series_instance.update(ObjectId(series_id))

            if data['section_id'] != str(series_old['section_id']):
                #Remove the series_id from the old section and update it to the new section
                db.section.update_one(
                                {'_id':series_old['section_id']}, 
                                {'$pull':{'series':ObjectId(series_id)}})
                db.section.update_one(
                                {'_id':ObjectId(data['section_id'])},
                                {'$push':{'series':ObjectId(series_id)}})

            return {
                'operation':'update_series',
                'success':True,
                'message':'Series updated successfully.'
            }

        except Exception as e:
            return hf.failure_message(operation='update_series', msg=str(e))

    def delete(self, series_id):
        try:
            series_old = db.series.find_one({'_id':ObjectId(series_id)})
            db.section.update_one(
                            {'_id':series_old['section_id']},
                            {'$pull':{'series':ObjectId(series_id)}})

            db.series.delete_one({'_id':ObjectId(series_id)})
            return {
                'operation':'delete_series',
                'success':True,
                'message':'Series deleted successfully.'
            }
        except Exception as e:
            return hf.failure_message(operation='delete_series', msg=str(e))