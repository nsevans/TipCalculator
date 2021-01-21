#########################################
#                                       #
#   Created By: Nicholas Evans          #
#   Project Start Date: May 19th, 2020  #
#   Backend Version 1.1.2               #
#                                       #
#########################################

from flask import Flask
flask_app = Flask(__name__)
import common.routes as routes
if __name__ == '__main__':

    routes.run()