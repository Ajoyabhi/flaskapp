from textwrap import fill
import pandas as pd

from application import app, render_template, request, redirect, jsonify, make_response
import json
from werkzeug.utils import secure_filename

from flask import send_from_directory, current_app

import uuid # for public id
from  werkzeug.security import generate_password_hash, check_password_hash
import jwt



from . import db
from . import FormData, Progress, ProfilingData, DescretizationData, BinningColumns, UnivariateData, BivariateData, \
    ProcessStatus, SegmentData, WeightOfEvidence, ApplicationStats, TargetData, CountData, VariableLog,correlationTable,ChiSquareTable,ExecutiveData,User,Project

import os
import time

from functools import wraps

from datetime import  datetime, timedelta
import time

import requests

# importing logic class for different operation
from logic.profiling import Profile
from logic.descretization import Descretization
from logic.binning import BinningVariable
from logic.woe import WOE
from logic.univariate import Univariate
from logic.bivariate import Bivariate
from logic.segmentation import Segmentation
from logic.countplot import CountPlot
from logic.chisquare import ChiSquare
from logic.correlation import CORRELATION
from logic.imputation import Impute

app.config['SECRET_KEY']='004f2af45d3a4e161a7dd2d17fdae47f'



# =======================authentication=========================================

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       print(request.headers)
       if 'X-Access-Token' in request.headers:
           token = request.headers['X-Access-Token']
            
          
        
       if not token:
           return jsonify({'message': 'a valid token is missing'})
       try:
           data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
           current_user = User.query.filter_by(public_id=data['public_id']).first()
       except:
           return jsonify({'message': 'token is invalid'})
 
       return f(current_user, *args, **kwargs)
   return decorator



  
# User Database Route
# this route sends back list of users
@app.route('/user', methods =['GET'])
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    users = User.query.all()
    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        # appending the user data json
        # to the response list
        output.append({
            'public_id': user.public_id,
            'first_name' : user.first_name,
            'email' : user.email
        })
  
    return jsonify({'users': output})



# signup route
@app.route('/signup', methods =['POST'])
def signup():
    if request.method == 'POST':
        # creates a dictionary of the form data
        data = request.form
        print(data)

        # gets name, email and password
        first_name,last_name, email = data.get('first-name'),data.get('last-name'), data.get('email')
        password = data.get('password')

        # checking for existing user
        user = User.query\
            .filter_by(email = email)\
            .first()
        
        user_id = User.query.all()
        if not user:
            # database ORM object
            user = User(
                public_id = len(user_id)+1,
                first_name = first_name,
                last_name = last_name,
                email = email,
                password = generate_password_hash(password)
            )
            # insert user
            db.session.add(user)
            db.session.commit()

            return make_response('Successfully registered.', 201)
        else:
            # returns 202 if user already exists
            return make_response('User already exists. Please Log in.', 202)
        
