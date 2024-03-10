import openai
from UltradianRhytm import UltradianRhythm
from Task import Task
import datetime as dt
import copy

class TaskScheduler:
    def __init__(self, tasks, wakeup, sleep): 
       api_key = "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"
       self.client = openai.Client(
           api_key=api_key
       )
       self.tasks = []  # List of tasks with attributes like name, duration, importance, flexibility
       for task in tasks:
           newTask = Task(task.name, task.startTime, task.endTime, task.flexibility)
           self.tasks.append(newTask)
       self.productivity_periods = UltradianRhythm.calculate_ultradian_intervals()  # Use default values for now
       self.wakeup, self.sleep = self.convert_wakeup_sleep_to_minutes(wakeup, sleep)
       self.free_times = [] 

    def convert_wakeup_sleep_to_minutes(self, wakeup, sleep):
        wakeup = int(wakeup.hour) * 60 + int(wakeup.minute)
        sleep = int(sleep.hour) * 60 + int(sleep.minute)
        return wakeup, sleep

    def assign_task_importance(self, tasks):
        prompt = "Rate the importance of the following tasks on a scale of 1 to 10. All responses must be of the form = [task number]. Task: [task name] Importance rating:[integer rating]. If no names are provided, give random numbers for [integer rating]\n"
        userPrompt = ""
        for i, taskObject in enumerate(tasks, start=1):
            userPrompt += f"{i}. Task: {taskObject.name}\nImportance rating:\n"
        
        response = self.client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": userPrompt
            }
        ],
        model="gpt-3.5-turbo"
    )
    
        # Extract and return the generated ratings
        splittedResponse = response.choices[0].message.content.split("\n")
        #print(splittedResponse)
        betterResponse = []
        for resp in splittedResponse:
            betterResponse.append(resp.split(":")[-1].strip())

        for i in range(len(self.tasks)):
            self.tasks[i].importance = betterResponse[i]

    def prioritize_tasks(self):
       # Sort tasks by importance and/or deadline
       self.tasks.sort(key=lambda x: (x.importance))
   
    """ def every_way_of_fitting_to_schedule(self):
        # Generate all possible combinations of tasks that fit into the schedule
        free_times = self.find_free_times()
        flexible_tasks = [task for task in self.tasks if task.flexibility]
        all_combinations = []

        for perm in permutations(flexible_tasks):
            current_combination = []
            free_time_index = 0
            current_time = free_times[free_time_index][0]
            for task in perm:
                # Convert task start and end times to datetime.datetime objects with a dummy date      
                task_duration_minutes = (task.endTime - task.startTime)
                free_time_duration_minutes = (free_times[free_time_index][1] - free_times[free_time_index][0])
                if free_time_duration_minutes >= task_duration_minutes:
                    free_time_duration_minutes -= task_duration_minutes
                    current_combination.append([task.name, current_time, current_time + task_duration_minutes])  # Append tuple to combination
                    current_time += task_duration_minutes + 5  # Add a 5-minute buffer between tasks
                    if len(current_combination) == len(perm):
                        all_combinations.append(current_combination)
                else:
                    if free_time_index + 1 < len(free_times):
                        free_time_index += 1
                        current_time = free_times[free_time_index][0]
                    else:
                        break

        return all_combinations """      


    def every_way_of_fitting_to_schedule(self):
        # Generate all possible combinations of tasks that fit into the schedule
        free_times = self.find_free_times()
        flexible_tasks = [task for task in self.tasks if task.flexibility]
        all_combinations = []

        # Define a recursive function to generate combinations
        def generate_combinations(current_index, current_combination, remaining_tasks, free_times):
            if current_index == len(free_times) or remaining_tasks == []:
                # All free time slots have been considered, add the current combination to the list
                all_combinations.append(current_combination)
                return
            
            # Try adding each task to the current free time slot
            for task in remaining_tasks:
                task_duration_minutes = task.endTime - task.startTime
                free_time_start, free_time_end = free_times[current_index]
                for start in range(free_time_start, free_time_end - task_duration_minutes + 1, 20):
                    if start + task_duration_minutes <= free_time_end:
                        # The task fits into the current free time slot
                        new_remaining_tasks = [t for t in remaining_tasks if t != task]
                        new_free_times = free_times[:]  
                        new_free_times[current_index] = [start + task_duration_minutes + 5, free_time_end] 
                        new_combination = current_combination + [(task, start, start + task_duration_minutes)]
                        generate_combinations(current_index, new_combination, new_remaining_tasks, new_free_times)
                    else:
                        # The task doesn't fit into the current free time slot, try the next one
                        generate_combinations(current_index + 1, current_combination, remaining_tasks, free_times)
                else:
                    # The task doesn't fit into the current free time slot, try the next one
                    generate_combinations(current_index + 1, current_combination, remaining_tasks, free_times)
        # Start generating combinations from the first free time slot
        generate_combinations(0, [], flexible_tasks, free_times)
        
        for i, combination in enumerate(all_combinations, start=1):
            print(f"Combination {i}:")
            for task, start_time, end_time in combination:
                print(f"Task: {task.name}, Start: {start_time}, End: {end_time}")
            print()
        return all_combinations
    
    def find_best_combination(self):
        all_tasks = copy.deepcopy(self.tasks)
        fixed_tasks = [task for task in all_tasks if not task.flexibility]
        self.assign_task_importance(all_tasks)
        all_combinations = self.every_way_of_fitting_to_schedule()
        max_score = 0
        best_combination = []
        for combination in all_combinations:
            if combination == None:
                continue
            total_score = 0
            for task, start_time, end_time in combination:
                time_in_between = 0
                current_time = start_time
                for i in range(len(self.productivity_periods)):
                    if current_time >= self.productivity_periods[i][0] and end_time <= self.productivity_periods[i][1]:
                        time_in_between += end_time - current_time
                        break
                    elif current_time >= self.productivity_periods[i][0] and end_time > self.productivity_periods[i][1]:
                        time_in_between += self.productivity_periods[i][1] - current_time
                        current_time = self.productivity_periods[i][1]
                    
                    elif current_time < self.productivity_periods[i][0] and end_time <= self.productivity_periods[i][1]:
                        if end_time > self.productivity_periods[i][0]:
                            time_in_between += end_time - self.productivity_periods[i][0]
                        break
                    
                    elif current_time < self.productivity_periods[i][0] and end_time > self.productivity_periods[i][1]:
                        time_in_between += self.productivity_periods[i][1] - self.productivity_periods[i][0]
                        current_time = self.productivity_periods[i][1]
                    
                    else: 
                        break
                total_score += time_in_between * int(task.importance)
            if total_score > max_score:
                max_score = total_score
                best_combination = combination
        
        to_return = []
        for task in best_combination:
            to_return.append([task[0].name, task[1], task[2]])

        for fixed in fixed_tasks:
            to_return.append([fixed.name, self.convert_to_minutes(fixed.startTime), self.convert_to_minutes(fixed.endTime)])

        to_return.sort(key=lambda x: x[1])

        for task in to_return:
            task[1] = self.convert_minutes_to_time(task[1])
            task[2] = self.convert_minutes_to_time(task[2])

        
        return to_return
    
    def convert_to_minutes(self, time):
        return time.hour * 60 + time.minute
           
    def convert_minutes_to_time(self, minutes):
        hours = minutes // 60
        minutes = minutes % 60
        time_diff = dt.timedelta(hours=hours, minutes=minutes)
        midnight = dt.datetime.combine(dt.date.today(), dt.time.min)
        desired_time = midnight + time_diff
        return desired_time
    
    def convert_tasks_to_minutes(self):
        for task in self.tasks:
            task.startTime = int(task.startTime.hour) * 60 + int(task.startTime.minute)
            task.endTime = int(task.endTime.hour) * 60 + int(task.endTime.minute)
    def find_free_times(self):
        # Sort tasks by start time to handle them in order
        self.convert_tasks_to_minutes()
        sorted_tasks = sorted(self.tasks, key=lambda x: x.startTime)
        fixed_tasks = [task for task in sorted_tasks if not task.flexibility]
        # Initialize the working hours
        working_hours_start = self.wakeup 
        working_hours_end = self.sleep   
        free_times = []
        current_time = working_hours_start
        for task in fixed_tasks:
            if current_time < task.startTime and current_time + (task.endTime - task.startTime) <= working_hours_end:
                free_times.append([current_time, task.startTime])
            current_time = task.endTime
        else:
            free_times.append([current_time, working_hours_end])
        self.free_times = free_times
        return free_times