import datetime as dt

class UltradianRhythm:
    def calculate_ultradian_intervals(wakeUp=dt.time(9, 0), sleep=dt.time(20, 0), peak_length=1.5, break_length=dt.timedelta(minutes=20)):
        """
        Calculate ultradian rhythm intervals within a workday using datetime.
        
        :param wakeUp: Workday start time as a datetime.time object
        :param sleep: Workday end time as a datetime.time object
        :param peak_length: Length of one peak performance period in hours
        :param break_length: Length of the break between peak periods as a datetime.timedelta object
        :return: List of tuples representing peak performance intervals as datetime.time objects
        """
    # Convert wakeUp and sleep times to datetime.datetime objects for calculation
        today = dt.date.today()
        wakeUp_dt = dt.datetime.combine(today, wakeUp)
        sleep_dt = dt.datetime.combine(today, sleep)
        
        awakeDuration = sleep_dt - wakeUp_dt
        awakeDuration_hours = awakeDuration.total_seconds() / 3600
        cycle_length_hours = peak_length + break_length.total_seconds() / 3600
        num_cycles = int(awakeDuration_hours / cycle_length_hours)
        
        intervals = []
        for cycle in range(num_cycles):
            peak_start = wakeUp_dt + dt.timedelta(hours=cycle * cycle_length_hours)
            peak_end = peak_start + dt.timedelta(hours=peak_length)
            
            # Only add intervals that fall within the day
            if peak_end.time() <= sleep and peak_start.time() >= wakeUp:
                intervals.append([peak_start.time(), peak_end.time()])

        for interval in intervals:
            interval[0] = interval[0].hour * 60 + interval[0].minute
            interval[1] = interval[1].hour * 60 + interval[1].minute
        return intervals

# Example usage
intervals = UltradianRhythm.calculate_ultradian_intervals()
