from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json

_app = Blueprint('_app', __name__)


@_app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    
    """

    ToDo: implement the picture upload route 

    """
    return render_template("index.html", user=current_user)

