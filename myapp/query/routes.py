from flask import render_template
from . import query_bp

@query_bp.route('/', methods=['GET'])
def query():
    return render_template('query/query.html')
