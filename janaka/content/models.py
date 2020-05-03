from datetime import datetime
from bson import ObjectId

from janaka.db import db

class Section:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def save(self): #Called when a section is created
        self.series = []
        return db.section.insert_one(self.json())

    def update(self, id): #Called to update a section
        db.section.update_one({'_id':id}, {'$set':self.json()})
        return True

    def json(self):
        out_dict = {
            'name':self.name,
            'description': self.description
        }
        if hasattr(self, 'series'):
            out_dict['series'] = self.series
        
        return(out_dict)

class Series: 
    #This shall not have a separate collection. But rather embedded in the series list of the section.
    def __init__(self, name, description, section_id):
        self.name = name 
        self.description = description
        self.section_id = section_id
    
    def save(self):
        self.blogs = []
        return db.series.insert_one(self.json())

    def update(self, id):
        db.series.update_one({'_id':id}, {'$set':self.json()})

    def json(self):
        out_dict = {
            'name':self.name,
            'description':self.description,
            'section_id':self.section_id
        }
        if hasattr(self, 'blogs'):
            out_dict['blogs'] = self.blogs
        return (out_dict)
        

class Blog:
    #Will have a separate collection blog in 
    def __init__(self, title, content, series_id):
        self.title = title
        self.content = content
        self.series_id = series_id

    def save(self):
        self.date_created = datetime.utcnow()
        self.date_last_edited = self.date_created
        return db.blog.insert_one(self.json())
    
    def update(self, id):
        self.date_last_edited = datetime.utcnow()
        db.blog.update_one({'_id':id}, {'$set':self.json()})
        return True

    def json(self):
        out_dict = {
            "title":self.title,
            "content":self.content,
            "series_id":self.series_id,
            "date_last_edited":self.date_last_edited,
        }
        #Update cases do not have date_created attribute.
        if hasattr(self, 'date_created'): 
            out_dict["date_created"] = self.date_created
        return (out_dict)