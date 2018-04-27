'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys
import copy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))


class MinHeap(object):
    def __init__(self):
        self.__list=[]
        self.__dict={}

    def shift_up(self, index): 
        if not isinstance(index, int):
            raise TypeError("index must be integer")       
        # print("Shifting up %d" % index)
        # [print(x) for x in self.__list]
        if index == 1:
            return    
        
        parent_index= (int)(index/2)
        if self.__list[index-1].burst_time < self.__list[parent_index-1].burst_time:
            tmp = self.__list[parent_index-1]
            self.__list[parent_index-1] = self.__list[index-1]
            self.__list[index-1]=tmp
            self.__dict[self.__list[parent_index-1].id]=parent_index
            self.__dict[self.__list[index-1].id]=index
            self.shift_up(parent_index)

    def shift_down(self,index):
        left_child=index*2
        right_child=index*2+1        
        min_index = 0
        _list = self.__list
        if right_child <= len(_list):
            if _list[left_child-1].burst_time <= _list[right_child-1].burst_time:
                min_index = left_child
            else:
                min_index = right_child
            if _list[index-1].burst_time > _list[min_index-1].burst_time:
                tmp = _list[min_index-1]
                _list[min_index-1]=_list[index-1]
                _list[index-1] = tmp
                self.__dict[_list[min_index-1].id]=min_index
                self.__dict[_list[index-1].id]=index
                self.shift_down(min_index)
        elif left_child <= len(_list):
            if _list[index-1].burst_time > _list[left_child-1].burst_time:
                tmp = _list[left_child-1]
                _list[left_child-1]=_list[index-1]
                _list[index-1] = tmp
                self.__dict[_list[left_child-1].id]=left_child
                self.__dict[_list[index-1].id]=index
                self.shift_down(left_child)

    def add(self, process):        
        self.__list.append(process)
        print("Add %d to heap with predicted burst time as %d" % (process.id, process.burst_time))
        # [print(x) for x in self.__list]
        self.__dict[process.id] = len(self.__list)
        self.shift_up(len(self.__list))
        
    
    def get_min(self):
        if len(self.__list) > 0:
            return self.__list[0]
        else:
            return None

    def remove(self, process):        
        print("Remove process %d" % process.id)
        index = self.__dict[process.id]        
        # print ("Index is %d" % index)
        process = self.__list[index-1]
        self.__list[index-1] = self.__list[len(self.__list)-1]
        self.__dict[self.__list[index-1].id]= index
        self.__list = self.__list[:-1]   
        self.__dict.pop(process.id, None)  
        # print(self.__dict)
        if len(self.__list) >0: 
            self.shift_down(index)        

    def get_index(self,process):
        return self.__dict[process.id]

    def pop(self):
        if len(self.__list) > 0:
            obj= self.__list[0]
            self.remove(obj)
        else:
            obj= None        
        return obj
    
def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    process_list_to_sch = copy.deepcopy(process_list)
    current_time = 0
    schedule = [] 
    current_process_list = process_list_to_sch
    remaining_process_list = []
    last_execution_time_dict = {}
    num_process=len(process_list_to_sch)
    waiting_time=0
    while(len(current_process_list)>0):
        for process in current_process_list:
            if current_time >= process.arrive_time:
                if len(schedule)==0 or schedule[len(schedule)-1][1]!=process.id:
                    schedule.append((current_time,process.id))                
                    # print("Add (%d,%d)" % (current_time, process.id))

                if process.id in last_execution_time_dict.keys():
                    last_execution_time = last_execution_time_dict[process.id]                   
                else:
                    last_execution_time = process.arrive_time                                
                waiting_time = waiting_time + (current_time - last_execution_time)                
                if process.burst_time > time_quantum:                    
                    remaining_process_list.append(process)
                    current_time = current_time + time_quantum
                    process.burst_time = process.burst_time - time_quantum
                    last_execution_time_dict[process.id] = current_time 
                else:
                    current_time = current_time + process.burst_time                
                    last_execution_time_dict.pop(process.id, None)                
            else:
                remaining_process_list.append(process)
        if len(remaining_process_list)> 0 and remaining_process_list[0].arrive_time>current_time:
            current_time = remaining_process_list[0].arrive_time
        current_process_list=remaining_process_list
        remaining_process_list=[]
    avg_waiting_time = waiting_time/(num_process+0.0)
    return schedule, avg_waiting_time

