# Program to produce a report and data analysis of the devices usage statistics

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import math
import numpy as np
import os

global log_database

def produce_graphs(devices, log_database):
    # Assume log_database is a loaded dictionary which maps device IDs to a list of formatted dictionaries
    # Assume devices is a list of all alphanumerical device IDs on record
    # for every log file associated with a device, extract no. dispensed, no. ignored dispensed and no. detected for a given 

    total_data = {}

    # change working directory so that graphs are saved in the a single folder
    cur_dir = os.getcwd() # current working directory

    # must be in static folder so flask can find graphs
    graph_dir = os.path.join(cur_dir, "static") # path to graph folder

    # if path doesn't exist, make it
    if not os.path.exists(graph_dir):
        os.mkdir(graph_dir)

    os.chdir(graph_dir) # change current working directory to this directory

    # names of the graphs which get created
    names = []

    for device in devices:
        # extract log files
        logs = log_database[device]

        # reset variables
        prev_date = -math.inf

        # map dates to a three item list containing total detected, total dispensed and total ignored respectively
        device_data = {}

        for log in logs:
            # extract date, which is in the form year month day e.g. 202011 is 1/1/2020
            date = int(log["time_sent"])
            
            # if day has changed
            if date not in device_data:
                # record new info for that day
                device_data[date] = [log["total_detected"], log["total_dispensed"], log["total_ignored"]]

                # update
                prev_date = date

            else:
                # if this day has already been recorded, append it on to existing info
                device_data[date][0] += log["total_detected"]
                device_data[date][1] += log["total_dispensed"]
                device_data[date][2] += log["total_ignored"]
        
        # sort dates list
        results = sorted(device_data.items(), key=sorter)

        # extract data
        dates = []
        total_detected = []
        total_dispensed = []
        total_ignored = []

        for key, value in results:
            # order of results list : total detected, total dispensed and total ignored respectively
            total_detected.append(value[0])
            total_dispensed.append(value[1])
            total_ignored.append(value[2])

            # format date to string
            key = str(key)
            date = [key[6:], key[4:6], key[:4]]
            dates.append("/".join(date))
        
        # produce graphs
        fig, ax = plt.subplots()

        # Plot each line of data
        ax.plot(dates, total_detected, label="Total Detected")
        ax.plot(dates, total_dispensed, label="Total dispensed")
        ax.plot(dates, total_ignored, label="Total Ignored")
        
        # Label axes
        ax.set_xlabel("Date")
        ax.set_ylabel("No. dispensed")

        # Make legend
        ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=3, mode="expand", borderaxespad=0.)

        # fix overlapping labels
        fig.autofmt_xdate(rotation=30)

        # name of file graph will be saved as
        name = "individual_graph_{:s}".format(device)

        # Save graphs
        plt.savefig(name)

        # add graph name
        names.append(name)
        
        # Save average data so it can be used in the total graph
        total_data[str(device)] = [sum(total_detected)//len(total_detected), sum(total_dispensed)//len(total_dispensed), sum(total_ignored)//len(total_ignored)]

    # produce bar chart to show total data
    fig, ax = plt.subplots()
    
    # width of bars in chart
    width = 0.3

    # x coordinates of each bar
    x = np.arange(len(total_data.keys()))

    # Look familiar?
    total_detected_means = []
    total_dispensed_means = []
    total_ignored_means = []
    sorted_devices = []

    # Get data
    data = total_data.items()

    # Extract data
    for key, value in data:
        # In order defined above
        total_detected_means.append(value[0])
        total_dispensed_means.append(value[1])
        total_ignored_means.append(value[2])

        # get device id associated with stats
        sorted_devices.append(str(key))
    
    # Plot grouped bar chart
    ax.bar(x - width, total_detected_means, width, label='Detected Mean')
    ax.bar(x, total_dispensed_means, width, label='Dispened Mean')
    ax.bar(x + width, total_ignored_means, width, label='Ignored Mean')

    # legend
    ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=3, mode="expand", borderaxespad=0.)

    # label chart
    ax.set_xlabel("Device ID")
    ax.set_ylabel("Quantity")

    # set x axis
    ax.set_xticks(x)
    ax.set_xticklabels(sorted_devices)

    # fix overlapping labels
    fig.autofmt_xdate(rotation=30)

    # name of graph file
    name = "total_graph"

    # Save graph
    plt.savefig(name)

    # add graph name
    names.append(name)

    # chnage the current working directory back
    os.chdir(cur_dir)

    return names


def sorter(t):
    return t[0]        

def produce_report(devices, log_database, graph_names):
    # Assume log_database is a loaded dictionary which maps device IDs to a list of formatted dictionaries
    # Assume devices is a list of all alphanumerical device IDs on record
    # Produce a html report containing the graphs made above
    report_start = """<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
</head>
<body>"""

    report_end = """
</body>
</html>"""

    # graphs html
    images = ""

    # remember working directory
    cur_dir = os.getcwd()

    # must be in templates folder so flask can find html file
    page_dir = os.path.join(cur_dir, "templates") # path to template website

    # if path doesn't exist, make it
    if not os.path.exists(page_dir):
        os.mkdir(page_dir)

    # add graphs to html doc
    for graph in graph_names:
        # format name
        name = graph.split("_")
        name = [s.capitalize() for s in name]
        name = " ".join(name)

        # get path to graph locally
        path = os.path.join("static", graph)
        print(path)

        # create html for displaying the image
        images += """

    <h3>{:s}</h3>
    <img src="\{:s}.png" alt="{:} graph">
    """.format(name, path, graph)

    # total report
    total = report_start + images + report_end

    # output file
    out_to_file = os.path.join(page_dir, "index.html")

    # open file
    f = open(out_to_file, "w")

    # write to file
    f.write(total)

    # close file stream
    f.close()


def run():
    # Access files, produce graphs and a report on the matter
    # Data to report on:
    #    - Usgae Statistics from the dispensers
    #    - Info from dispensers in the form:
    """
    {
        "device_ID":0
        "current_volume": 0, 
        "date_received": "27/05/2020", 
        "total_detected": 0, 
        "total_dispensed": 0, 
        "total_ignored": 0
    }
    """
    # Report on each variable over a time period (such as a week) and comparasion to other dispensers

    # Gonna test with a local file
    global log_database

    log_database = {}

    try:
        with open("log_database.json") as f:
            log_database = json.load(f) # load devices.json as a dict
            #print(log_database)
    except:
        print("Unable to load file log_database.json")

    # device ID list
    devices = ["device_" + str(i) for i in range(10)]

    # produce and save graphs based on log file data
    graph_names = produce_graphs(devices, log_database)

    # produce and save a summary of collected statistics
    produce_report(devices, log_database, graph_names)

    return "index.html"

if __name__ == '__main__':
    run()