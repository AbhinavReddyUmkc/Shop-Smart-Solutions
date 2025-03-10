from flask import Flask, jsonify
from risk_analysis import calculate_risk

app = Flask(__name__)

@app.route('/risk_score/<int:likelihood>/<int:impact>', methods=['GET'])
def get_risk_score(likelihood, impact):
    return jsonify({"risk_score": calculate_risk(likelihood, impact)})

if __name__ == '__main__':
    app.run(debug=True)