@app.route('/signin', methods=['POST','GET'])
def signin():
    if request.method == 'GET':
         # creates dictionary of form data
        auth = request.args
        print(auth)

        if not auth or not auth.get('email') or not auth.get('password'):
            # returns 401 if any email or / and password is missing
            return make_response(
                'Could not verify',
                401,
                {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
            )

        user = User.query\
            .filter_by(email = auth.get('email'))\
            .first()

        if not user:
            # returns 401 if user does not exist
            return make_response(
                'Could not verify',
                401,
                {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
            )

        if check_password_hash(user.password, auth.get('password')):
            # generates the JWT Token
            token = jwt.encode({
                'public_id': user.public_id,
                'exp' : datetime.utcnow() + timedelta(minutes = 30)
            }, app.config['SECRET_KEY'],algorithm="HS256")
            
            print(token)
            
            return jsonify({'token' : token.decode('UTF-8')})
        # returns 403 if password is wrong
        return make_response(
            'Could not verify',
            403,
            {'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
        )
        
        

#authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('sign-in.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('sign-up.html')




# Create Restful API


@app.route('/form_post', methods=['GET', 'POST'])
@token_required
def form_post(current_user):
    if request.method == 'POST':
        print("into form post")
        print(current_user)
        project_name = request.form.get('project_name')
        project_details = request.form.get('project_details')

        # ------Selection field status
        is_bank_engagement = request.form.get('bank_engagement')

        if is_bank_engagement == '1':
            is_bank_engagement = True
        else:
            is_bank_engagement = False

        is_demographic = request.form.get('demographic')
        if is_demographic == '1':
            is_demographic = True
        else:
            is_demographic = False

        is_digital = request.form.get('digital')
        if is_digital == '1':
            is_digital = True
        else:
            is_digital = False

        is_financial_behaviour = request.form.get('financial_behaviour')
        if is_financial_behaviour == '1':
            is_financial_behaviour = True
        else:
            is_financial_behaviour = False
        

        is_loan_spending = request.form.get('loan_spendings')
        if is_loan_spending == '1':
            is_loan_spending = True
        else:
            is_loan_spending = False


        is_product_holding = request.form.get('product_holdings')
        if is_product_holding == '1':
            is_product_holding = True
        else:
            is_product_holding = False


        is_transactional = request.form.get('transactional')
        if is_transactional == '1':
            is_transactional = True
        else:
            is_transactional = False


        #------------Toggle data status

        is_target_available = request.form.get('is_target_available')
        
        if is_target_available == '1':
            is_target_available = True
        else:
            is_target_available = False
            
            
         #------------SB Toggle data status

        is_sb_file = request.form.get('sparkbeyond_switch')
        
        if is_sb_file == '1':
            is_sb_file = True
        else:
            is_sb_file = False
            
        #------------segmentation toggle

        is_segmentation = request.form.get('segmentation_switch')
        
        if is_segmentation == '1':
            is_segmentation = True
        else:
            is_segmentation = False
            
            
#         segment threshold
        lift_threshold = request.form.get('lift_threshold')
        proportion_threshold = request.form.get('proportion_threshold')
        


        operation_type = request.form.get('operation_type')

        #conditional target name 
        if is_target_available == True:
            target_name = 'Target'
        else:
            target_name = request.form.get('target_variable')

        upload_date = request.form.get('upload_date')
        upload_date = datetime.strptime(upload_date, '%Y-%m-%d')
        
        
        
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        
        f_sb = request.files['sb_file']
        print('fileeeeeeeeeeeeeeee Name........',f_sb.filename)
        if f_sb.filename=='':
            spark_beyond_file_path = 'Empty'
        else:
            f_sb.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f_sb.filename)))
            spark_beyond_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f_sb.filename))
        
        # rename customer id
        if is_target_available == True:
            df = pd.read_csv(file_path)
            df.columns = ['ucic_id','Target']
            #create file to map target
            target_file_path = os.path.join(app.config['UPLOAD_FOLDER'],'target_file.csv')
            df.to_csv(target_file_path,index=False)
            df = df[['ucic_id']]
            df.to_csv(file_path, index=False)
        else:    
            df = pd.read_csv(file_path)
            df.columns = ['ucic_id']
            df.to_csv(file_path, index=False)


        # truncate before updating
        db.session.execute('''DELETE FROM form_data''')
        db.session.commit()

        # commit changes to database
        form_data = FormData(project_name=project_name,project_details=project_details, operation_type=operation_type,upload_date = upload_date,is_bank_engagement = is_bank_engagement ,
                             is_demographic = is_demographic,is_digital = is_digital,is_product_holding = is_product_holding,is_transactional = is_transactional,is_target_available = is_target_available ,
                             is_financial_behaviour = is_financial_behaviour,is_loan_spending = is_loan_spending,
                             target_variable=target_name, file_location=file_path,sb_file_location=spark_beyond_file_path,is_sb_status = is_sb_file,is_segmentation=is_segmentation,lift_threshold=lift_threshold,proportion_thresold=proportion_threshold)
        db.session.add(form_data)
        db.session.commit()
        return redirect('tracker')
        # return {"message": "success done updating data"}, 202


# ------------------------------------------PROFILING CODE--------------------------------------------------------


