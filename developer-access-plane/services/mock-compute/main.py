from flask import Flask, request, jsonify
import threading
import time
import requests
import os
import uuid

app = Flask(__name__)

LAGO_API_URL = os.getenv("LAGO_API_URL", "http://lago-api:3000")
LAGO_API_KEY = os.getenv("LAGO_API_KEY", "hidden")

jobs = {}

def report_usage(job_id, user_id):
    while jobs.get(job_id) == "RUNNING":
        try:
            # Simulate 10 seconds of GPU usage
            payload = {
                "event": {
                    "transaction_id": str(uuid.uuid4()),
                    "code": "gpu_seconds",
                    "external_customer_id": user_id,
                    "properties": {
                        "seconds": 10
                    }
                }
            }
            headers = {
                "Authorization": f"Bearer {LAGO_API_KEY}",
                "Content-Type": "application/json"
            }
            # The Lago API endpoint for events is usually /api/v1/events
            # However, internal communication might differ. Assuming standard public API structure.
            response = requests.post(f"{LAGO_API_URL}/api/v1/events", json=payload, headers=headers)
            print(f"Reported usage for {job_id}: {response.status_code}")
        except Exception as e:
            print(f"Error reporting usage: {e}")
        
        time.sleep(10)

@app.route('/jobs/start', methods=['POST'])
def start_job():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    job_id = str(uuid.uuid4())
    jobs[job_id] = "RUNNING"
    
    thread = threading.Thread(target=report_usage, args=(job_id, user_id))
    thread.start()
    
    return jsonify({"job_id": job_id, "status": "STARTED"})

@app.route('/jobs/stop', methods=['POST'])
def stop_job():
    data = request.json
    job_id = data.get('job_id')
    if job_id in jobs:
        jobs[job_id] = "STOPPED"
        return jsonify({"job_id": job_id, "status": "STOPPED"})
    return jsonify({"error": "Job not found"}), 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
