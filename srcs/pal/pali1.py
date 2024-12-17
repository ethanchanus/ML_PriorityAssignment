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
import pandas as pd



def pali1_find_new_pseudo_premier(nFind, numProc, numTasks, tslst, tlst, Tmin, Tmax, maxtry):
    tsi=0

    i1foundlst = pd.DataFrame(columns=['tsi','newtask_c','newtask_t','newtask_taskhaz'] )

    nFound = 0
    newtask = tasks.SporadicTask(0, 0)
    while (len(i1foundlst) < nFind) and (tsi< len(tslst)):
        syshaz = tslst.loc[tsi, 'pseudo_premier']
        passign = list(*tslst.loc[tsi, 'pseudo_passign'])

        # assign newtask with lowest priority
        
        tmp = tlst.loc[tsi*numTasks:(tsi+1)*numTasks-1, : ]
        tmp=tmp.iloc[passign, :]
        ts = tasks.TaskSystem([ tasks.SporadicTask(ti['C'], ti['T']) for _, ti in tmp.iterrows()  ] + [newtask]) 
        
        numTry=0
        while numTry < maxtry:
            newTi = int(periods_loguniform(Tmin, Tmax))
            newtask.deadline = newTi
            newtask.period = newTi            
            newCi = 0       
            
            newtaskhazlst = []
            for c in range (1, newTi+1):
                # O(n), use bin_search for o(logn)
                newtask.cost = c
                # bScheduleable = 
                bSched = rtalc.is_schedulable_rta_lc(numProc, ts)
                if not bSched:
                    newtaskhazlst += [newTi + 1]
                    break
                else:
                    newtaskhazlst += [newtask.response_time/newtask.period]

                # print(tsi, "try ", numTry, " found", nFound,' syshaz ', syshaz, newtask.response_time, newtask.period, c,newTi)

                if newtaskhazlst[-1] > syshaz:
                    break
                
            try:
                newtaskhaz = max(filter(lambda i: i <= syshaz, newtaskhazlst))
            except:
                #not found
                numTry += 1
                continue

            #found
            newCi = newtaskhazlst.index(newtaskhaz) + 1 # since c start from 1
            break

        if numTry < maxtry:
            #found
            i1foundlst= i1foundlst.append(
                {'tsi': tsi,
                'newtask_c':newCi,
                'newtask_t':newTi,
                'newtask_taskhaz':newtaskhaz
                },ignore_index=True)
            print (tsi, newTi, newCi, syshaz, newtaskhaz, newtaskhazlst[-1] )
            # nFound += 1
        else:
            print(tsi, "not found")

        tsi += 1
    
    print(i1foundlst)


if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    print(os.getcwd(), sys.path)
    import time
    from generator.premier import *

    
    nFind = 10
    numTasks = 7
    maxTry = 5
    numProc = 2
    Tmin = 10
    Tmax = 10000
    permulst = load_permulst(numTasks)    
    
    tlst = pd.read_csv("data/acceptable/m2n7/fin_tlst_ts5000_m2_n7.1638826047.2074971")
    tlst['i'] = [i for i in range(0, len(tlst))]  

    tslst = pd.read_csv("data/acceptable/m2n7/fin_tslst_ts5000_m2_n7.1638826047.2074971")
    tslst['tsi'] = [i for i in range(0, len(tslst))]        

    tslst = tslst[0:5]
    # tslst['minsyshaz_heristic_pa'] = tslst['tsi'].apply(lambda tsidx:
    #     calc_minsyshaz_heristic_pa(numProc, targettlst = tlst.loc[tsidx*numTasks:(tsidx+1)*numTasks - 1])
    #     )
   
    tslst[['pseudo_premier', 'pseudo_passign']] = tslst['tsi'].apply(lambda tsidx:
        find_pseudo_primer
            (numProc, permulst=permulst,
            targettlst = tlst.loc[tsidx*numTasks:(tsidx+1)*numTasks - 1])
        )
    
    # tslst[['premier', 'passign']] =tslst['tsi'].apply(lambda tsidx:
    #     find_primer
    #         (numProc, permulst=permulst,
    #         targettlst = tlst.loc[tsidx*numTasks:(tsidx+1)*numTasks - 1])
    #     )

    pali1_find_new_pseudo_premier(nFind=10, numProc=numProc, numTasks=numTasks,  tslst = tslst, tlst = tlst, Tmin=Tmin, Tmax=Tmax, maxtry=maxTry)