if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    print(sys.path)
    
# from typing import final
from generator.dist import * 
from generator.genutil import *
from rtmodel import tasks
from schedule import rta_lc_guan09 as rtalc
from schedule import audsley_opa as opa
import timeit
import threading
from util.log import myprint
from generator.permu import *
import os
def generate_tasklst(numProc, numTasks, numTaskset, utilDistr, Tmin, Tmax):
    
    #  - B# 1 882/1001 ts, found 119 ts. 16.52ts/10s
    def genFixSum(n, m, distr):        
        r = []
        while True:
            r = [ distr()() for i in range (0,n) ]
            if sum(r) <= m:
                break

        return pd.DataFrame(r, columns=['U'] )

    def uniform_choice_func():
        # global utilDistr
        return uniform_choice(utilDistr)
        
    
    def genFixSum0(n,m,distr):
        # B# 2 994/1001 ts, found 2 ts. 0.30ts/10s, (2,5)
        r= gen_util_StaffordRandFixedSum(n,u=m, nsets=1)
        # r = gen_util_UUniFastDiscard(n,u=m, nsets=1)        
        return pd.DataFrame(*r, columns=['U'] )

    tasks_column_list = [  'C', 'T', 'U','tmp', 'i']

    tasklst = pd.DataFrame(np.zeros((numTasks*numTaskset, len(tasks_column_list))),
                columns=tasks_column_list)
    tasklst['i'] = [i for i in range(0, len(tasklst))]    
    
    myprint("generate_tasklst generate period")
    tasklst['T'] = tasklst['T'].apply(lambda x: periods_loguniform(Tmin, Tmax) )
    myprint("generate_tasklst complete generating period")

    myprint("generate_tasklst generate utilization")
    
    # distr_choices = [pp for i in range(0, numTaskset)]
    # tasklst['U'] = tasklst['i'].apply(lambda i: distr_choices[ int(i/numTasks)] ())    
    for i in range(0, len(tasklst), numTasks):
        # p = genFixSum(n=numTasks, m=numProc, distr=distr_choices[ i//numTasks ])
        p = genFixSum(n=numTasks, m=numProc, distr=uniform_choice_func)
        p.index += i
        tasklst.loc[i:i + numTasks,'U'] = p
    myprint("generate_tasklst complete utilization")

    tasklst['C'] = np.rint(tasklst['U']*tasklst['T'])

    # tasklst.to_csv('data/tasklst{}'.format(time.time()) , index=False)

    return tasklst

def load_tasklst(fname):
    tasklst = pd.read_csv(fname)
    myprint(tasklst)
    return tasklst

def generate_tasksetlst(numProc, numTasks, numTaskset, tasklst, permulst, maxtry_crta):

    taskset_column_list = [  'tsi','U', 'violate_c1cond','violate_c2cond']
    tasksetlst = pd.DataFrame(np.zeros((numTaskset,len(taskset_column_list))),
                columns=taskset_column_list)
    tasksetlst['tsi'] = [i for i in range(0, numTaskset)]        

    myprint("generate_tasksetlst c1/c2 check")
    # U for taskset total utilization
    tasksetlst[['violate_c1cond', 'violate_c2cond','U']] = tasksetlst['tsi'].apply(
        lambda x: taskset_check_c1c2cond(
            x, 
            tasklst.loc[ x*numTasks:(x+1)*numTasks-1, :], 
            m=numProc, 
            permulst=permulst, 
            maxtry_crta=maxtry_crta )
        )
    myprint("generate_tasksetlst complete c1/c2 check")

    return tasksetlst


