from flask import Flask, render_template, request, redirect, flash, jsonify, make_response
import json

# database repo import
import os
from flask_sqlalchemy import SQLAlchemy
import datetime
from dataclasses import dataclass
from flask_login import UserMixin
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import InputRequired, Length, ValidationError

# from marshmallow import fields
# from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

app = Flask(__name__)

app.config['DEBUG'] = True


# configuring database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_database.sqlite3'
db = SQLAlchemy(app)
# app.config['SECRET_KEY'] = 'thisisasecretkey'


# -----------------------------------Defining Model------------------------------------------------
# create user table
# class UserData(db.Model):
#     __tablename__ = "user"
#     id = db.Column('ID', db.Integer, primary_key=True)
#     user_name = db.Column(db.String)
#
#     def create(self):
#         db.session.add(self)
#         db.session.commit()
#         return self
#
#     def __init__(self, user_name):
#         self.user_name = completion_status
#
#     def __repr__(self):
#         return f"{self.id}"

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    public_id=db.Column(db.Integer,nullable=True,unique=True) 
    first_name=db.Column(db.String(50), nullable=True, unique=True)
    last_name=db.Column(db.String(50), nullable=True, unique=True)
    email=db.Column(db.String(70), nullable=True, unique=True)
    password=db.Column(db.String(80), nullable=True)


class Project(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    public_id=db.Column(db.String(50),nullable=True,unique=True) 
    project_id=db.Column(db.String(50),nullable=True,unique=True) 


@dataclass
class FormData(db.Model):
    id: int
    public_id:int
    project_id:str
    project_name: str
    project_details: str
    project_name: str
    project_details: str
    operation_type: str
    is_bank_engagement: bool
    is_demographic: bool
    is_digital: bool
    is_financial_behaviour: bool
    is_loan_spending: bool
    is_product_holding: bool
    is_transactional: bool
    target_variable: str
    upload_date: datetime
    file_location: str
    sb_file_location: str
    is_sb_status: bool
    is_segmentation: bool
    lift_threshold: str
    proportion_thresold: str
        
        

    id = db.Column(db.Integer, primary_key=True)
    public_id=db.Column(db.Integer,nullable=True,unique=True) 
    project_id=db.Column(db.String(50),nullable=True,unique=True)
    project_name = db.Column(db.String, nullable=False)
    project_details = db.Column(db.String, nullable=False)
    operation_type = db.Column(db.String, nullable=False)
    is_bank_engagement = db.Column(db.Boolean, nullable=False)
    is_demographic = db.Column(db.Boolean, nullable=False)
    is_digital = db.Column(db.Boolean, nullable=False)
    is_financial_behaviour = db.Column(db.Boolean, nullable=False)
    is_loan_spending = db.Column(db.Boolean, nullable=False)
    is_product_holding = db.Column(db.Boolean, nullable=False)
    is_transactional = db.Column(db.Boolean, nullable=False)
    is_target_available = db.Column(db.Boolean, nullable=False)
    is_sb_status = db.Column(db.Boolean, nullable=False)
    is_segmentation = db.Column(db.Boolean, nullable=False)


    target_variable = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.DATE, nullable=False)
    file_location = db.Column(db.String, nullable=False)
    sb_file_location = db.Column(db.String, nullable=False)
    lift_threshold = db.Column(db.String, nullable=False)
    proportion_thresold = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id


