from flask import jsonify
from . import api_bp

@api_bp.route('/users')
def get_users():
    return jsonify([
        {'id': 1, 'username': 'user1'},
        {'id': 2, 'username': 'user2'}
    ])