def taskset_check_c1c2cond(tsidx,  tasklst, m, permulst, maxtry_crta):
    n = tasklst.count
    
    utiltotal = tasklst['U'].sum()
    violate_c1cond = False
    violate_c2cond  = True # if C-RTA is failed on given taskset, the C2 is violated

    ts = tasks.TaskSystem([
        tasks.SporadicTask(ti['C'], ti['T']) for _, ti in tasklst.iterrows() 
        ])    
    # myprint(tasklst)

    # DMPO heuristic schedule
    ts.sort_by_deadline()
    violate_c1cond  = rtalc.is_schedulable_rta_lc(m, ts)
    if (violate_c1cond ):
        return pd.Series(
            ["DMPO RTA-LC", violate_c2cond, utiltotal], 
            index=['violate_c1cond', 'violate_c2cond','U']
            )

    # # DkC heuristic schedule
    # ts.sort_by_deadline_minus_cost()
    # violate_c1cond  = rtalc.is_schedulable_rta_lc(m, ts)
    # if (violate_c1cond ):
    #     # return bSchedulable 
    #     return pd.Series(
    #         ['D-CMPO RTA-LC' , violate_c2cond, utiltotal], 
    #         index=['violate_c1cond', 'violate_c2cond','U']
    #         )

    # ts.sort_by_dkc(m)
    # violate_c1cond  = rtalc.is_schedulable_rta_lc(m, ts)
    # if (violate_c1cond ):
    #     # return bSchedulable 
    #     return pd.Series(
    #         ['DkC RTA-LC' , violate_c2cond, utiltotal], 
    #         index=['violate_c1cond', 'violate_c2cond','U']
    #         )
    
    # OPA w/ DA-LC check
    violate_c1cond  = opa.audsley_opa(ts, m, lambda x: rtalc.is_schedulable_da_lc(m, x))
    if (violate_c1cond ):
        # return bSchedulable         
        return pd.Series(
            ['OPA DA-LC' , violate_c2cond, utiltotal], 
            index=['violate_c1cond', 'violate_c2cond','U']
            )
    
    #violate_c1cond remains False - no violation
    # myprint("no violation on C1")
    # Check for C2 condition by using C_RTA

    for i in range(0, min(maxtry_crta, len(permulst))):
        target_ts_idx = uniform_choice(permulst)
        newts = tasks.TaskSystem([
            tasks.SporadicTask(ti['C'], ti['T']) for _, ti in tasklst.iloc[target_ts_idx].iterrows()])

        bSched = rtalc.is_schedulable_c_rta(m, newts)
        # print("bSched", bSched)
        # print("c-rta i={} bSched={} w/ pa={}".format(i, bSched, target_ts_idx))

        if bSched:
            # Given taskset is schedulable with C-RTA, C2 is not violated
            # Save the random C-RTA scheduleable priority assignment to violate_c2cond column
            violate_c2cond = ' '.join(str(e) for e in target_ts_idx) #tasklst.iloc[target_ts_idx]
            # violate_c2cond = False
            break
    
    return pd.Series(
        [violate_c1cond, violate_c2cond, utiltotal], 
        index=['violate_c1cond', 'violate_c2cond', 'U']
        )