def SRTF_scheduling(process_list):
    # print("Starting the SRTF Scheduling")
    proc_list_to_sch = copy.deepcopy(process_list)
    if len(process_list)==0:
        return ([],0.0)
    current_time = 0
    schedule = []
    last_execution_time_dict = {}
    sched_proc_inx = 0
    minheadp = MinHeap()    
    current_time = proc_list_to_sch[0].arrive_time
    waiting_time = 0
    sched_proc_inx = get_arrived_proc_SRTF(sched_proc_inx, proc_list_to_sch, current_time, minheadp)
    # print("Start scheduling the tasks")
    while(minheadp.get_min() is not None):
        if sched_proc_inx < len(proc_list_to_sch)-1:
            next_arrival_time = proc_list_to_sch[sched_proc_inx+1].arrive_time
        else:
            next_arrival_time = -1
        
        if next_arrival_time < 0:            
            #If no more process arrive, in shortest remaining time first algorithm,
            #no more preemptive happen, just clean all remaining in ascending burst time order.
            while(minheadp.get_min() is not None):
                proc_to_exe = minheadp.get_min()
                scheduleProcess(schedule, current_time, proc_to_exe)
                # print("Burst time: %d" % process_to_exe.burst_time)
                if proc_to_exe.id in last_execution_time_dict.keys():
                    last_execution_time = last_execution_time_dict[proc_to_exe.id]                   
                else:
                    last_execution_time = proc_to_exe.arrive_time                
                waiting_time = waiting_time + (current_time - last_execution_time)                                
                current_time = current_time + proc_to_exe.burst_time
                last_execution_time_dict[proc_to_exe.id]=current_time                
                # print("Current time is %d" % current_time)
                removeFinishedProc(minheadp, proc_to_exe, last_execution_time_dict)
                # print("Finished process %d, current time: %d, waiting time: %d" %(proc_to_exe.id, current_time, waiting_time))
                
        else:            
            proc_to_exe = minheadp.get_min()
            scheduleProcess(schedule, current_time, proc_to_exe)
            #Calculate the waiting time first.
            if proc_to_exe.id in last_execution_time_dict.keys():
                last_execution_time = last_execution_time_dict[proc_to_exe.id]                   
            else:
                last_execution_time = proc_to_exe.arrive_time                                
            waiting_time = waiting_time + (current_time - last_execution_time)                
            # Current process finished before next process arrives.
            if proc_to_exe.burst_time <= next_arrival_time - current_time:                
                current_time = current_time + proc_to_exe.burst_time    
                last_execution_time_dict[proc_to_exe.id]=current_time           
                removeFinishedProc(minheadp, proc_to_exe, last_execution_time_dict)
                # print("Finished process %d, current time: %d, waiting time: %d" %(proc_to_exe.id, current_time, waiting_time))                
                #If all process currently submitted are finished, need to add next cycle of arrival process.
                if minheadp.get_min() is None:
                    current_time = next_arrival_time
                    sched_proc_inx = get_arrived_proc_SRTF(sched_proc_inx+1, proc_list_to_sch, current_time, minheadp)                    
            # Upon the time next process arrives, need to recheck the SRT.
            else:                
                proc_to_exe.burst_time = proc_to_exe.burst_time - (next_arrival_time - current_time)
                last_execution_time_dict[proc_to_exe.id] = next_arrival_time
                minheadp.shift_up(minheadp.get_index(proc_to_exe))
                current_time = next_arrival_time  
                last_execution_time_dict[proc_to_exe.id]=current_time                              
                sched_proc_inx = get_arrived_proc_SRTF(sched_proc_inx+1, proc_list_to_sch, current_time, minheadp)                                        
    avg_waiting_time = waiting_time/(len(process_list))
    #print("len %d" % len(process_list))
    return schedule,avg_waiting_time 

def removeFinishedProc(minheadp, proc_to_exe, last_execution_time_dict):
    minheadp.remove(proc_to_exe)
    last_execution_time_dict.pop(proc_to_exe.id,None)

def scheduleProcess(schedule, current_time, process_to_exe):
    if len(schedule)==0 or schedule[len(schedule)-1][1]!=process_to_exe.id:
        schedule.append((current_time,process_to_exe.id))                    

