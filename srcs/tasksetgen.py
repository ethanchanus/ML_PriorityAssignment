from generator.gen import *
from rtmodel import tasks
from schedule import rta_lc_guan09 as rtalc
from schedule import audsley_opa as opa
import timeit
import threading
from util.log import myprint
from generator.permu import *
import os

def thread_gen(threadid, numProc, numTasks, numTaskset, utilDistr, Tmin, Tmax, maxtry_crta, tasksetlst, tasklst):
    myprint("Start thread_gen ".format( threadid))
    ts, t = generate_acceptable_tasksetlst(
        numProc=numProc, numTasks=numTasks, 
        numTaskset=numTaskset, 
        utilDistr=utilDistr,
        Tmin=Tmin, Tmax=Tmax, maxtry_crta=maxtry_crta)

    tasksetlst[threadid] = ts
    tasklst[threadid] = t


if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    print(os.getcwd(), sys.path)
    import time

    myprint("Generate all the task set")
    Tmin = 10
    Tmax = 10000
    

    # numProc = 2
    # numTasks = 4
    # numTaskset = 2
    # numThread = 1
    # MaxTry_CRTA = 5

    numProc = int(sys.argv[1])
    numTasks = int(sys.argv[2])
    numTaskset = int(sys.argv[3])
    numThread = int(sys.argv[4])
    MaxTry_CRTA = int(sys.argv[5])
    myprint("Gen options: numProc={}, numTasks={}, numTaskset={}, numThread={}".format(numProc,numTasks, numTaskset, numThread))

    myprint("--START------------------------------------")

    utilization_distribution_choices = [
        
        bimodal(0, 1, 0.1),        
        bimodal(0, 1, 0.3),
        
        bimodal(0, 1, 0.5),
        
        bimodal(0, 1, 0.7),        
        bimodal(0, 1, 0.9),        
        exponential(0, 1, 0.1),        
        exponential(0, 1, 0.3),        
        exponential(0, 1, 0.5),        
        exponential(0, 1, 0.7),        
        exponential(0, 1, 0.9),               
    ]

    if numTasks>7:
        utilization_distribution_choices += [ 
            bimodal(0, 1, 0.2),
            bimodal(0, 1, 0.4),
            bimodal(0, 1, 0.6),
            bimodal(0, 1, 0.8),
            exponential(0, 1, 0.8),
            exponential(0, 1, 0.6),
            exponential(0, 1, 0.4),
            exponential(0, 1, 0.2)]

   
    tasksetlst=[i for i in range(0,numThread)]
    tasklst=[i for i in range(0,numThread)]


    threadlst = [ threading.Thread(
        target=thread_gen, 
        args=(tid,
            numProc, numTasks, 
            numTaskset//numThread + 1, 
            utilization_distribution_choices, 
            Tmin, Tmax, MaxTry_CRTA,
            tasksetlst,
            tasklst
            ),
            )
        for tid in range(0,numThread)
    ]
    
    start = timeit.default_timer()


    for ti in threadlst:
        time.sleep(0.1)
        ti.start()

    for ti in threadlst:
        ti.join()

    myprint("--END------------------------------------")
    end = timeit.default_timer()

    myprint(end - start)

    t = tasklst[0]    
    ts = tasksetlst[0]    
    for i in range (1, len(tasklst)):
        tasklst[i]['i'] += len(tasklst[i-1]) 
        tasksetlst[i]['tsi'] += len(tasksetlst[i-1])
        t = t.append(tasklst[i], ignore_index=True)         
        ts = ts.append(tasksetlst[i], ignore_index=True) 

    tm = time.time()
    fname='data/acceptable/fin_tlst_ts{}_m{}_n{}.{}'.format(numTaskset, numProc, numTasks, tm)
    myprint("Write to file "+fname)
    t.to_csv(fname , index=False)

    fname='data/acceptable/fin_tslst_ts{}_m{}_n{}.{}'.format(numTaskset, numProc, numTasks, tm)
    myprint("Write to file "+ fname)
    ts.to_csv('data/acceptable/fin_tslst_ts{}_m{}_n{}.{}'.format(numTaskset, numProc, numTasks, tm) , index=False)
