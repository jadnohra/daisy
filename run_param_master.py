#!./dev/venv/bin/python

import subprocess
import queue
import threading
import time
from util.arg import *
import util.logging as logging
from param.net_msg import Receiver
from param.param_master import CartesianEngine
import param.param_protocol as protocol

def capture_scenario_params(scenario, ip_port):
    def launch_slaves():
        p = subprocess.Popen(['./dev/venv/bin/python', 'run_param_slave.py', 
                                '-scenario', scenario, '-stop_frame', '0',
                                '-no_logging', '-headless', protocol.k_arg_capture])
        p.wait()
    def receive_param_loop(param_engine):
        try:
            while True:
                objects = receiver.receive_objects()
                handle_received_params(objects, param_engine)
        except KeyboardInterrupt:
            receiver.stop()
    def handle_received_params(objects, param_engine):
        for obj in objects:
            logging.info(" Captured '{}' '{}' '{}'".format(obj['name'], obj['space'], obj['dflt']))
            param_engine.add_sampler(obj['name'], obj['space'], obj['dflt'])
            logging.info(f" Total Combination count {param_engine.product_size}")
    logging.info(f"====== Capturing '{scenario}' scenario parameters ======")
    receiver = Receiver(ip_port)
    launch_slaves()
    param_engine = CartesianEngine()
    handle_received_params(receiver.receive_objects(), param_engine)
    receiver.stop()
    return param_engine

def flow_scenarios(scenario, param_engine, sample_count=8, thread_count=4):
    def signal_sample_taken(lock, sample_holder):
        lock.acquire()
        sample_holder[0] = sample_holder[0] + 1
        lock.release()
    def count_samples_taken(lock, sample_holder):
        lock.acquire()
        ret = sample_holder[0]
        lock.release()
        return ret
    class ParametrizerThread(threading.Thread):
        def __init__(self, param_engine, queue, thread_count):
            super(ParametrizerThread, self).__init__()
            self._queue = queue
            self._thread_count = thread_count
            self._param_engine = param_engine
            self._stop_signalled = False
            
        def run(self):
            while self._stop_signalled == False:
                while self._queue.qsize() < 2:
                    sample = self._param_engine.sample()
                    if sample is not None:
                        self._queue.put(sample)
                    else:
                        return
                time.sleep(0)

    class WorkerThread(threading.Thread):
        def __init__(self, index, queue, lock, sample_holder, sample_names, scenario):
            super(WorkerThread, self).__init__()
            self._index = index
            self._queue = queue
            self._stop_signalled = False
            self._lock = lock
            self._sample_holder = sample_holder
            self._sample_names  = sample_names
            self._scenario = scenario
            
        def launch_and_wait(self, sample):
            par_args = []
            for i, v in enumerate(sample):
                par_args.append(protocol.k_arg_par_prefix + self._sample_names[i])
                par_args.append(str(v))
            opt_args = []
            if arg_has('-flow.monitors'):
                opt_args.append('-monitors')
                opt_args.append(arg_get('-flow.monitors', ''))
            p = subprocess.Popen(['./dev/venv/bin/python', 'run_param_slave.py', 
                                    '-scenario', self._scenario, 
                                    '-stop_frame', str(arg_get('-flow.frames', 50)),
                                    '+headless' if arg_has('-flow.headed') else '-headless',
                                    '+no_logging' if arg_has('-flow.verbose') else '-no_logging'] 
                                    + opt_args + par_args)
            p.wait()
            
        def run(self):
            while self._stop_signalled == False:
                try:
                    sample = self._queue.get_nowait()
                    signal_sample_taken(self._lock, self._sample_holder)
                    logging.info(f" #{self._index}: '{sample}'")
                    self.launch_and_wait(sample)
                except queue.Empty:
                    time.sleep(0)
    
    logging.info(f"====== Running '{scenario}' parameter flow ({sample_count} samples) ======")
    logging.info(f"{param_engine.get_param_names()}")
    
    thread_count = min(thread_count, sample_count)
    
    que = queue.Queue()
    lock = threading.Lock()
    sample_holder = [0]
    param_thread = ParametrizerThread(param_engine, que, thread_count)
    param_thread.start()
    
    worker_threads = []
    for i in range(thread_count):
        thread = WorkerThread(i, que, lock, sample_holder, param_engine.get_param_names(), scenario)
        worker_threads.append(thread)
    for t in worker_threads:
        t.start()
    
    while (count_samples_taken(lock, sample_holder) < sample_count
            and param_thread.is_alive()):
        time.sleep(0.01)
        
    for t in worker_threads:
        t._stop_signalled = True
        t.join()
        
    param_thread._stop_signalled = True
    param_thread.join()

# good demo: -scenario lidar -flow.frames 300 -flow.headed -flow.samples 12 -flow.threads 6
# good demo: -scenario brake-pb -flow.frames 100 -flow.headed -flow.samples 10 -flow.threads 1 -flow.monitors collision -flow.verbose
def main():
    scenario = arg_get('-scenario', 'scenario-1')
    ip_port = arg_get('-ip_port', 'localhost:4997').split(':')
    sample_count = int(arg_get('-flow.samples', 12))
    thread_count = int(arg_get('-flow.threads', 8))
    param_engine = capture_scenario_params(scenario, ip_port)
    flow_scenarios(scenario, param_engine, sample_count=sample_count, thread_count=thread_count)

if __name__ == "__main__":
    main()