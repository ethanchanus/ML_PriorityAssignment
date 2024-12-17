if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    print(sys.path)


# from socket import PACKET_LOOPBACK
from sys import path_importer_cache
import pandas
import timeit
from util.log import myprint
import os
import pandas as pd
import numpy as np
# firom generator import permu.load_permulst
from sklearn.utils import shuffle
import re

filetslst = [
    '',
    '',
    '',
    '',
    'data/acceptable/m2n4/final/tslst_m2n4_final.csv',
    'data/acceptable/m2n5/final/tslst_m2n5_final.csv',
    'data/acceptable/m2n6/final/tslst_m2n6_final.csv',
    'data/acceptable/m2n7/final/tslst_m2n7_final.csv',
    # 'data/acceptable/m2n8/final/tslst_m2n8_final.csv'
    # 'data/acceptable/m2n8/final/tslst_m2n8_pseudo_final.csv'
    'data/acceptable/m2n8_pseudo/final/tslst_m2n8_final.csv'
]

filetlst = [
    '',
    '',
    '',
    '',
    'data/acceptable/m2n4/final/tlst_m2n4_final.csv',
    'data/acceptable/m2n5/final/tlst_m2n5_final.csv',
    'data/acceptable/m2n6/final/tlst_m2n6_final.csv',
    'data/acceptable/m2n7/final/tlst_m2n7_final.csv',
    # 'data/acceptable/m2n8/final/tlst_m2n8_final.csv'
    # 'data/acceptable/m2n8/final/tlst_m2n8_pseudo_final.csv'
    'data/acceptable/m2n8_pseudo/final/tlst_m2n8_final.csv'
    
    ]

class PalData:
    def __init__(self, numProc=2, numTasks=4) -> None:
        self.m = numProc
        self.n = numTasks
        self.nextbatchidx = 0

        # self.load_csv()

        pass
    
    def next_batch(self, batchsize=-1):
        
        self.batchsize = min(batchsize, len(self.tslstnp)) if batchsize != -1 else len(self.tslstnp)

        X = self.tlstnp[self.nextbatchidx:self.nextbatchidx+batchsize]
        Y = self.tslstnp[self.nextbatchidx:self.nextbatchidx+batchsize]        

        print("Acquired {} samples".format( len(X)) )

        self.nextbatchidx += batchsize

        return X, Y

    def get_tslen(self):
        return len(self.tslst)
    
    def remove_unscheduable(self):
        
        ts = self.tslst
        tl = self.tlst

        col = 'pseudo_premier' if 'pseudo_premier' in ts.columns else 'premier'
        
        tstmp  = ts[ts[col] <= 1]
        ti = []
        
        for tsi in tstmp['tsi']:
            ti += list(range(tsi*self.n, (tsi+1)*self.n))
        
        self.tslst = tstmp
        self.tlst = self.tlst.loc[ti]
        self.tslst.reset_index()
        self.tlst.reset_index()
        
    def get_pa_col_name(self):
        return 'passign' if 'passign' in self.tslst.columns else 'pseudo_passign'
    
    def convert_to_numpy(self):
        d = self.tslst[self.get_pa_col_name()]
        d = d.apply(lambda pa: (eval(re.sub('\s+', ',', pa))))
        d = np.array(d.to_list())
        
        # tslstnp -> tslst numpy
        self.tslstnp = d #d.to_numpy()

        d = self.tlst[['C','T']].to_numpy()
        d = d.reshape((len(self.tslst), self.n, 2))

        self.tlstnp = d

        assert(len(self.tslstnp) == len(self.tlstnp))
        assert(len(self.tlstnp[0]) == self.n)
        assert(len(self.tlstnp[0][0]) == 2 )
        
    def save_numpy_tofile(self,tsfname, tfname):
        print("Dump #{} tasksets to {} and #{} tasks to file {}".format(
            len(self.tslstnp),tsfname,
            len(self.tlstnp),tfname))
       
        np.save(tsfname, self.tslstnp)
        np.save(tfname, self.tlstnp)

    def load_numpy_fromfile(self,tsfname, tfname):        
        
        self.tslstnp= np.load(tsfname )
        self.tlstnp= np.load(tfname )
        
        print("Load #{} tasksets from {} and #{} tasks from file {}".format(
            len(self.tslstnp),tsfname,
            len(self.tlstnp),tfname))
        
    def load_csv(self ):
        tsfname =  filetslst[self.n]
        tfname = filetlst[self.n]
        self.tslst = pd.read_csv(tsfname)
        self.tlst = pd.read_csv(tfname)
        assert(len(self.tslst)*self.n == len(self.tlst))
        assert(len(self.tslst)*self.n == len(self.tlst))
        # self.tslst=self.tslst.iloc[0:10,:]
        # self.tlst=self.tlst.iloc[0:10*self.n,:]
        print("Load {} taskset from {} and {} tasks from {}".format(
            len(self.tslst),tsfname,
            len(self.tlst),tfname))
        
        
        self.remove_unscheduable()
        print("Filter out unschedulable tasksets, remaining {} taskset and {} tasks ".format(
            len(self.tslst),
            len(self.tlst)))
        
        # live with this
        print("# of dupplicated taskset: ", self.tslst.duplicated(subset=['U']).sum())

        self.convert_to_numpy()
        
    def data_aug(self, p=5):
        
        new_tslst = pd.DataFrame(data=np.repeat(self.tslst.values, p, axis=0), columns=self.tslst.columns)
        new_tlst = pd.DataFrame(data=np.repeat(self.tlst.values, p, axis=0), columns=self.tlst.columns)
        # new_tslst = pd.DataFrame(data=np.repeat(self.tslst.iloc[0:10,:].values, p, axis=0), columns=self.tslst.columns)
        # new_tlst = pd.DataFrame(data=np.repeat(self.tlst.iloc[0:10*self.n,:].values, p, axis=0), columns=self.tlst.columns)
        
        newtidx = []
        pa_col_name = self.get_pa_col_name()
        for tsidx, ts in new_tslst.iterrows():
            if tsidx % 5000 == 0:
                print("Data augmentation p={}, total #{}/#{}".format(p, tsidx, len(new_tslst)))
                
            pa = ts[pa_col_name]
            pa = eval(re.sub('\s+', ',', pa))            
            
            tidx_old = list(range((tsidx//p)*self.n, (tsidx//p+1)*self.n))
            tidx_new = list(range((tsidx)*self.n, (tsidx+1)*self.n))
            
            tidx_pa_sorted = [tidx_old[i] for i in pa]
            pa_shuffle = shuffle(pa)
            tidx_shuffle = [tidx_pa_sorted[i] for i in np.argsort(pa_shuffle)]
            ts[pa_col_name] = str(pa_shuffle).replace(',',' ')
            new_tslst.loc[tsidx] = ts
            new_tlst.iloc[ tidx_new, :] = self.tlst.iloc[tidx_shuffle, :].values.tolist()            
            
            assert(self.tlst.iloc[tidx_old].iloc[pa]['C'].values.tolist() ==  new_tlst.iloc[tidx_new].iloc[pa_shuffle]['C'].values.tolist())
            
        self.tslst = new_tslst
        self.tlst = new_tlst
        self.convert_to_numpy()
    

from keras.utils.np_utils import to_categorical
if __name__ == "__main__":
    p = PalData(numProc=2, numTasks=4)
    X, Y = p.next_batch(batchsize=10)
    print(X)
    print(Y)

    # YY = []
    # for y in Y:
    #     YY.append(to_categorical(y))
    #     YY = np.asarray(YY)
    # print(YY)