def get_arrived_proc_SRTF(scheduled_process_index, process_list_to_sch, current_time, minheap):
    for i in range(scheduled_process_index, len(process_list_to_sch)):
        if process_list_to_sch[i].arrive_time <= current_time:
            minheap.add(process_list_to_sch[i])
            scheduled_process_index = i
            # print("scheduled_process_index is %d" % scheduled_process_index)
        else:
            break
    return scheduled_process_index

def get_arrived_proc_SJF(scheduled_process_index, process_list_to_sch, current_time, minheap,last_burst_time_dict,alpha,initial_guess,last_predict_time_dict):
    print("scheduled_process_index : %d" %scheduled_process_index)
    added=False
    for i in range(scheduled_process_index, len(process_list_to_sch)):
        proc_to_add = process_list_to_sch[i]
        if proc_to_add.arrive_time <= current_time:
            if proc_to_add.id in last_burst_time_dict.keys():
                proc_to_add.burst_time = alpha * last_burst_time_dict[proc_to_add.id] + (1-alpha) * last_predict_time_dict[proc_to_add.id]
            else: 
                proc_to_add.burst_time = initial_guess            
            minheap.add(process_list_to_sch[i])
            last_predict_time_dict[proc_to_add.id]=proc_to_add.burst_time
            scheduled_process_index = i
            added = True
            # print("scheduled_process_index is %d" % scheduled_process_index)
        else:
            break
    return scheduled_process_index if added else scheduled_process_index-1

def SJF_scheduling(process_list, alpha):
    if process_list is None or len(process_list)==0:
        return ([],0.0)
    initial_guess = 5
    proc_list_to_sch = copy.deepcopy(process_list)
    [setattr(x, "real_burst_time", x.burst_time) for x in proc_list_to_sch]
    [setattr(x, "burst_time", initial_guess) for x in proc_list_to_sch]
    last_burst_time_dict = {}
    current_time = 0    
    last_predict_time_dict={}
    waiting_time = 0
    schedule = []
    minheap = MinHeap()
    sched_proc_inx = 0
    proc_to_exe = proc_list_to_sch[0]
    current_time = proc_to_exe.arrive_time   
    sched_proc_inx = get_arrived_proc_SJF(sched_proc_inx, proc_list_to_sch, current_time, minheap, last_burst_time_dict,alpha,initial_guess,last_predict_time_dict)
    # print("sche_proc_inx: %d" % sched_proc_inx)
    while minheap.get_min() is not None:
        proc_to_exe = minheap.get_min()
        schedule.append((current_time, proc_to_exe.id))
        print("Current time: %d, waiting time %d, start %d" % (current_time,waiting_time,proc_to_exe.id))
        waiting_time = waiting_time + ( current_time - proc_to_exe.arrive_time)
        current_time = current_time + proc_to_exe.real_burst_time
        last_burst_time_dict[proc_to_exe.id] = proc_to_exe.real_burst_time
        minheap.remove(proc_to_exe)
        if minheap.get_min() is None and sched_proc_inx + 1 < len(proc_list_to_sch) and current_time < proc_list_to_sch[sched_proc_inx+1].arrive_time:
            current_time = proc_list_to_sch[sched_proc_inx+1].arrive_time            
            print("Arrived process finished, get next batch: %d with index %d" % (current_time, sched_proc_inx))
        sched_proc_inx = get_arrived_proc_SJF(sched_proc_inx+1, proc_list_to_sch, current_time, minheap, last_burst_time_dict,alpha,initial_guess,last_predict_time_dict)        
    avg_waiting_time = waiting_time / len(process_list)
    return (schedule, avg_waiting_time)

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

    #Task 2
    RR_avg_time_list=[]
    for time_quantum in range(1,20):
        _, avg_time = RR_scheduling(process_list,time_quantum = time_quantum)
        RR_avg_time_list.append((time_quantum,round(avg_time,2)))
    write_output("RR_diff_quantum_test.txt", RR_avg_time_list, 0.0)
    
    sjf_avg_time_list =[]
    alpha_list = [x/20.0 for x in range(1,20)]
    for alpha in alpha_list:
        _, avg_time = SJF_scheduling(process_list,alpha=alpha)
        sjf_avg_time_list.append((alpha, round(avg_time,2)))
    write_output("SJF_diff_alpha_test.txt", sjf_avg_time_list, 0.0)
    

    #Bonus
if __name__ == '__main__':
    main(sys.argv[1:])
