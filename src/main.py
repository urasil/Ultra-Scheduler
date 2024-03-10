from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime as dt

app = Flask(__name__)
CORS(app)



# task format = [[name, start_time, end_time], [name, start_time, end_time], ...]
@app.route('/api/task', methods=['GET'])
def send_task(task=[['Task 1', dt.time(9,0), dt.time(10,0)], ['Task 2', dt.time(11,0), dt.time(12,0)]]):
    # Additional validation for start_time and end_time can be added here

    processed_task = []
    for item in task:
        if not isinstance(item, list) or len(item) != 3:
            return jsonify({'error': 'Invalid task format. Each item should be a list with 3 elements.'}), 400

        name, start_time, end_time = item
        # Convert times to datetime objects for today's date
        today_date = dt.date.today()
        start_datetime = dt.datetime.combine(today_date, start_time).isoformat()
        end_datetime = dt.datetime.combine(today_date, end_time).isoformat()        
        processed_task.append([name, start_datetime, end_datetime])
    
    # If the task format is valid, send it to React
    return jsonify({'task': processed_task})


# Function to get todays date from web app needed
@app.route('/api/imported-task', methods=['POST'])
def receive_task(data):
    wakeUpTime = dt.datetime.strptime(data['getUpTime'], '%H:%M').time()
    sleepTime = dt.datetime.strptime(data['sleepTime'], '%H:%M').time()
    tasks = data['events']
    for task in tasks:
        name = task['summary']
        startTime = dt.datetime.fromisoformat(task['start']['dateTime']).time()
        endTime = dt.datetime.fromisoformat(task['start']['dateTime']).time()
        flexible = bool(task['flexible'])
        print(name, startTime, endTime, flexible)

    return




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')