@app.route('/profiling', methods=['GET', 'POST'])
def profiling():
    if request.method == 'GET':
        form_data = FormData.query.filter_by(id=1).first()
        file_location = form_data.file_location
        upload_date = form_data.upload_date
        is_target_available = form_data.is_target_available
        sb_file_location = form_data.sb_file_location
        is_sb_status = form_data.is_sb_status
        is_segmentation = form_data.is_segmentation
        

        db.session.execute('''DELETE FROM process_status''')
        db.session.commit()


        #adding main task according to operation type
        #query form data

        operation_type = form_data.operation_type
        
        if operation_type=='profiling':
            objects = [ProcessStatus(process_name="Data Mapping", process_status=0),
#             ProcessStatus(process_name="descretization", process_status=0),
            ProcessStatus(process_name="Count Plot", process_status=0)]
            db.session.add_all(objects)
            db.session.commit()

        if operation_type=='insight_generation':
            print('writing insight generation')
            if is_segmentation:
                objects = [ProcessStatus(process_name="Data Mapping", process_status=0),
                        ProcessStatus(process_name="Correlation", process_status=0),
                        ProcessStatus(process_name="Binning", process_status=0),
    #                     ProcessStatus(process_name="descretization", process_status=0),
                        ProcessStatus(process_name="Calculating WOE Score", process_status=0),
                        ProcessStatus(process_name="Chi-Squared Test", process_status=0),
                        ProcessStatus(process_name="Univariate", process_status=0),
                        ProcessStatus(process_name="Bivariate", process_status=0),
                        ProcessStatus(process_name="Segmentation", process_status=0)]
                db.session.add_all(objects)
                db.session.commit()
            else:
                objects = [ProcessStatus(process_name="Data Mapping", process_status=0),
                        ProcessStatus(process_name="Correlation", process_status=0),
                        ProcessStatus(process_name="Binning", process_status=0),
    #                     ProcessStatus(process_name="descretization", process_status=0),
                        ProcessStatus(process_name="Calculating WOE Score", process_status=0),
                        ProcessStatus(process_name="Chi-Squared Test", process_status=0),
                        ProcessStatus(process_name="Univariate", process_status=0),
                        ProcessStatus(process_name="Bivariate", process_status=0),]
                db.session.add_all(objects)
                db.session.commit()

        process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "Data Mapping").one()
        process_obj.process_status = 1
        db.session.commit()

        profile = Profile(file_location, upload_date,is_target_available,sb_file_location,is_sb_status)
        profile.mapping()

        
        # db.session.execute('''DELETE FROM progress''')
        # db.session.commit()
        return {"message": "success"}, 202


# -------------------------------DESCRETIZATION---------------------------------------------------------


@app.route('/descretization', methods=['GET', 'POST'])
def descretization():
    form_data = ProfilingData.query.filter_by(id=1).first()
    file_location = form_data.file_location

    categorize = Descretization(file_location)
    categorize.run()

#     process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "descretization").one()
#     process_obj.process_status = 1
#     db.session.commit()
    # db.session.execute('''DELETE FROM progress''')
    # db.session.commit()
    return {"message": "success"}, 202


# --------------------------------------------BINNNING OF VARIABLES-------------------------------------------------

@app.route('/binning', methods=['GET', 'POST'])
def binning():
    profile_data = ProfilingData.query.filter_by(id=1).first()
    file_location = profile_data.file_location

    form_data = FormData.query.filter_by(id=1).first()
    target_variable = form_data.target_variable

    descretization_data = DescretizationData.query.filter_by(categories="continuous_variable").first()
    continuous_variable = json.loads(descretization_data.column_values)
    binning_obj = BinningVariable(file_location, target_variable, continuous_variable)
    binning_obj.run()

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "Binning").one()
    process_obj.process_status = 1
    db.session.commit()
    # db.session.execute('''DELETE FROM progress''')
    # db.session.commit()
    return {"message": "success"}, 202


# -------------------------------------CALCULATE WEIGHT OF EVIDENCE ---------------------------------------------

@app.route('/weight_of_evidence', methods=['GET', 'POST'])
def weight_of_evidence():
    profile_data = ProfilingData.query.filter_by(id=1).first()
    file_location = profile_data.file_location

    form_data = FormData.query.filter_by(id=1).first()
    target_variable = form_data.target_variable

#     bin_data = BinningColumns.query.filter_by(id=1).first()
    descretization_data = DescretizationData.query.filter_by(categories="categorical_variable").first()
    bin_columns = json.loads(descretization_data.column_values)

    woe_obj = WOE(file_location, target_variable, bin_columns)
    woe_obj.iv_woe()

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "Calculating WOE Score").one()
    process_obj.process_status = 1
    db.session.commit()
    # db.session.execute('''DELETE FROM progress''')
    # db.session.commit()

    return {"message": "success"}, 202


# ---------------------------CALCULATING CHI SQUARE TEST---------------------------------
@app.route('/chi_square_test', methods=['GET', 'POST'])
def chi_square_test():
    profile_data = ProfilingData.query.filter_by(id=1).first()
    file_location = profile_data.file_location

    form_data = FormData.query.filter_by(id=1).first()
    target_variable = form_data.target_variable

    descretization_data = DescretizationData.query.filter_by(categories="categorical_variable").first()
    categorical_variable = json.loads(descretization_data.column_values)
    discrete_data = DescretizationData.query.filter_by(categories="discrete_variable").first()
    discrete_variable = json.loads(descretization_data.column_values)

    chisquare_obj = ChiSquare(file_location, target_variable, categorical_variable)
    chisquare_obj.run()
    
    impute_obj = Impute(file_location, target_variable, categorical_variable,discrete_variable)
    impute_obj.run()

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "Chi-Squared Test").one()
    process_obj.process_status = 1
    db.session.commit()
    # db.session.execute('''DELETE FROM progress''')
    # db.session.commit()

    return {"message": "success"}, 202


