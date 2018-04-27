from simulator import *


def multi_core_FCFS(process_list,num_cores):
    #store the (switching time, proccess_id) pair
    schedule = []    
    waiting_time = 0
    cores=[x for x in range(0,num_cores)]
    finished_time_for_core=[0 for x in range(0,num_cores)]    
    for process in process_list:    
        scheduled=False    
        for i in cores:
            if finished_time_for_core[i] ==0 or process.arrive_time>finished_time_for_core[i]:
                schedule.append((process.arrive_time,process.id, cores[i]))
                finished_time_for_core[i]=process.arrive_time + process.burst_time        
                scheduled=True
                break
        if not scheduled:
            min_comp_time = None
            inx=None
            for i in cores:
                if min_comp_time==None:
                    min_comp_time=finished_time_for_core[i]
                    inx =i
                elif min_comp_time > finished_time_for_core[i]:
                    min_comp_time=finished_time_for_core[i]
                    inx =i
            schedule.append((min_comp_time,process.id,cores[inx]))
            finished_time_for_core[inx] = min_comp_time + process.burst_time
            waiting_time = waiting_time + (min_comp_time - process.arrive_time)            
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def update_last_finished_time(process, finished_time, time_quantum):
    if process.burst_time > time_quantum:
        finished_time = finished_time + time_quantum
    else:
        finished_time = finished_time + process.burst_time
    return finished_time
def get_arrived_process(process_list,start_inx, current_time, list_to_add):
    for i in range(start_inx, len(process_list)):
        if process_list[i].arrive_time <= current_time:
            list_to_add.append(process_list[i])
            start_inx = i
        else:
            break
    return start_inx
def multi_core_RR(process_list, time_quantum, num_cores):
    proc_list_to_sch = copy.deepcopy(process_list)    
    current_time = 0
    schedule = [] 
    current_process_list = proc_list_to_sch
    remaining_process_list = []
    last_execution_time_dict = {}
    num_process=len(proc_list_to_sch)
    cores = [x for x in range(0,num_cores)]    
    core_inx=0
    last_finished_time_per_core=[0 for x in range(0,num_cores)]
    sch_core=[-1 for x in range(0,num_cores)]
    waiting_time=0
    added_proc_inx=0
    current_time = proc_list_to_sch[0].arrive_time
    # added_proc_inx=get_arrived_process(proc_list_to_sch,added_proc_inx, current_time, current_process_list)
    while(len(current_process_list)>0):        
        for process in current_process_list:            
            min_finished_time=None
            min_inx=None
            max_finished_time=None
            for i in cores:       
                if min_finished_time==None or  min_finished_time > last_finished_time_per_core[i]:
                    min_finished_time=last_finished_time_per_core[i]
                    min_inx = i
                if max_finished_time==None or max_finished_time < last_finished_time_per_core[i]:
                    max_finished_time=last_finished_time_per_core[i]           
            if min_finished_time >= process.arrive_time:    
                print(process.id)            
                alrdy_sched = False            
                for i in cores:                
                    if sch_core[i]==process.id:
                        if i != min_inx:
                            alrdy_sched=True
                            if last_finished_time_per_core[i] == min_finished_time:
                                if process.burst_time > time_quantum:
                                    last_finished_time_per_core[i] = last_finished_time_per_core[i] + time_quantum
                                    last_execution_time_dict[process.id] = last_finished_time_per_core[i]
                                    remaining_process_list.append(process)
                                else:
                                    last_finished_time_per_core[i] = last_finished_time_per_core[i] + process.burst_time                                
                                    last_execution_time_dict.pop(process.id,None)
                            else:
                                remaining_process_list.append(process)
                            break
                if not alrdy_sched:
                    if sch_core[min_inx] != process.id:#I did not schedule on this core in the previous run
                        schedule.append((last_finished_time_per_core[min_inx], process.id, min_inx))
                        sch_core[min_inx] = process.id
                        print("Schduleing (%d,%d,%d)" % (last_finished_time_per_core[min_inx], process.id, min_inx))
                        if process.id in last_execution_time_dict.keys():
                            last_exe_time = last_execution_time_dict[process.id]
                        else:
                            last_exe_time = process.arrive_time
                        waiting_time = waiting_time + (last_finished_time_per_core[min_inx] - last_exe_time)
                    if process.burst_time > time_quantum:                        
                        last_finished_time_per_core[min_inx] = last_finished_time_per_core[min_inx] + time_quantum
                        last_execution_time_dict[process.id] = last_finished_time_per_core[min_inx]
                        remaining_process_list.append(process)
                    else:
                        last_finished_time_per_core[min_inx] = last_finished_time_per_core[min_inx] + process.burst_time
                        last_execution_time_dict.pop(process.id,None)                        
                    process.burst_time = process.burst_time - time_quantum
            else:
                remaining_process_list.append(process)
        current_time = current_time + 1
        for i in cores:
            if last_finished_time_per_core[i] < current_time:
                last_finished_time_per_core[i] = current_time
                last_execution_time_dict.pop(sch_core[i],None)
                sch_core[i]=-1
        current_process_list=remaining_process_list
        remaining_process_list=[]
        print("Metrics")
        print(last_finished_time_per_core)
        print(sch_core)
        # break
    avg_waiting_time = waiting_time/(num_process+0.0)
    return schedule, avg_waiting_time


def _main_(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    #Bonus Multi core scheduling for FCFS and RR
    FCFS_schedule, FCFS_avg_waiting_time= multi_core_FCFS(process_list,2)
    write_output('FCFS_multi_core.txt', FCFS_schedule, FCFS_avg_waiting_time )

    RR_schedule, RR_avg_waiting_time= multi_core_RR(process_list, 2,2)
    write_output('RR_multi_core.txt', RR_schedule, RR_avg_waiting_time )

if __name__ == '__main__':
    _main_(sys.argv[1:])
