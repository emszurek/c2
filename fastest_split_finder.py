#!/usr/bin/env python3

import os
import sys
import statistics

def Log_Loader():
    ### Function to return a dictionary of the logfile
    
    # build a list of files starting with 'concept2' and prompt user to select if more than 1
    print('Detecting Concept 2 logfiles.')
    file_list = []
    for dir_file in os.listdir():
        if dir_file.count('concept2'):
            file_list.append(dir_file)
            print(len(file_list),'. ',dir_file,sep='')
    
    if len(file_list) == 0:
        print('No Concept 2 logfiles found. \nPlease run this script from a directory with Concept 2 logfiles.')
        input('Press any key to exit.')
        sys.exit('Exit Code 0: No Concept 2 logfiles found.')

    elif len(file_list) == 1:
        user_selection = 1

    else:
        user_selection = input('Please select a logfile by number:')
        
    file_selection = file_list[int(user_selection)-1]

    print('Loading ',file_selection,'...',sep='',end='')
    log_file = open(file_selection, 'rt')

    log_dictionary = {
        'Pull':[],
        'Time':[],
        'Distance':[],
        'Pace':[],
        'Watts':[],
        'CalHr':[],
        'StrokeRate':[],
        'HeartRate':[]
    }

    for line in log_file.readlines():
        # split each line into a new list value for the source CSV
        line_split = line.split(',')

        # iterate through the list and assign values to corresponding key value lists
        value_locator = 0
        for log_key in log_dictionary.keys():
            log_dictionary[log_key].append(line_split[value_locator].strip('"').strip('"\n'))
            value_locator += 1

    # Trim headers
    for log_key in log_dictionary.keys():
        log_dictionary[log_key].pop(0)

    # Handle formatting
    for log_key in log_dictionary:
        value_locator = 0
        if log_key == 'Time':
            for log_key_value in log_dictionary[log_key]:
                log_dictionary[log_key][value_locator] = float(log_key_value)
                value_locator += 1
        elif log_key == 'Distance':
            for log_key_value in log_dictionary[log_key]:
                log_dictionary[log_key][value_locator] = int(float(log_key_value))
                value_locator += 1
        else:
            pass

    print(' done')

    return log_dictionary

def Build_Meter_Dict(log_dict):
    ### Function to pad out missing meter values and return a dict with meters as key
    meter_dict = {}
    lower_meter = 0
    upper_meter = 0

    #iterate a dictionary out to the highest meter recorded in log
    for meter_x in range(log_dict['Distance'][0], log_dict['Distance'][-1]+1):
        #print('meter x is',meter_x,'of type',type(meter_x))

        if log_dict['Distance'].count(meter_x):
            time_x = log_dict['Time'][log_dict['Distance'].index(meter_x)]
            meter_dict.update({meter_x: time_x})
            lower_meter = meter_x
            #print('time of',meter_x,'is',time_x,'of type',type(time_x)) #debug
        else:
            #find next
            meter_x_pos = log_dict['Distance'].index(lower_meter)
            upper_meter = log_dict['Distance'][meter_x_pos+1]
            #print('meter',meter_x,'is between',lower_meter,'and',upper_meter) #debug
            
            #process averages
            lower_time = log_dict['Time'][log_dict['Distance'].index(lower_meter)]
            upper_time = log_dict['Time'][log_dict['Distance'].index(upper_meter)]
            time_delta = upper_time - lower_time
            time_span = upper_meter - lower_meter
            time_rate = time_delta / time_span
            #print('lower meter',lower_meter,'and upper meter',upper_meter,'are',time_span,'meters and',time_delta,'seconds apart.') #debug

            #apply
            #most_recent_trusted_time = l
            time_x = lower_time + (time_rate*(meter_x-lower_meter))
            meter_dict.update({meter_x: time_x})
    
    return meter_dict

def Find_Best_Split(meter_times):
    ### Hunt for best split time per meter
    best_time = 9999
    split_time_log = []

    assert type(meter_times) == dict
    for meter, time in meter_times.items():
        split_end_meter = meter + 500
        try:
            split_end_time = meter_times[split_end_meter]
            total_split_time = split_end_time - time
            split_time_log.append(total_split_time)
            if total_split_time < best_time:
                best_time = total_split_time
        except: pass
        #print('Meter',meter,'split at',total_split_time,'seconds') #debug

    split_average = statistics.mean(split_time_log)
    split_stdev = statistics.stdev(split_time_log)

    return [best_time, split_average, split_stdev]

def main():
    # main loop

    c2_log_file = Log_Loader()
    meter_dict = Build_Meter_Dict(c2_log_file)
    split_metrics = Find_Best_Split(meter_dict)
    assert type(split_metrics) == list and len(split_metrics) == 3
    best_split_time = split_metrics[0]
    best_split_minutes = int(best_split_time//60)
    best_split_seconds = best_split_time % 60
    avg_split_time = split_metrics[1]
    avg_split_minutes = int(avg_split_time//60)
    avg_split_seconds = avg_split_time % 60

    announcement = 'Your best split time was {}:{:2.1f}.\nYour mean split time was {}:{:2.1f}'
    print(announcement.format(best_split_minutes, best_split_seconds, avg_split_minutes, avg_split_seconds))
    print('Split standard deviation was',round(split_metrics[2], 2),'seconds.')
    
    #print(len(c2_log_file['CalHr']))
    CalHrSum = 0
    for val in c2_log_file['CalHr']:
        CalHrSum += int(val)
    #print(CalHrSum/len(c2_log_file['CalHr']))
    CalHrAvg = CalHrSum / len(c2_log_file['CalHr'])
    TotalSec = int(c2_log_file['Time'][-1])
    CalBurn = (CalHrAvg-300+(1.714*210))*TotalSec/3600
    print('You burned a total of',round(CalBurn,1),'calories')

    return None

if __name__ == "__main__":
    main()
