from flask import render_template
from . import predict_bp

@predict_bp.route('/', methods=['GET'])
def predict():
    return render_template('predict/predict.html')