def generate_acceptable_tasksetlst(numProc, numTasks, numTaskset, utilDistr, Tmin, Tmax, maxtry_crta):

    start = timeit.default_timer()
    
    fname_final_tasklst  = 'data/acceptable/fin_tlst_ts{}_m{}_n{}.{}'.format(numTaskset, numProc, numTasks, start)
    fname_final_tasksetlst = 'data/acceptable/fin_tslst_ts{}_m{}_n{}.{}'.format(numTaskset, numProc, numTasks, start)

    permulst = load_permulst(numTasks) 
    
    # To generate the tasklist & tasksetlist structure only       
    final_tasklst = generate_tasklst(numProc=1, numTasks=1, numTaskset=1, Tmin=Tmin, Tmax=Tmax, utilDistr=utilDistr)
    final_tasksetlst = generate_tasksetlst(numProc=1, numTasks=1, numTaskset=1, tasklst=final_tasklst, permulst=permulst, maxtry_crta=maxtry_crta)

    #drop all the tasklst & taskset. keep the variables structure only
    final_tasklst = final_tasklst[0:0]
    final_tasksetlst = final_tasksetlst [0:0]

    batch = 1
    generated_ts = 0
    last_generated_ts = 0
    
    while generated_ts < numTaskset:
        myprint("generate_tasklst")
        tasklst = generate_tasklst(numProc, numTasks, numTaskset*5, utilDistr=utilDistr, Tmin=Tmin, Tmax= Tmax )
        # tasklst = load_tasklst("data/tasklst1638718653.729022")  
        myprint("generate_tasksetlst")
        tasksetlst = generate_tasksetlst(numProc=numProc, numTasks=numTasks, numTaskset=numTaskset*5, tasklst=tasklst, permulst=permulst, maxtry_crta=maxtry_crta)            

        tstmp  = tasksetlst[tasksetlst['violate_c2cond']!=True]
        batch_found_ts = len(tstmp)
        generated_ts += batch_found_ts

        end = timeit.default_timer()

        myprint("B# {} {}/{} ts, found {} ts. {:.2f}ts/10s"
            .format(
                batch, numTaskset-generated_ts, numTaskset,  
                batch_found_ts,
                generated_ts/(end-start)*10
                ))

        # print("Working on batch {} for {}/{} taskset. Genearting {} tasks (m={},n={}). Found {} acceptable taskset."
        #     .format(batch,
        #     numTaskset-generated_ts, numTaskset, 
        #     numTasks*numTaskset, 
        #     numProc, numTasks , batch_found_ts))

        if batch_found_ts == 0:
            continue

        for tsi in tstmp['tsi']:
            titmp = tasklst.loc[ tsi*numTasks:(tsi+1)*numTasks-1, :]
            final_tasklst = final_tasklst.append(titmp, ignore_index=True)

        final_tasksetlst = final_tasksetlst.append(tasksetlst[tasksetlst['violate_c2cond']!=True], ignore_index = True)        

        batch += 1

        if  generated_ts - last_generated_ts  >= 20:
            last_generated_ts = generated_ts
            myprint("Save interim generated taskset/tasks")
            final_tasklst.to_csv(fname_final_tasklst , index=False)
            final_tasksetlst.to_csv( fname_final_tasksetlst, index=False)
    try:
        os.remove(fname_final_tasklst)
        os.remove(fname_final_tasksetlst)
    except:
        pass
    final_tasksetlst['tsi'] = [i for i in range(0, generated_ts)]        
    final_tasklst['i'] = [i for i in range(0, len(final_tasklst))]    

    return final_tasksetlst, final_tasklst


if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    print(os.getcwd(), sys.path)
    import time

    myprint("Generate all the task set")
    Tmin = 10
    Tmax = 10000
    

    # numProc = 2
    # numTasks = 9
    # numTaskset = 1000
    # numThread = 1
    # MaxTry_CRTA = 5

    numProc = int(sys.argv[1])
    numTasks = int(sys.argv[2])
    numTaskset = int(sys.argv[3])
    numThread = int(sys.argv[4])
    MaxTry_CRTA = int(sys.argv[5])
    myprint("Gen options: numProc={}, numTasks={}, numTaskset={}, numThread={}".format(numProc,numTasks, numTaskset, numThread))

    

    utilization_distribution_choices = [
        # bimodal(0.5,1, 0.1),
        # bimodal(0.5,1, 0.3),
        # bimodal(0.5,1, 0.5),
        # bimodal(0.5,1, 0.7),
        # bimodal(0.5,1, 0.9),
        # exponential(0.5,1, 0.1),
        # exponential(0.5,1, 0.3),
        # exponential(0.5,1, 0.5),
        # exponential(0.5,1, 0.7),
        # exponential(0.5,1, 0.9)
        
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

    myprint("END----")
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
    t.to_csv('data/acceptable/fin_tlst_ts{}_m{}_n{}.{}'.format(numTaskset, numProc, numTasks, tm) , index=False)
    ts.to_csv('data/acceptable/fin_tslst_ts{}_m{}_n{}.{}'.format(numTaskset, numProc, numTasks, tm) , index=False)

    # print(timeit.timeit("generate_acceptable_tasksetlst( "
    #                 "numProc=2, numTasks=5, "
    #                 "numTaskset=100,"
    #                 " utilDistr=utilization_distribution_choices,"
    #                 " Tmin=10, Tmax=10000, maxtry_crta=5)",
    #     setup="from __main__ import generate_acceptable_tasksetlst, utilization_distribution_choices",
    #     number=2))