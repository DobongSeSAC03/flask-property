from flask import render_template
from . import parking_bp

@parking_bp.route('/', methods=['GET'])
def parking():
    return render_template('parking/parking.html')
