import os
import time
import webbrowser

from flask import request, make_response, jsonify, abort
from flask_cors import CORS
from flaskwebgui import FlaskUI
from werkzeug.utils import secure_filename

from common.Employees import Employees
from common.pdf_reader import PDFToText
import common.settings as settings
import common.event_logger as logger
import common.utils as utils
import common.keep_alive_scheduler as keep_alive_scheduler

from __main__ import flask_app
app = flask_app


@app.route("/", methods=['GET'])
def index():
    try:
        return app.send_static_file('html/index.html')
    except Exception as e:
        logger.logTraceback('Endpoint: \'/\'\n---'+str(e)+'---', e)
        abort(500, description=e)

@app.route('/generate', methods=['POST'])
def generate_data():
    
        logger.logEvent('Employee list requested...')
        logger.logEvent('Validating request...')
        #Check if file exists in request
        if 'file' not in request.files:
            return make_response(jsonify({'success': False, 'status': 'No File'}), 400)
        
        file = request.files['file']

        #Check if file is an empty string (invalid)
        if file.filename == '':
            return make_response(jsonify({'success': False, 'status': 'No File'}), 400)
        
        traceback_data = ""

        if file and utils.is_allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                traceback_data += "File Path: {}".format(file_path)
                #Save file to uploads folder
                file.save(file_path)

                #Generate report
                reader = PDFToText(file_path)
                employees = Employees()

                #Extract Data from pdf report
                extracting_start_time = time.time()
                pdf_string = reader.extract_pdf_text()
                logger.logEvent('Completed text extraction ({}s)'.format(round(time.time() - extracting_start_time, 4)))

                parsing_start_time = time.time()
                employees.generate_employee_info(pdf_string)
                logger.logEvent('Completed parsing ({}s)'.format(round(time.time()-parsing_start_time, 4)))
                
                logger.logEvent('Employee list response sent!')
                return make_response(jsonify({'success': True, 'response':{'employees': employees.employees}}), 200)
            except Exception as e:
                logger.logTraceback('Endpoint: \'/generate\'\n'+traceback_data+'\n---'+str(e)+'---', e)
                abort(500, description=e)
    


@app.route('/keepAlive', methods=['GET'])
def keep_alive():
    try:
        keep_alive_scheduler.job_started = True
        keep_alive_scheduler.resetWaitTime()
        return make_response(jsonify({'success':True}), 200)
    except Exception as e:
        logger.logTraceback('Endpoint: \'/keepAlive\'\n---'+str(e)+'---', e)
        abort(500, description=e)

@app.route('/settings', methods=['GET'])
def settings_controller():
    try:
        return app.send_static_file('html/settings.html')
    except Exception as e:
        logger.logTraceback('Endpoint: \'/settings\'\n---'+str(e)+'---', e)
        abort(500, description=e)
        

@app.route('/settings_get', methods=['GET'])
def get_settings():
    try:
        return make_response(jsonify({'success':True, 'settings':settings.user_settings['EMPLOYEE_NAMES']}), 200)
    except Exception as e:
        logger.logTraceback('Endpoint: \'/settings_get\'\n---'+str(e)+'---', e)
        abort(500, description="Request Settings: \n"+e)

@app.route('/settings_update', methods=['POST'])
def update_settings():
    try:

        names = request.json

        names_added = list(set(names) - set(settings.user_settings['EMPLOYEE_NAMES']))
        names_removed = list(set(settings.user_settings['EMPLOYEE_NAMES']) - set(names))

        settings.update_user_setting('EMPLOYEE_NAMES', names)
        settings.write_updated_settings_to_file()

        if names_added != []:
            logger.logEvent('Employee names added to EMPLOYEE_NAMES setting: '+str(', '.join('"'+n+'"' for n in names_added)))
        
        if names_removed != []:
            logger.logEvent('Employee names removed from EMPLOYEE_NAMES setting: '+str(', '.join('"'+n+'"' for n in names_removed)))
        
        return make_response(jsonify({'success': True}))
    except Exception as e:
        logger.logTraceback('Endpoint: \'/settings_update\'\nUpdating Employee Names: \n---'+str(e)+'---', e)
        abort(500, description=e)

@app.route('/createdby', methods=['GET'])
def creator():
    try:
        return  """
                    <link rel="shortcut icon" href="/static/favicon.ico">
                    <p>Created By: Nicholas Evans</p>
                    <p>Date Started: May 19th 2020</p>
                    <p>Date of Initial Release: June 27th 2020</p>
                    <p>Server Version: """+str(settings.app_settings['SERVER_VERSION'])+"""</p>
                    <p>Client Version: """+str(settings.app_settings['CLIENT_VERSION'])+"""</p>
                """
    except Exception as e:
        logger.logTraceback('Endpoint: \'/settings\'\n---'+str(e)+'---', e)
        abort(500, description=e)

@app.route('/changelog', methods=['GET'])
def changelog():
    try:

        formatted_data = ''
        with open(settings.app_settings["CHANGELOG_PATH"], 'r') as f:
            for line in f.readlines():
                formatted_data += "<pre>"+line+"</pre>"

        return  """
                    <link rel="shortcut icon" href="/static/favicon.ico">
                    """+formatted_data+"""

                """

    except Exception as e:
        logger.logTraceback('Endpoint: \'/settings\'\n---'+str(e)+'---', e)
        abort(500, description=e)

def run():

    app.config['UPLOAD_FOLDER'] = settings.app_settings['UPLOAD_PATH']
    CORS(app)

    webbrowser.open('http://localhost:'+str(settings.app_settings["SERVER_PORT"])+'/', new=1)

    keep_alive_scheduler.startJob()

    logger.logEvent('Server starting up...')

    # NOTE: Logging will fail if use_reloader is set to True, since
    # it creates 2 processes and they both try to write to and rename
    # the same file
    app.run(debug=settings.app_settings['DEBUG'], use_reloader=False)