#calculating correlation
@app.route('/correlation', methods=['GET', 'POST'])
def correlation():
    profile_data = ProfilingData.query.filter_by(id=1).first()
    file_location = profile_data.file_location

    form_data = FormData.query.filter_by(id=1).first()
    target_variable = form_data.target_variable


    chisquare_obj = CORRELATION(file_location, target_variable)
    chisquare_obj.run()

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "Correlation").one()
    process_obj.process_status = 1
    db.session.commit()
    # db.session.execute('''DELETE FROM progress''')
    # db.session.commit()

    return {"message": "success"}, 202


@app.route('/univariate', methods=['GET', 'POST'])
def univariate():
    profile_data = ProfilingData.query.filter_by(id=1).first()
    file_location = profile_data.file_location

    form_data = FormData.query.filter_by(id=1).first()
    target_variable = form_data.target_variable

    descretization_data = DescretizationData.query.filter_by(categories="categorical_variable").first()
    categorical_variable = json.loads(descretization_data.column_values)

    univariate_plot = Univariate(file_location, target_variable, categorical_variable)
    univariate_plot.run()

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "Univariate").one()
    process_obj.process_status = 1
    db.session.commit()
    return {"message": "success"}, 202


@app.route('/bivariate', methods=['GET', 'POST'])
def bivariate():
    profile_data = ProfilingData.query.filter_by(id=1).first()
    file_location = profile_data.file_location

    form_data = FormData.query.filter_by(id=1).first()
    target_variable = form_data.target_variable
    is_segmentation = form_data.is_segmentation

    descretization_data = DescretizationData.query.filter_by(categories="categorical_variable").first()
    categorical_variable = json.loads(descretization_data.column_values)

    univariate_plot = Bivariate(file_location, target_variable, categorical_variable,is_segmentation)
    univariate_plot.run()

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "Bivariate").one()
    process_obj.process_status = 1
    db.session.commit()

    # db.session.execute('''DELETE FROM ProcessStatus''')
    # db.session.commit()
    return {"message": "success"}, 202

@app.route('/count_plot', methods=['GET', 'POST'])
def count_plot():
    profile_data = ProfilingData.query.filter_by(id=1).first()
    file_location = profile_data.file_location

    # form_data = FormData.query.filter_by(id=1).first()
    # target_variable = form_data.target_variable

    categorical_data = DescretizationData.query.filter_by(categories="categorical_variable").first()
    categorical_variable = json.loads(categorical_data.column_values)

    discrete_data = DescretizationData.query.filter_by(categories="discrete_variable").first()
    discrete_variable = json.loads(discrete_data.column_values)

    count_plot = CountPlot(file_location, categorical_variable,discrete_variable)
    count_plot.run()

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "Count Plot").one()
    process_obj.process_status = 1
    db.session.commit()

    # db.session.execute('''DELETE FROM ProcessStatus''')
    # db.session.commit()
    return {"message": "success"}, 202


@app.route('/segmentation', methods=['GET', 'POST'])
def segmentation():
    profile_data = ProfilingData.query.filter_by(id=1).first()
    file_location = profile_data.file_location

    form_data = FormData.query.filter_by(id=1).first()
    target_variable = form_data.target_variable
    lift_threshold = form_data.lift_threshold
    proportion_threshold = form_data.proportion_thresold

    descretization_data = DescretizationData.query.filter_by(categories="categorical_variable").first()
    categorical_variable = json.loads(descretization_data.column_values)

    segmentation_obj = Segmentation(file_location, target_variable, categorical_variable,lift_threshold,proportion_threshold)
    segmentation_obj.run()

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "Segmentation").one()
    process_obj.process_status = 1
    db.session.commit()
    return {"message": "success"}, 202


@app.route('/reporting', methods=['GET', 'POST'])
def reporting():
    return "reporting"


