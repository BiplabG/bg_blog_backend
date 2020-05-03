from flask import request
from flask_restful import Resource
from bson import ObjectId
from bson.json_util import dumps
from json import loads

from janaka.content import content_api
from janaka.db import db
from . import helper_functions as hf

blog_return_items = ['title', 'date_created'] #Fields to be sent for blog in the overview.

def get_blogs_from_series_id(series_id):
    series = db.series.find_one({'_id':ObjectId(series_id)})
    if 'blogs' in series:
        blogs_container = list(db.blog.find({'_id':{'$in':series['blogs']}}, blog_return_items))
        series['blogs'] = blogs_container
    return series

def get_series_from_section(section):
    series_container = [] #Array to contain series of a section
    if 'series' in section:
        for series_id in section['series']:
            series = get_blogs_from_series_id(series_id)
            series_container.append(series)
        section['series'] = series_container
    return section

@content_api.resource('/overview')
class Overview(Resource):
    """
    Get overview of the blogs. This returns a nice json for the website section, series and the blogs. 
    """
    def get(self):
        try:
            sections = list(db.section.find())
            for section in sections:
                section = get_series_from_section(section)
                
            return ({
                'operation':'get_overview',
                'success':True,
                'message':'Overview data fetched successfully.',
                'data':loads(dumps(sections))
            })
        except Exception as e:
            return hf.failure_message(operation='get_overview', msg=str(e))

@content_api.resource('/series_overview/<string:series_id>')
class SeriesOverview(Resource):
    def get(self, series_id):
        try:
            series = get_blogs_from_series_id(series_id)
            return ({
                'operation':'get_series_overview',
                'success':True,
                'message':'Series Overview data fetched successfully.',
                'data':loads(dumps(series))
            })
        except Exception as e:
            return hf.failure_message(operation='get_series_overview', msg=str(e))

