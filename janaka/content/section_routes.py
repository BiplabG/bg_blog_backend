from flask import request, current_app
from flask_restful import Resource
from bson import ObjectId
from bson.json_util import dumps
from json import loads
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
import os

from . import content_api
from .models import Section, Series
from janaka.commons import helper_functions as hf
from janaka.db import db

@content_api.resource('/section')
class AllSections(Resource):
    def get(self):
        """Get request that handles getting overview of all sections."""
        try: 
            all_sections = db.section.find()
            return {
                "operation":"get_sections",
                "success":True,
                "message":"All sections fetched successfully.",
                "data": loads(dumps(all_sections))
            }
        except Exception as e:
            return hf.failure_message(operation="get_sections", msg=str(e))

    @jwt_required
    def post(self):
        """Post Request that handles creating new section."""
        try:
            data = request.get_json()
            hf.is_valid_data_keys(data=data, required_keys=['name', 'description'])
            section_instance = Section(name=data['name'], description=data['description'])
            saved_instance = section_instance.save()
            return {
                "operation":"create_section",
                "success":True,
                "message":"Section created successfully.",
                "id":loads(dumps(saved_instance.inserted_id)),
            }
        except Exception as e:
            return hf.failure_message(operation="create_section", msg=str(e))

@content_api.resource('/section/<string:section_id>')
class OneSection(Resource):
    def get(self, section_id):
        """Only get the section data."""
        try:
            section = db.section.find_one({'_id':ObjectId(section_id)})
            assert list(section), f"No data retrieved from DB, my friend. Perhaps there is no section with id {section_id}."
            return {
                "operation":"get_section",
                "success":True,
                "message":"Section fetched successfully.",
                "data":loads(dumps(section))
            }
        except Exception as e:
            return hf.failure_message(operation="get_section", msg=str(e))

    @jwt_required
    def put(self, section_id):
        """Post request that handles editing a section."""
        try:
            data = request.get_json()
            hf.is_valid_data_keys(data=data, required_keys=['name', 'description'])
            section_instance = Section(name=data['name'], description=data['description'])
            section_instance.update(ObjectId(section_id))
            return {
                'operation':'update_section',
                'success':True,
                'message':'Section updated successfully.'
            }
        except Exception as e:
            return hf.failure_message(operation="update_section", msg=str(e))
        
    @jwt_required
    def delete(self, section_id):
        """Delete request that deletes a section."""
        try:
            db.section.delete_one({'_id':ObjectId(section_id)})
            #TODO: Handle the deletion of section and propagate this to delete the associated blogs. 
            return {
                'operation':'delete_section',
                'success':True,
                'message':"Section deleted successfully"
            }
        except Exception as e:
            return hf.failure_message(operation="delete_section", msg=str(e))
    
@content_api.resource('/section/<string:section_id>/upload_image')
class SectionImage(Resource):
    def put(self, section_id):
        try:
            assert 'file' in request.files, "No file sent in the upload."
            file=request.files['file']
            assert file.filename!="", "No file selected."
            hf.is_file_allowed(file.filename)
            filename=secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'section/', filename))
            db.section.update({'_id':ObjectId(section_id)}, {'$set':{'image':filename}})
            return {
                'operation':'upload_section_image',
                'success':True,
                'message':"Section image uploaded successfully."
            }
        
        except Exception as e:
            return hf.failure_message(operation="upload_section_image", msg=str(e))
    