@app.route('/progress', methods=['GET', 'POST'])
def progress():
    if request.method == 'GET':
        task_done = []
        task_pending = []
        master_done = []
        master_pending = []
        percentage_subtask_complete = 0


        master = None
        status = None

        # profile_data = ProfilingData.query.filter_by(id=1).first()
        # file_location = profile_data.file_location
        # print(file_location)


        # process_master = ProcessStatus.query.filter_by(process_status=1).all()
        process_master = ProcessStatus.query.all()
        progress_data_all = Progress.query.all()
        
        form_data = FormData.query.all()
        operation_type = form_data[0].operation_type
        
        

        #update master data
        for master_task in process_master:
            # print('master_task.............',master_task.process_status)
            if master_task.process_status == 1:
                master_done.append(master_task.process_name)
            else:
                master_pending.append(master_task.process_name)


        if len(process_master) > 0:
            master = process_master[-1].process_name

        for data in progress_data_all:
            if data.task_status == '1':
                task_done.append(data.task_description)
            else:
                task_pending.append(data.task_description)

        if len(task_pending)>0:
            percentage_subtask_complete = len(task_done)/(len(task_done)+len(task_pending))*100
        print('percent .........',percentage_subtask_complete)


        status = {'task_done':task_done,'task_pending':task_pending,'master_done':master_done,'master_pending':master_pending,'percentage_subtask_complete':percentage_subtask_complete,'operation_type':operation_type}
        




        # print(len(progress_data_all))
        # if len(progress_data_all) > 0:
        #     for data in progress_data_all:
        #         if data.task_status == '1':
        #             task_done.append(data)
        #         else:
        #             task_pending.append(data)
        #     if len(task_pending) > 0:
        #         progress_data = task_pending[0];
        #         task_name = progress_data.task_name
        #         task_description = progress_data.task_description
        #         task_status = progress_data.task_status
        #         progress_finished = len(task_done)
        #         progress_pending = len(task_pending)
        #         status = {'status': 'processing', 'task_name': task_name, 'task_description': task_description,
        #                   'task_status': task_status, 'progress_finished': progress_finished,
        #                   'progress_pending': progress_pending, 'master_process': master}
        #     else:
        #         task_name = None
        #         task_description = None
        #         task_status = None
        #         progress_finished = len(task_done)
        #         progress_pending = len(task_pending)
        #         status = {'status': 'done', 'task_name': task_name, 'task_description': task_description,
        #                   'task_status': task_status, 'progress_finished': progress_finished,
        #                   'progress_pending': progress_pending, 'master_process': master, 'download_url': 'download_base'}
        # else:
        #     status = {'status': 'done', 'download_url': 'download_base'}

        # progress_data = Progress.query.filter_by(task_status=1).order_by(Progress.update_date.desc()).first()
        # if progress_data is None:
        #     return jsonify({'status': 'done'})
        #     # return jsonify("Done Processing")
        # else:
        #     task_name = progress_data.task_name
        #     task_description = progress_data.task_description
        #     task_status = progress_data.task_status
        #     # totalProcess = len(progress_data)
        #     print(progress_data)
        return jsonify(status)


@app.route('/download_base', methods=['GET', 'POST'])
def download():
    if request.method == 'GET':
        file_name = 'segment.csv'
        uploads = os.path.join(current_app.root_path, app.config['DOWNLOAD_FOLDER'])
        return send_from_directory(directory=uploads, filename=file_name)


# -------------------------------------------GET REQUEST TO PLOT DATA---------------------------------------------------
@app.route('/fetch_form', methods=['GET', 'POST'])
def fetch_form():
    if request.method == 'GET':
        form_data = FormData.query.all()
        response = jsonify(form_data[0])
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/univariate_plot', methods=['GET', 'POST'])
def univariate_plot():
    if request.method == 'GET':
        args = request.args
        strength_selected = args.get('strength')
        
        pagination_number = args.get('paginationNumber')
        
        
        
        if strength_selected == 'useless':
            stregth = 'Useless'
        if strength_selected == 'weak':
            stregth = 'Weak Predictor'
        if strength_selected == 'medium':
            stregth = 'Medium Predictor'
        if strength_selected == 'strong':
            stregth = 'Strong Predictor'
        if strength_selected == 'suspicious':
            stregth = 'Suspicious'    
        
        
        print('univariate arguments',args)
        plt_data = UnivariateData.query.filter_by(predictor_strength=stregth).paginate(page=int(pagination_number),per_page=30)
#         plt_data = UnivariateData.query.filter_by(predictor_strength=stregth).limit(10).all()
        print(plt_data)

        response = jsonify(plt_data.items)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/bivariate_plot', methods=['GET', 'POST'])
