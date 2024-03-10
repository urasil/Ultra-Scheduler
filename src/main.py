from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime as dt
from backend.Task import Task
from backend.TaskScheduler import TaskScheduler

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
        name = item[0]
        start_time = item[1].isoformat()
        end_time = item[2].isoformat()
        processed_task.append({'summary': name, 'start': {'dateTime': start_time}, 'end': {'dateTime': end_time}})
    
    processed_task.sort(key=lambda x: x['start']['dateTime'])

    print(2, {'events': processed_task})
    # return jsonify({'events': processed_task})
    # If the task format is valid, send it to React
    return jsonify({'events': processed_task})


# Function to get todays date from web app needed
# summary(STR), start_time(ISO), end_time(ISO), flexible(BOOL)
@app.route('/api/imported-task', methods=['POST'])
def receive_task():
    data = request.get_json()
    wakeUpTime = dt.datetime.strptime(data['getUpTime'], '%H:%M').time()
    sleepTime = dt.datetime.strptime(data['sleepTime'], '%H:%M').time()
    tasks = data['events']
    taskList = []
    for task in tasks:
        name = task['summary']
        date = dt.datetime.fromisoformat(task['start']['dateTime']).date()
        startTime = dt.datetime.fromisoformat(task['start']['dateTime'])
        endTime = dt.datetime.fromisoformat(task['end']['dateTime'])
        flexible = task['flexible']
        print(name, startTime, endTime, flexible)
        taskList.append(Task(name, startTime, endTime, flexible))
    
    scheduler = TaskScheduler(taskList, wakeUpTime, sleepTime)
    processed_data = scheduler.find_best_combination()
    print(1, processed_data)

    return send_task(processed_data)
    # return jsonify({'task': processed_data})




if __name__ == '__main__':
    # receive_task({'getUpTime': '08:00', 'sleepTime': '23:00', 'events': [{'summary': '', 'start': {'dateTime': '2021-08-01T04:45:00:00'}, 'end': {'dateTime' : '2021-08-01T07:30:00'}, 'flexible': 'True'}, {'summary': 'tmrw shit', 'start': {'dateTime': '2021-08-01T17:15:00'}, 'end': {'dateTime' : '2021-08-01T23:45:00'}, 'flexible': 'True'}]})
    app.run(debug=True, host='0.0.0.0')