class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String, nullable=False)
    task_description = db.Column(db.String, nullable=False)
    task_status = db.Column(db.String, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


@dataclass
class ProfilingData(db.Model):
    id: int
    file_location: str
    update_date: datetime

    id = db.Column(db.Integer, primary_key=True)
    file_location = db.Column(db.String, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


class DescretizationData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categories = db.Column(db.String, nullable=False)
    column_values = db.Column(db.String, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


class BinningColumns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bin_name = db.Column(db.String, nullable=False)
    bin_column_name = db.Column(db.String, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


@dataclass
class WeightOfEvidence(db.Model):
    id: int
    variable_name: str
    information_value: str

    id = db.Column(db.Integer, primary_key=True)
    variable_name = db.Column(db.String, nullable=False)
    information_value = db.Column(db.String, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


@dataclass
class UnivariateData(db.Model):
    id: int
    plot_title: str
    plot_data: str
    plot_narrative: str
    predictor_strength: str

    id = db.Column(db.Integer, primary_key=True)
    plot_title = db.Column(db.String, nullable=False)
    plot_data = db.Column(db.String, nullable=False)
    plot_narrative = db.Column(db.String, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    predictor_strength = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id


@dataclass
class BivariateData(db.Model):
    id: int
    plot_title: str
    plot_data: str
    plot_narrative: str
    predictor_strength: str

    id = db.Column(db.Integer, primary_key=True)
    plot_title = db.Column(db.String, nullable=False)
    plot_data = db.Column(db.String, nullable=False)
    plot_narrative = db.Column(db.String, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    predictor_strength = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id


@dataclass
class SegmentData(db.Model):
    id: int
    segment_name: str
    segment_lift: str
    segment_conversion_rate: str
    segment_customer: str
    segment_customer_count: str
    segment_bau: str

    id = db.Column(db.Integer, primary_key=True)
#     segment_name = db.Column(db.String, nullable=False)
#     segment_customer = db.Column(db.String, nullable=False)
#     segment_conversion = db.Column(db.String, nullable=False)
#     segment_narrative = db.Column(db.String, nullable=False)

    segment_name = db.Column(db.String, nullable=False)
    segment_lift = db.Column(db.String, nullable=False)
    segment_conversion_rate = db.Column(db.String, nullable=False)
    segment_customer = db.Column(db.String, nullable=False)
    segment_customer_count = db.Column(db.String, nullable=False)
    segment_bau = db.Column(db.String, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


@dataclass
class ProcessStatus(db.Model):
    id: int
    process_name: str
    process_status: int

    id = db.Column(db.Integer, primary_key=True)
    process_name = db.Column(db.String, nullable=False)
    process_status = db.Column(db.Integer, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


@dataclass
class ApplicationStats(db.Model):
    id: int
    customer_base: str
    variable_mapped: int
    time_taken: int

    id = db.Column(db.Integer, primary_key=True)
    customer_base = db.Column(db.String, nullable=False)
    variable_mapped = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id


@dataclass
class CountData(db.Model):
    id: int
    title: str
    plot_data: str

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    plot_data = db.Column(db.String, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id

@dataclass
class VariableLog(db.Model):
    id: int
    variable_name: str
    
    
    id = db.Column(db.Integer, primary_key=True)
    variable_name = db.Column(db.String, nullable=False)
    

    def __repr__(self):
        return '<User %r>' % self.id

@dataclass
class ChiSquareTable(db.Model):
    id: int
    variable: str
    p_value: str
    
    
    id = db.Column(db.Integer, primary_key=True)
    variable = db.Column(db.String, nullable=False)
    p_value = db.Column(db.String, nullable=False)
    
    

    def __repr__(self):
        return '<User %r>' % self.id

@dataclass
class correlationTable(db.Model):
    id: int
    variable_name: str
    correlation:str
    
    id = db.Column(db.Integer, primary_key=True)
    variable_name = db.Column(db.String, nullable=False)
    correlation = db.Column(db.String, nullable=False)
    

    def __repr__(self):
        return '<User %r>' % self.id

#-----data to fill targer field------
@dataclass
class TargetData(db.Model):
    id: int
    target_variable: str
    

    id = db.Column(db.Integer, primary_key=True)
    target_variable = db.Column(db.String, nullable=False)
    

    def __repr__(self):
        return '<User %r>' % self.id
    
@dataclass
class ExecutiveData(db.Model):
    id: int
    narrative: str
    

    id = db.Column(db.Integer, primary_key=True)
    narrative = db.Column(db.String, nullable=False)
    

    def __repr__(self):
        return '<User %r>' % self.id


db.create_all()

from application import routes

# Static folder configuration
UPLOAD_FOLDER = 'application/upload_folder'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DOWNLOAD_FOLDER = 'final_base'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

BASE_URL = 'http://10.226.70.165:50000/'
app.config['BASE_URL'] = BASE_URL