def bivariate_plot():
    if request.method == 'GET':
        args = request.args
        strength_selected = args.get('strength')
        
        pagination_number = args.get('paginationNumber')
        
        
       
        
        if strength_selected == 'useless':
            stregth = 'Useless'
        if strength_selected == 'weak':
            stregth = 'Weak Predictor'
        if strength_selected == 'medium':
            stregth = 'Medium Predictor'
        if strength_selected == 'strong':
            stregth = 'Strong Predictor'
        if strength_selected == 'suspicious':
            stregth = 'Suspicious'
            
            
        print('strngth value',stregth)
        
        plt_data = BivariateData.query.filter_by(predictor_strength=stregth).paginate(page=int(pagination_number),per_page=30)
        print(plt_data.items)
        
        
#         plt_data = BivariateData.query.filter_by(predictor_strength=stregth).limit(10).all()
        response = jsonify(plt_data.items)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@app.route('/segment_data', methods=['GET', 'POST'])
def segment_data():
    if request.method == 'GET':
        plt_data = SegmentData.query.order_by(SegmentData.segment_customer_count.desc()).limit(10).all()
        response = jsonify(plt_data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/woe', methods=['GET', 'POST'])
def woe():
    if request.method == 'GET':
#         plt_data = WeightOfEvidence.query.all()
        plt_data = WeightOfEvidence.query.order_by(WeightOfEvidence.information_value.desc()).limit(10).all()
        response = jsonify(plt_data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/application_stats', methods=['GET', 'POST'])
def application_stats():
    if request.method == 'GET':
        plt_data = ApplicationStats.query.all()
        response = jsonify(plt_data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/find_target_data', methods=['GET', 'POST'])
def find_target_data():
    if request.method == 'GET':
        plt_data = TargetData.query.all()
        response = jsonify(plt_data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@app.route('/process_status_data', methods=['GET', 'POST'])
def process_status_data():
    if request.method == 'GET':
        main_process = ProcessStatus.query.all()
        response = jsonify(main_process)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/count_plot_get', methods=['GET', 'POST'])
def count_plot_get():
    if request.method == 'GET':
        main_process = CountData.query.all()
        response = jsonify(main_process)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@app.route('/variable_log_get', methods=['GET', 'POST'])
def variable_log_get():
    if request.method == 'GET':
        main_process = VariableLog.query.all()
        response = jsonify(main_process)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@app.route('/correlation_get', methods=['GET', 'POST'])
def correlation_get():
    if request.method == 'GET':

#         main_process = correlationTable.query.all()
        main_process = correlationTable.query.order_by(correlationTable.correlation.desc()).limit(10).all()
        response = jsonify(main_process)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@app.route('/chisquare_get', methods=['GET', 'POST'])
def chisquare_get():
    if request.method == 'GET':
#         main_process = ChiSquareTable.query.all()
        main_process = ChiSquareTable.query.order_by(ChiSquareTable.p_value.desc()).limit(10).all()
        response = jsonify(main_process)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
@app.route('/executive_summary_get', methods=['GET', 'POST'])
def executive_summary_get():
    if request.method == 'GET':
#         main_process = ChiSquareTable.query.all()
        main_process = ExecutiveData.query.order_by(ExecutiveData.p_value.desc()).limit(10).all()
        response = jsonify(main_process)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
@app.route('/pagination_get', methods=['GET', 'POST'])
def pagination_get():
    if request.method == 'GET':
        univariate_record = UnivariateData.query.all()
        bivariate_record = BivariateData.query.all()
        print(len(univariate_record))
        print(len(bivariate_record))
        
        if len(univariate_record)>len(bivariate_record):
            total_records = len(univariate_record)
        else:
            total_records = len(bivariate_record)
        
        number_of_elements = total_records // 10
        
        response = jsonify(number_of_elements)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

# -------------------------------------------------PAGES----------------------------------------------






@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index_replace.html')


@app.route('/layout', methods=['GET', 'POST'])
def layout():
    return render_template('layout.html')


@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    return render_template('tracker_replace.html')


@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    return render_template('analytics.html')

@app.route('/profiling_analytics', methods=['GET', 'POST'])
def profiling_analytics():
    return render_template('profiling_analytics.html')

@app.route('/report_download', methods=['GET', 'POST'])
def report_download():
    return render_template('report.html')

@app.route('/executive_summary', methods=['GET', 'POST'])
def executive_summary():
    return render_template('executive_summary.html')

#--------------------------------------------fill data---------------------------------------

@app.route('/fill_target_data', methods=['GET', 'POST'])
def fill_target_data():
    db.session.execute('''DELETE FROM target_data''')
    db.session.commit()

    objects = [TargetData(target_variable="li_conversion"),
                TargetData(target_variable="gi_converion"),
                TargetData(target_variable="pl_conversion"),
                ]
    db.session.add_all(objects)
    db.session.commit()
    return {"message": "success"}, 202


# ----------------------------------------clear all data before execution-------------------------------
@app.route('/clear_all_data', methods=['GET', 'POST'])
def clear_all_data():
    
    for t in db.metadata.tables.keys():
        db.session.execute('''DELETE FROM %s'''%t)
    db.session.commit()
    return {"message": "success"}, 202
        


# -----------------------------------------Serialize execution-------------------------------------

#test cases
@app.route('/test1', methods=['GET', 'POST'])
def test1():
    #writing main process to database
    print('process started..........................')

    db.session.execute('''DELETE FROM process_status''')
    db.session.commit()
    

    objects = [ProcessStatus(process_name="profiling", process_status=0),
                   ProcessStatus(process_name="descretization", process_status=0),
                   ProcessStatus(process_name="binning", process_status=0),
                   ProcessStatus(process_name="woe", process_status=0),
                   ProcessStatus(process_name="univariate", process_status=0),
                   ProcessStatus(process_name="bivariate", process_status=0),
                   ProcessStatus(process_name="segmentation", process_status=0)]
    db.session.add_all(objects)
    db.session.commit()
    

    #clear profiling data table and progress
    db.session.execute('''DELETE FROM profiling_data''')
    # db.session.execute('''DELETE FROM progress''')
    db.session.commit()

    #add task to progress
    objects = [Progress(task_name="task1", task_description="mapping demographic", task_status=0),
                   Progress(task_name="task2", task_description="mapping transaction", task_status=0),
                   Progress(task_name="task3", task_description="mapping retiered", task_status=0)]
    db.session.add_all(objects)
    db.session.commit()

    time.sleep(5)
    #update task in progress table
    task_obj = db.session.query(Progress).filter(Progress.id == 1).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(15)

    task_obj = db.session.query(Progress).filter(Progress.id == 2).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(15)

    task_obj = db.session.query(Progress).filter(Progress.id == 3).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(10)

    #update main process status
    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "profiling").one()
    process_obj.process_status = 1
    db.session.commit()

    print('profiling done...........................................')
    

    # descretization
    db.session.execute('''DELETE FROM progress''')
    db.session.commit()

    #add task to progress
    objects = [Progress(task_name="task1", task_description="doing test1", task_status=0),
                   Progress(task_name="task2", task_description="doing test2", task_status=0),
                   Progress(task_name="task3", task_description="doing test3", task_status=0)]
    db.session.add_all(objects)
    db.session.commit()


    time.sleep(5)
    #update task in progress table
    task_obj = db.session.query(Progress).filter(Progress.id == 1).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(15)

    task_obj = db.session.query(Progress).filter(Progress.id == 2).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(15)

    task_obj = db.session.query(Progress).filter(Progress.id == 3).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(10)

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "descretization").one()
    process_obj.process_status = 1
    db.session.commit()
    print('descretization done...........................................')

    # ----------------------binning
    db.session.execute('''DELETE FROM progress''')
    db.session.commit()

    #add task to progress
    objects = [Progress(task_name="task1", task_description="doing binningtest1", task_status=0),
                   Progress(task_name="task2", task_description="doing binningtest2", task_status=0),
                   Progress(task_name="task3", task_description="doing binningtest3", task_status=0)]
    db.session.add_all(objects)
    db.session.commit()

 
    time.sleep(5)
    #update task in progress table
    task_obj = db.session.query(Progress).filter(Progress.id == 1).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(15)

    task_obj = db.session.query(Progress).filter(Progress.id == 2).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(15)

    task_obj = db.session.query(Progress).filter(Progress.id == 3).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(10)

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "binning").one()
    process_obj.process_status = 1
    db.session.commit()

    print('binning done...........................................')

    # ----------------------woe
    db.session.execute('''DELETE FROM progress''')
    db.session.commit()

    time.sleep(5)
    #add task to progress
    objects = [Progress(task_name="task1", task_description="doing woetest1", task_status=0),
                   Progress(task_name="task2", task_description="doing woetest2", task_status=0),
                   Progress(task_name="task3", task_description="doing woetest3", task_status=0)]
    db.session.add_all(objects)
    db.session.commit()


    time.sleep(5)
    #update task in progress table
    task_obj = db.session.query(Progress).filter(Progress.id == 1).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(15)

    task_obj = db.session.query(Progress).filter(Progress.id == 2).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(15)

    task_obj = db.session.query(Progress).filter(Progress.id == 3).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(10)

    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "woe").one()
    process_obj.process_status = 1
    db.session.commit()

    time.sleep(5)
    # ----------------------univariate
    db.session.execute('''DELETE FROM progress''')
    db.session.commit()

    #add task to progress
    objects = [Progress(task_name="task1", task_description="univariate process", task_status=0)
                   ]
    db.session.add_all(objects)
    db.session.commit()


    time.sleep(5)
    #update task in progress table
    task_obj = db.session.query(Progress).filter(Progress.id == 1).one()
    task_obj.task_status = 1
    db.session.commit()

    
    time.sleep(10)
   
    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "univariate").one()
    process_obj.process_status = 1
    db.session.commit()


    print('univariate...............done')

    # ----------------------bivariate
    db.session.execute('''DELETE FROM progress''')
    db.session.commit()
    time.sleep(5)
    #add task to progress
    objects = [Progress(task_name="task1", task_description="bivariate process", task_status=0)
                   ]
    db.session.add_all(objects)
    db.session.commit()



    #update task in progress table
    task_obj = db.session.query(Progress).filter(Progress.id == 1).one()
    task_obj.task_status = 1
    db.session.commit()

    
    time.sleep(10)
   
    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "bivariate").one()
    process_obj.process_status = 1
    db.session.commit()


    print('bivariate...............done')

    # ----------------------segmentation
    db.session.execute('''DELETE FROM progress''')
    db.session.commit()

    #add task to progress
    objects = [Progress(task_name="task1", task_description="segmentation process", task_status=0),
                Progress(task_name="task2", task_description="redirecting", task_status=0)]
    db.session.add_all(objects)
    db.session.commit()



    #update task in progress table
    task_obj = db.session.query(Progress).filter(Progress.id == 1).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(10)

    task_obj = db.session.query(Progress).filter(Progress.id == 2).one()
    task_obj.task_status = 1
    db.session.commit()

    time.sleep(10)
    

   
    process_obj = db.session.query(ProcessStatus).filter(ProcessStatus.process_name == "segmentation").one()
    process_obj.process_status = 1
    db.session.commit()


    print('bivariate...............done')

    
    

    return {"message": "success"}, 202







