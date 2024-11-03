from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import json
from filelock import FileLock
from patient_alert import PatientAlert

load_dotenv()

app = Flask(__name__)

def read_alerts(filename="alerts.json"):
   try:
       with FileLock(filename + ".lock"):
           with open(filename, "r") as f:
               data = json.load(f)
               return [PatientAlert(**alert) for alert in data]
   except FileNotFoundError:
       return []

def write_alerts(alerts, filename="alerts.json"):
   with FileLock(filename + ".lock"):
       with open(filename, "w") as f:
           # Convert PatientAlert objects to dictionaries
           alerts_json = [{"priority": a.priority, "reason": a.reason, "excerpt": a.excerpt} 
                        for a in alerts]
           json.dump(alerts_json, f, indent=2)

@app.route('/tools/alert_doctor', methods=['POST'])
def alert_doctor():
   try:
       data = request.get_json()
       print(data)
       results = []
       for tool_call in request.get_json()["message"]["toolCalls"]:
           print(tool_call)
           id = tool_call["id"]
           patient_note = tool_call["function"]["arguments"]["patient_note"]
           alert_reason = tool_call["function"]["arguments"]["alert_reason"]
           alert_priority = tool_call["function"]["arguments"]["alert_priority"]
           
           # Create new alert
           new_alert = PatientAlert(alert_priority, alert_reason, patient_note)
           
           # Read existing alerts
           existing_alerts = read_alerts()
           
           # Add new alert
           existing_alerts.append(new_alert)
           
           # Write back all alerts
           write_alerts(existing_alerts)
           
           print(new_alert)
           results.append({"toolCallId": id, "result": "The doctor has been alerted"})
       print(jsonify({"results":results}))
       return jsonify({"results":results}), 200
   except Exception as e:
       print(e)
       return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
   app.run(debug=True, port=5555)