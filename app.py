from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/tools/alert_doctor', methods=['POST'])
def alert_doctor():
    for tool_call in request.get_json()["message"]["toolCalls"]:
        print(tool_call)
        
    try:
        data = request.get_json()
        print(data)[
        
        return jsonify({"status": "success", "message": "Alert sent successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5555)