@app.route('/serialize_execution', methods=['GET', 'POST'])
def serialize_execution():

    #clear tables before execution
    db.session.execute('''DELETE FROM progress''')
    db.session.commit()
    
    # response = requests.get(app.config['BASE_URL']+"test1")
    # print(response)



    #check operation type

    #query form data
    form_data = FormData.query.all()
    operation_type = form_data[0].operation_type
    
    is_segmentation = form_data[0].is_segmentation
    
    if operation_type=='profiling':
        response = requests.get(app.config['BASE_URL']+"profiling")
        print('response.status_code',response.status_code)
        if response.status_code == 202:
            response2 = requests.get(app.config['BASE_URL']+"descretization")
            print('response2.status_code',response2.status_code)
            if response2.status_code == 202:
               response3 = requests.get(app.config['BASE_URL']+"count_plot")     
               print('response2.status_code',response3.status_code) 
    else:
        print('into insight generation')
        response = requests.get(app.config['BASE_URL']+"profiling")
        if response.status_code == 202:
            response2 = requests.get(app.config['BASE_URL']+"correlation")
            if response2.status_code == 202:
                response3 = requests.get(app.config['BASE_URL']+"descretization")
                print('descretization Dobne.....................')
                if response3.status_code == 202:
                    response4 = requests.get(app.config['BASE_URL']+"binning")
                    if response4.status_code == 202:
                        response5 = requests.get(app.config['BASE_URL']+"descretization")
                        print('descretization Dobne.....................')
                        if response5.status_code == 202:
                            response6 = requests.get(app.config['BASE_URL']+"weight_of_evidence")
                            if response6.status_code == 202:
                                response7 = requests.get(app.config['BASE_URL']+"descretization")
                                print('descretization Dobne.....................')
                                if response7.status_code == 202:
                                    response8 = requests.get(app.config['BASE_URL']+"chi_square_test")
                                    print('Chi square test Dobne.....................')
                                    if response8.status_code == 202:
                                        response9 = requests.get(app.config['BASE_URL']+"descretization")
                                        if response9.status_code == 202:
                                            response10 = requests.get(app.config['BASE_URL']+"univariate")
                                            if response10.status_code == 202:
#                                                 response11 = requests.get(app.config['BASE_URL']+"bivariate")
#                                                 if response11.status_code == 202:
                                                if is_segmentation == True:
                                                    print('starting segmentation')
                                                    response12 = requests.get(app.config['BASE_URL']+"segmentation")
                                                    if response12.status_code == 202:

                                                        return {"message": "success"}, 202
                                                else:
                                                    return {"message": "success"}, 202