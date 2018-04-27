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

def _main_(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    #Bonus
    FCFS_schedule, FCFS_avg_waiting_time= multi_core_FCFS(process_list,2)
    write_output('FCFS_multi_core.txt', FCFS_schedule, FCFS_avg_waiting_time )

if __name__ == '__main__':
    _main_(sys.argv[1:])
