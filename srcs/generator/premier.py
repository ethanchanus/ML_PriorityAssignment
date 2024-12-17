if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    print(sys.path)

import numpy
from generator.dist import * 
from rtmodel import tasks
from schedule import rta_lc_guan09 as rtalc
from schedule import audsley_opa as opa
import timeit
import threading
from util.log import myprint

def load_permulst(numTasks):
    permulst = np.loadtxt("data/permu{}.csv".format(numTasks), dtype=np.int8 , delimiter=',')
    return permulst 

def calc_syshaz(m, pai, targettlst):
    #calculate system hazard of the taskset by by using response time RTA-LC

    if type(targettlst ) is tasks.TaskSystem:
        ts= targettlst
    else:
        ts = tasks.TaskSystem([
            tasks.SporadicTask(
                ti['C'], ti['T']) 
                for _, ti in targettlst.iloc[pai].iterrows()
            ])  
    bSched = rtalc.is_schedulable_rta_lc(m, ts)    
    if not bSched:
        return m+1
    
    syshaz = [ti.response_time/ti.period for ti in ts]
    syshaz = max(syshaz)
    return syshaz


def calc_minsyshaz_heristic_pa(tsidx, m, targettlst):

    if type(targettlst ) is tasks.TaskSystem:
        ts= targettlst
    else:
        ts = tasks.TaskSystem([
            tasks.SporadicTask(
                ti['C'], ti['T']) 
                for _, ti in targettlst.iterrows()
            ]) 

    heuristic_pa=[lambda x: ts.sort_by_deadline, lambda x: ts.sort_by_deadline_minus_cost(), lambda x: ts.sort_by_dkc (m)]
    pa_syshaz = [] 
    for pa in heuristic_pa:
        pa(0)
        
        # Calculate the system hazard of each heursitic assignment in heuristic_pa
        # -> Try to find the best system hazard as we can from heursitic assignment
        pa_syshaz += [ calc_syshaz(m, pai=None, targettlst=ts) ]
    
    return min(pa_syshaz)


def find_premier(tsidx, numProc, permulst, targettlst):
    # Exhaustive search for the System hazard/premier of all task's assignment permutation

    passign_column_list = ['pai', 'passign', 'syshaz']

    passignlst = pd.DataFrame(np.zeros((len(permulst), len(passign_column_list))),
                columns=passign_column_list)
    passignlst ['pai'] = [i for i in range(0, len(passignlst))]
    passignlst['passign']  = passignlst ['pai'].apply(lambda pai:  permulst[pai] )
    passignlst['syshaz'] = passignlst ['passign'].apply(lambda passign:  calc_syshaz(numProc, passign, targettlst))

    premier = passignlst['syshaz'].min()
    passign = passignlst[passignlst['syshaz']==premier]['passign'].head(1)
    # passign =list(passign)
 
    r = pd.Series([premier, *passign.tolist()], index=['premier', 'passign'] )
    return r 
    

def find_pseudo_premier(tsidx, numProc, permulst, targettlst):
    
    
    def calc_pseudo_premier(numProc, passign, minsyshaz_heristic_pa, targettlst, bFound):

        if bFound[0]:
            # found, ignore the rest of taskset, assign those syshaz to numproc+1 (which are not schedulable)
            return numProc+1

        syshaz = calc_syshaz(numProc, passign, targettlst)
        if syshaz < minsyshaz_heristic_pa:
            bFound[0] =True

        return syshaz

   
    minsyshaz_heristic_pa = calc_minsyshaz_heristic_pa(tsidx, m=numProc, targettlst=targettlst)

    passign_column_list = ['pai', 'passign', 'syshaz']

    passignlst = pd.DataFrame(np.zeros((len(permulst), len(passign_column_list))),
                columns=passign_column_list)
    
    passignlst ['pai'] = [i for i in range(0, len(passignlst))]
    passignlst['passign']  = passignlst ['pai'].apply(lambda pai:  permulst[pai] )

    # find the a first assignment thas has system hazard be better than the minsyshaz_heristic_pa
    
    # shuffle the passign list before finding pseudo premier
    passignlst = passignlst.sample(frac=1)#.reset_index(drop=True)    
    
       
    bFoundPseudoPremier = [False] # for ref passing purpose
    passignlst['syshaz'] = passignlst ['passign'].apply(
        lambda passign:  
            calc_pseudo_premier(
                numProc, passign, minsyshaz_heristic_pa, targettlst, bFoundPseudoPremier))
    
    premier = passignlst['syshaz'].min()
    passign = passignlst[passignlst['syshaz']==premier]['passign'].head(1)

    r = pd.Series(    [ premier, *passign.tolist()],    index=['pseudo_premier', 'pseudo_passign'] )
    return r 


# For testing purpose
if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    print(os.getcwd(), sys.path)
    import time
    import pandas as pd
    import numpy as np

    numProc = 2
    numTasks = 7
    numTaskset = 1000
    numThread = 20    

    permulst = load_permulst(numTasks)     

    tlst = pd.read_csv("data/acceptable/m2n7/fin_tlst_ts5000_m2_n7.1638826047.2074971")
    tlst['i'] = [i for i in range(0, len(tlst))]  

    tslst = pd.read_csv("data/acceptable/m2n7/fin_tslst_ts5000_m2_n7.1638826047.2074971")
    tslst['tsi'] = [i for i in range(0, len(tslst))]            

    tslst = tslst[0:1]
    tslst['minsyshaz_heristic_pa'] = tslst['tsi'].apply(lambda tsidx:
        calc_minsyshaz_heristic_pa(tsidx, numProc, targettlst = tlst.loc[tsidx*numTasks:(tsidx+1)*numTasks - 1])
        )
   
    tslst[['pseudo_premier', 'pseudo_passign']] = tslst['tsi'].apply(lambda tsidx:
        find_pseudo_premier
            (numProc, permulst=permulst,
            targettlst = tlst.loc[tsidx*numTasks:(tsidx+1)*numTasks - 1])
        )
    
    tslst[['premier', 'passign']] =tslst['tsi'].apply(lambda tsidx:
        find_premier
            (numProc, permulst=permulst,
            targettlst = tlst.loc[tsidx*numTasks:(tsidx+1)*numTasks - 1])
        )
    tslst.to_csv('test.csv')
    print(tslst)    