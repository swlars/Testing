#!/usr/bin/python3
import os
import subprocess
import re
import seaborn
import statistics
import pandas
import numpy
import json
from collections import defaultdict
import tkinter
import matplotlib
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import datetime
import string
import time

# NOTES:
# OUTPUT DIRECTORIES
# TODO
# 


# UDP Test
# Tuning
# Socket buffer size, larger iperf3 socket buffers

NUM_THREADS = 16 
RUNS_PER_THREAD = 10 

#NUM_THREADS = 8
#RUNS_PER_THREAD = 10

#IPERF3_CONTROL = "/home/swlarsen/git/esnet/iperf/src/iperf3"
#IPERF3_TEST = "/home/swlarsen/git/seg/iperf/src/iperf3"
#IPERF2="/home/swlarsen/git/iperf2-code/src/iperf"

IPERF3_CONTROL = "/Users/swlarsen/git/esnet/iperf/src/iperf3"
IPERF3_TEST = "/Users/swlarsen/git/seg/iperf/src/iperf3"
IPERF2="/Users/swlarsen/git/iperf2-code/src/iperf"

OUTPUT_DIRECTORY="outputs/"
# CONTROL/TEST/IP2_timestamp

SERVER_IP = "192.168.127.2"
PORT="5201"


# Make a folder
def make_folder(name):
    print("make_folder: {}".format(name))
    folder_name = "{}_{}".format(name, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    print("time {}".format(folder_name))
    new_output = os.path.join(OUTPUT_DIRECTORY, folder_name)
    os.mkdir(new_output, 0o777)
    return new_output


def run(binary, output_directory, filename):
    print("Run")
    # TODO check binaries?
    #= "c_{}_{}.txt"
    # /home/swlarsen/git/iperf/src/iperf3 -c 192.168.127.2 --parallel ${i} >> name

    for test in range(1, NUM_THREADS+1):
        for run in range(0, RUNS_PER_THREAD):
            cmd = [binary, "-c", SERVER_IP, "-J", "-P", "{}".format(test), "-p",PORT]
            print("cmd: {}".format(cmd))
            output = os.path.join(output_directory, filename.format(test, run))
            print("opening: {}", output)
            with open(output, "w") as f:
                t = subprocess.call(cmd, stdout=f, stderr=f)
                print("exiting with: {}".format(t))

    return

def run_control():
    print("Run Control")
    control_filename = "c_{}_{}.txt"
    # /home/swlarsen/git/iperf/src/iperf3 -c 192.168.127.2 --parallel ${i} >> name
    output = make_folder("control")
    print("output: {}".format(output))
    run(binary=IPERF3_CONTROL, output_directory=output, filename=control_filename)

#    for test in range(1, NUM_THREADS+1):
#        for run in range(0, RUNS_PER_THREAD):
#            control_cmd = [IPERF3_CONTROL, "-c", SERVER_IP, "-J", "-P", "{}".format(test)]
#            print("control_cmd: {}".format(control_cmd))
#
#            with open(control_filename.format(test, run), "w") as f:
#                t = subprocess.call(control_cmd, stdout=f, stderr=f)
#                print("exiting with: {}".format(t))

    return

def run_test():
    print("Run Test")
    #./src/iperf3 -c 192.168.127.2 --parallel 1
    test_filename = "t_{}_{}.txt"
    output = make_folder("test")
    print("output: {}".format(output))
    run(binary=IPERF3_TEST, output_directory=output, filename=test_filename)
    #for i in range(1, NUM_THREADS+1):
    #    with open(test_filename.format(i), "a+") as f:
    #        test_cmd = [IPERF3_TEST, "-c", SERVER_IP, "-J", "-P", "{}".format(i)]
    #        print("test_cmd: {}".format(test_cmd))
    #        for run in range(0, RUNS_PER_THREAD):
    #            subprocess.call(test_cmd, stdout=f, stderr=f)
    return

def run_ip2():
    print("Run ip2")
    test_filename = "ip2_{}_{}.txt"
    output = make_folder("test")
    print("output: {}".format(output))
    run(binary=IPERF2, output_directory=output, filename=test_filename)
    return


import glob
def summarize_runs(output_directory, filename, summary_filename):
    print("Summarize runs")
    print("Looking in ... {}".format(output_directory))
    print("filename: {} :: {}".format(filename, filename.split('_')))

    # Assume separate directories for each test run
    directories = [directory for directory in os.listdir(output_directory) if directory.startswith(filename.split('_')[0])]

    # TODO probably need to make this so it can handle double digits
    #runs = {}
    # TODO get_run_from_name() ... etc ?

    # TODO some of this is hard coded
    threads = [ []] 
    print(threads)
    for directory in directories:
        print("{}".format(directory))
        for files in glob.glob(os.path.join(output_directory, directory, filename.format('*', '*'))):
            path = files.split('/')
            name = path[-1].split('_')

            num_threads = int(name[1])
            run_num = int(name[-1].split('.')[0])

            with open(files, 'r') as f:
                run = json.load(f)
            if num_threads > len(threads):
                while len(threads) <= num_threads:
                    threads.append([])
            threads[num_threads].append(run)
        summary_file = os.path.join(output_directory, directory, summary_filename)
        with open(summary_file, 'w') as s:
            s.write(json.dumps(threads))
    return

def parse_with_json(output_directory, filename, summary_filename):
    print("Parsing with json")
    summary = []

    for test in range(1, NUM_THREADS+1):
        summary.append(test)
        summary[test-1] = [test, []]
        print(summary)
        for run in range(0, RUNS_PER_THREAD):
            output = output_directory + filename.format(test, run)
            print("parsing: {}", output)
            with open(output, "r") as f:
                out_json = json.load(f)

                print("JSON: {}".format(out_json["start"]["num_streams"]))
                print("JSON: {}".format(out_json["end"]["sum_sent"]["bits_per_second"]))
                print("JSON: {}".format(out_json["end"]["sum_recv"]["bits_per_second"]))
                summary[test-1][1].append(out_json["end"]["sum_sent"]["bits_per_second"])

    sum_file = output_directory + summary_filename
    print("summary: {}".format(summary))

    print("opening {}".format(sum_file))
    with open(sum_file, "w") as s:
        s.write(json.dumps(summary))

def parse_summary_with_json(output_directory, summary_filename, output):
    # TODO this things the files have the same prefix!!!!!!

    # TODO: CHECK IF OUTPUT DIRECTORY EXISTS
    print("Parsing summary {} with JSON".format(summary_filename))

    if not os.path.exists(output_directory):
        print("ERROR: output directory {} does not exist!".format(output_directory))
        return

    directories = [directory for directory in os.listdir(output_directory) if directory.startswith(summary_filename.split('_')[0])]
    for directory in directories:
        # Look at the summary file in each directory
        sum_file = os.path.join(output_directory, directory, summary_filename)
        #runs = []
        threads = []
        with open(sum_file, "r") as f:
            threads = json.load(f)

        summary = {}
        throughput_per_thread_count = [[]]
        cpu_utilization_per_thread_count = [[]]

        # TODO check limits, threads <

        #for run in runs:
        print("\n\n\n\n\n\n")
        for thread_num in range(0, len(threads)):
            print("thread_num : {}".format(thread_num))

            # Make sure the length is correct
            if thread_num >= len(throughput_per_thread_count):
                while thread_num >= len(throughput_per_thread_count):
                    throughput_per_thread_count.append([])
                    cpu_utilization_per_thread_count.append([])
            print(threads[thread_num])

            #if thread_num not in threads:
            #    print("NOPE")
            #    continue
            for run in threads[thread_num]:
                # TODO this is now only for verification
                if "num_streams" in threads[thread_num][0]["start"]:
                    print("JSON: {}".format(run["start"]["num_streams"]))
                    if thread_num != run["start"]["num_streams"]:
                        print("ERROR: thread_num {} vs num_streams {}".format(thread_num, num_streams))
                        exit(-1)
                else:
                    print("num_streams 0")
                print("            {}".format(run["end"]["cpu_utilization_percent"]))
                #print("            {}".format(run["end"]))

                # Add the run
                #print("threads {} tpt: {}".format(thread_num, throughput_per_thread_count))
                throughput_per_thread_count[thread_num].append(run["end"]["sum_sent"]["bits_per_second"])
                cpu_utilization_per_thread_count[thread_num].append(run["end"]["cpu_utilization_percent"])
                print(throughput_per_thread_count)

            

        #print("JSON: {}".format(run["end"]["sum_sent"]["bits_per_second"]))
        #print("JSON: {}".format(run["end"]["sum_recv"]["bits_per_second"]))
        summary["throughput_per_thread_count"] = throughput_per_thread_count
        summary["cpu_utilization_per_thread_count"] = cpu_utilization_per_thread_count
        #print(summary)

        output_file = os.path.join(output_directory, directory, output)
        with open(output_file, "w") as o:
            o.write(json.dumps(summary))


def parse_control():
    print("Parse Control")
    control_filename = "c_{}_{}.txt"
    parse_with_json(output_directory=OUTPUT_DIRECTORY, filename=control_filename, summary_filename="control_summary.json")
    return

def print_graph(filename):
    # Find all files
    # Parse all files
    print("opening {}".format(filename))
    with open(filename, "r") as f:
        data = json.load(f)
    if not data:
        print("ERROR data is None")
        exit(-1)
    print()
    print()
    print()
    print("opening {}".format(filename))
    print("DATA: {}".format(data))
    print()
    print()
    data_x = [z for z in range(1, NUM_THREADS)]
    print(data_x)
    #data_y = [statistics.median(y) for (x, y) in data]
    #data_y = [statistics.median(y) for y in data]
    #data_y =[]
    #for (x, y) in data["cpu_utilization_per_thread_count"]:
    #host_total
    #remote_system
    util = data["cpu_utilization_per_thread_count"]
    print("cpu_utilization_per_thread_count")
    # TODO AUTOMATICALLY GET THREAD
    host_total_threads = []

    remote_total_threads = []

    for thread in util:
        host_total_per_thread_count = []
        remote_total_per_thread_count = []

        #print("thread: {}".format(thread))

        for run in thread:
            host_total_per_thread_count.append(run["host_total"])
            remote_total_per_thread_count.append(run["remote_total"])

        print("host_total_per_thread_count {}".format(host_total_per_thread_count))
        #host_total_threads.append(statistics.median(host_total_per_thread_count))

        host_total_threads.append(host_total_per_thread_count)
        remote_total_threads.append(remote_total_per_thread_count)
    print("host_total_threads {}".format(host_total_threads))
    host_total_threads_df = pandas.DataFrame(host_total_threads)
    # No +1 to len
    host_total_x = [z for z in range(1, len(host_total_threads))]
    host_total_y = [statistics.median(z) for z in host_total_threads[1:]]

    remote_total_x = [z for z in range(1, len(host_total_threads))]
    remote_total_y = [statistics.median(z) for z in remote_total_threads[1:]]

    seaborn.set_theme(style="ticks", palette="pastel")
    seaborn.lineplot(x=host_total_x, y=host_total_y)
    seaborn.lineplot(x=remote_total_x, y=remote_total_y)
    plt.show()

    #seaborn.boxplot(data=host_total_threads_df, x=control_x, y=control_y)
    print(len(host_total_threads))
    #seaborn.boxplot(x=control_x, y=host_total_threads[1:])
    plt.show()
    #HERE
   

#    for x in data["cpu_utilization_per_thread_count"]:
#        # FOR EACH THREAD
#
#        #print("{}:{}".format(x, y))
#        print("BOO ")
#        print(len(x))
#        for y in x:
#            print(len(y))
#            print("HI {}".format(y))
#        #print("{}:{}".format(x, y))
#        #print(" {}".format(x["host_total"]))
#        #print(" {}".format(x["host_system"]))
#        #print(" {}".format(x["host_user"]))
#        #print(" {}".format(x["remote_total"]))
#        #print(" {}".format(x["remote_system"]))
#        #print(" {}".format(x["remote_user"]))
#
#    # throughput_per_thread_count
#    #data_y = [y for y in data]
#    # cpu_utilization_per_thread_count
#    #print(data_y)
#    cpu_util = pandas.DataFrame(data["cpu_utilization_per_thread_count"])
#    print("\n\n\n\n\n\n\n\n\n\n")
#    print("cpu_util {}".format(cpu_util))
#    #data_y = [statistics.median(y) for y in data]
#    #seaborn.lineplot(data=cpu_util)#, x=data_x, y=data_y)
#    seaborn.lineplot(data=cpu_util)#,x=data_x, y=data_y)
#
#    throughput = pandas.DataFrame(data["throughput_per_thread_count"])
#    print("throughput {}".format(throughput))
#    seaborn.lineplot(data=throughput)#, x=data_x, y=data_y)
#    plt.show()
#    #plt.savefig("here.png")
#
#    #c_df = pandas.DataFrame(c)
#    #p_df = pandas.DataFrame(p)
#
#    #seaborn.lineplot(data=c_df, x=control_x, y=control_y)
#    #seaborn.lineplot(data=p_df, x=thread_x, y=thread_y)
#    return

def print_control():
    output_directory = OUTPUT_DIRECTORY
    if not os.path.exists(output_directory):
        print("ERROR: output directory {} does not exist!".format(output_directory))
        return
    #summary_filename="control_summary.json"
    summary_filename="c_graph.json"

    directories = os.listdir(output_directory)
    for directory in directories:
        if not directory.startswith("control"):
            continue
        # Look at the summary file in each directory
        sum_file = os.path.join(output_directory, directory, summary_filename)
        print("sum_file: {}".format(sum_file))
        if not os.path.exists(sum_file):
            print("ERROR: sum_file {} does not exist".format(sum_file))
        print_graph(sum_file)
        #runs = []
        #with open(sum_file, "r") as f:
        #    runs = json.load(f)
    #sum_file = output_directory + summary_filename
    return

def print_test():
    print("Print Test")

    # GBits/sec
    #p = [
    #[1, [19.8, 20.4, 20.5]],
    #[2, [41.6, 40.6, 31.2]],
    #[3, [53.5, 40.6, 39.9]],
    #[4, [53.7, 49.9, 52.8]],
    #[5, [78.2, 75.3, 59.2]],
    #[6, [46.9, 48.0, 46.5]],
    #[7, [76.6, 60.4, 75.0]],
    #[8, [52.8, 51.9, 42.4]],
    #[9, [50.8, 53.8, 63.8]],
    #[10, [47.8, 66.6, 60.5]],
    #[11, [49.6, 43.2, 58.2]],
    #[12, [49.9, 61.0, 51.5]],
    #[13, [43.9, 45.0, 59.5]],
    #[14, [54.9, 51.5, 60.8]],
    #[15, [46.0, 67.1, 51.5]],
    #[16, [46.0, 55.4, 53.0]]
    #]

    #c = [
    #        [1,[30.5, 28.4, 28.3]],
    #        [2,[25.7, 26.6, 28.7]],
    #        [3,[16.2, 26.3, 16.2]],
    #        [4,[26.7, 23.2, 23.1]],
    #        [5,[24.9, 24.7, 23.4]],
    #        [6,[19.5, 21.7, 25.0]],
    #        [7,[21.9, 21.7, 22.1]],
    #        [8,[23.2, 22.3, 23.2]],
    #        [9,[23.0, 24.3, 24.3]],
    #        [10,[21.5, 21.2, 21.0]],
    #        [11,[23.7, 22.1, 24.2]],
    #        [12,[22.2, 20.1, 20.1]],
    #        [13,[22.4, 22.4, 22.4]],
    #        [14,[22.1, 20.7, 22.6]],
    #        [15,[23.3, 21.5, 22.6]],
    #        [16,[22.6, 22.3, 22.3]],
    #]
    control_x = [z for z in range(1, 17)]
    print(control_x)
    control_y = [statistics.median(y) for (x, y) in c]
    print(control_y)

    thread_x = [z for z in range(1, 17)]
    print(thread_x)
    thread_y = [statistics.median(y) for (x, y) in p]
    print(thread_y)
    #plot = [median(x[1]) for x in p]
    #print(plot)
    c_df = pandas.DataFrame(c)
    p_df = pandas.DataFrame(p)

    seaborn.lineplot(data=c_df, x=control_x, y=control_y)
    seaborn.lineplot(data=p_df, x=thread_x, y=thread_y)
    plt.show()

def summarize_control_runs():
    control_filename = "c_{}_{}.txt"
    summarize_runs(output_directory=OUTPUT_DIRECTORY, filename=control_filename, summary_filename="c_summary.json")

def summarize_ip2_runs():
    control_filename = "ip2_{}_{}.txt"
    summarize_runs(output_directory=OUTPUT_DIRECTORY, filename=control_filename, summary_filename="IP2_SUMMARY.json")

def main():
    print("main test")
    #make_folder(name="control")
    
    #run_control()
    #summarize_control_runs()
    #parse_summary_with_json(output_directory=OUTPUT_DIRECTORY, summary_filename="c_summary.json", output="c_graph.json")
    print_control()

    #run_test()
    #run_ip2()
    #summarize_ip2_runs()
    #parse_summary_with_json(output_directory=OUTPUT_DIRECTORY, summary_filename="IP2_SUMMARY.json")
    #run_test()


    #parse_control()
    #print_control()
    #filename = "c_{}_{}.txt"
    #parse_with_jq(filename)

    #run_test()
    #print_test()
    #print_graph()

if __name__ == "__main__":
    print("main")
    main()
