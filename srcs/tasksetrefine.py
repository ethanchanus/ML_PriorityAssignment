from numpy import NaN
from generator.gen import *
from generator.premier import *
from rtmodel import tasks
from schedule import rta_lc_guan09 as rtalc
# from schedule import audsley_opa as opa
import timeit
import threading
from util.log import myprint
import math

def taskfile_combine(numTasks, datadir):

    datafiles = [ f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir,f)) ]
    timestamplst = list(set([f.split('.', 1)[1] for f in datafiles]))

    # taskset file list
    tsfilelst = list(filter(lambda x: x.find("tslst") >=0, datafiles))
    # task file list
    tfilelst = list(filter(lambda x: x.find("tlst") >=0, datafiles))
    
    combined_tslst = None
    combined_tlst = None
    for t in timestamplst:
        tsfile = list(filter(lambda x: x.find(t) >=0, tsfilelst))[0]
        tfile = list(filter(lambda x: x.find(t) >=0, tfilelst)) [0]
        myprint("Get tasksetlst from {}, tasklist from {}".format(tsfile, tfile))
        tslst = pd.read_csv(datadir+tsfile)
        tlst = pd.read_csv(datadir+tfile)

        myprint("Total {} task set, expecting {} tasks, got {} tasks".format(len(tslst), len(tslst)*numTasks, len(tlst)))
        # Sanity check 
        if len(tslst)*numTasks != len(tlst):
            myprint("---> INGORE: Total {} task set, expecting {} tasks but got {} tasks".format(len(tslst), len(tslst)*numTasks, len(tlst)))
            continue
            
        if combined_tslst is None:
            combined_tslst = tslst
            combined_tlst = tlst
        else: 
            combined_tslst = combined_tslst.append(tslst, ignore_index=True)
            combined_tlst =combined_tlst.append(tlst, ignore_index=True)


        myprint('---')

    if (len(combined_tslst)*numTasks != len(combined_tlst)) or (combined_tslst['U'].sum() -  combined_tlst['U'].sum() > 0.001):
        myprint("---> Error when combining all the data files")
        return None, None    

    combined_tslst['tsi'] = [i for i in range(0, len(combined_tslst))]
    combined_tlst['i'] = [i for i in range(0, len(combined_tlst))]

    myprint("--->  Total {} task set, total {} tasks".format(len(combined_tslst), len(combined_tlst)))
    myprint("Diff U={}".format( combined_tslst['U'].sum() -  combined_tlst['U'].sum()))
    return combined_tslst, combined_tlst

if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    print(os.getcwd(), sys.path)
    import time

    myprint("Generate all the task set")
    Tmin = 10
    Tmax = 10000


    numProc = int(sys.argv[1])
    numTasks = int(sys.argv[2])
    premierType = sys.argv[3]
    dataDir = sys.argv[4]
    fnameOut = sys.argv[5]
    

    # numProc = 2
    # numTasks = 5
    # dataDir = "data/acceptable/m2n5_test/"
    # fnameOut="m2n5_test.csv"
    # premierType = "pseudo_premier"
    # # # premierType = "premier"
    # fnameOut = "m2n5_test.csv"
    tsPerBatch = 100

    tlstfnameOut = dataDir+ "final/tlst_" + fnameOut
    tslstfnameOut = dataDir+ "final/tslst_" + fnameOut

    myprint("{} options: numProc={}, numTasks={}, premierType={}, dataDir={}, fnameOut={}".format(sys.argv[0],numProc, numTasks, premierType, dataDir, fnameOut))
    
    # python tasksetrefine.py 2 5 pseudo_premier data/acceptable/m2n5_test/ m2n5_test.csv
    
    permulst = load_permulst(numTasks)
    if premierType=='pseudo_premier':
        fn = find_pseudo_premier
        collst = ['pseudo_premier', 'pseudo_passign']
    else:
        fn = find_premier
        collst = ['premier', 'passign']

    # create final output dir
    try:
        os.mkdir(dataDir+"final")
    except:
        pass 

    
    if os.path.exists(tlstfnameOut) and os.path.exists(tslstfnameOut):
        myprint('Resume from taskset file {} and task list file {}'.format(tslstfnameOut, tlstfnameOut))
        combined_tslst=pd.read_csv(tslstfnameOut)
        combined_tlst=pd.read_csv(tlstfnameOut)
        print(len(combined_tslst), len(combined_tlst))
    else:
        myprint('Combining data files')    
        combined_tslst, combined_tlst = taskfile_combine(numTasks=numTasks, datadir=dataDir)
        for c in collst:
            if c not in combined_tslst:
                combined_tslst[c] = NaN
    
    
    myprint('Calcualte {} for {} taskset, {} tasks'.format(premierType, len(combined_tslst), len(combined_tlst)))

    l = len(combined_tslst)
    
    batchlst = [ [i for i in range(b*tsPerBatch, (b+1)*tsPerBatch) ] for b in range(0, l//tsPerBatch) ] 
    batchlst += [ [j for j in range(tsPerBatch*(l//tsPerBatch), l)]] if l%tsPerBatch >0 else []

    for b, r in enumerate(batchlst):
        tmp = combined_tslst.iloc[r][['tsi', collst[0], collst[1]]]
        combined_tslst.loc[r, collst] = tmp['tsi'].apply(lambda tsidx :
                fn
                    (tsidx, numProc, permulst=permulst,
                    targettlst = combined_tlst.loc[tsidx*numTasks:(tsidx+1)*numTasks - 1])
                    if math.isnan(tmp.loc[tsidx, collst[0]]) else tmp.loc[tsidx, collst] 
                )
        myprint('B#{} complete {}/{} taskset, write: {}final/<tslst_, tlst_>/{}'.format(b, len(r)*b,l,  dataDir,  fnameOut))
        combined_tslst.to_csv(tslstfnameOut)
        combined_tlst.to_csv(tlstfnameOut)
