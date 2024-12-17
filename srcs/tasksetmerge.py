from generator.gen import *
from rtmodel import tasks
from schedule import rta_lc_guan09 as rtalc
from schedule import audsley_opa as opa
import timeit
import threading
from util.log import myprint
from generator.permu import *
import os


numTasks = 4
filetlst = [
    'data/acceptable/m2n4/1/final/tlst_m2n4.csv',
    'data/acceptable/m2n4/2/final/tlst_m2n4.csv',
    'data/acceptable/m2n4/3/final/tlst_m2n4.csv',
    'data/acceptable/m2n4/4/final/tlst_m2n4.csv',
    'data/acceptable/m2n4/5/final/tlst_m2n4.csv',
    'data/acceptable/m2n4/6/final/tlst_m2n4.csv',
    'data/acceptable/m2n4/7/final/tlst_m2n4.csv'
    ]

filetslst =[    
    'data/acceptable/m2n4/1/final/tslst_m2n4.csv',
    'data/acceptable/m2n4/2/final/tslst_m2n4.csv',
    'data/acceptable/m2n4/3/final/tslst_m2n4.csv',
    'data/acceptable/m2n4/4/final/tslst_m2n4.csv',
    'data/acceptable/m2n4/5/final/tslst_m2n4.csv',
    'data/acceptable/m2n4/6/final/tslst_m2n4.csv',
    'data/acceptable/m2n4/7/final/tslst_m2n4.csv'
    ]

filetslstout  = 'data/acceptable/m2n4/final/tslst_m2n4_final.csv'
filetlstout = 'data/acceptable/m2n4/final/tlst_m2n4_final.csv'

# numTasks = 5
# filetlst = [
#     'data/acceptable/m2n5/1/final/tlst_m2n5.csv',
#     'data/acceptable/m2n5/2/final/tlst_m2n5.csv',
#     'data/acceptable/m2n5/3/final/tlst_m2n5.csv',
#     'data/acceptable/m2n5/4/final/tlst_m2n5.csv',
#     'data/acceptable/m2n5/5/final/tlst_m2n5.csv',
#     ]

# filetslst =[    
#     'data/acceptable/m2n5/1/final/tslst_m2n5.csv',
#     'data/acceptable/m2n5/2/final/tslst_m2n5.csv',
#     'data/acceptable/m2n5/3/final/tslst_m2n5.csv',
#     'data/acceptable/m2n5/4/final/tslst_m2n5.csv',
#     'data/acceptable/m2n5/5/final/tslst_m2n5.csv',
#     ]
# filetslstout  = 'data/acceptable/m2n5/final/tslst_m2n5_final.csv'
# filetlstout = 'data/acceptable/m2n5/final/tlst_m2n5_final.csv'


# numTasks = 6
# filetlst = [
#     'data/acceptable/m2n6/1/final/tlst_m2n6_test.csv',
#     'data/acceptable/m2n6/2/final/tlst_m2n6_test.csv',
#     'data/acceptable/m2n6/3/final/tlst_m2n6_test.csv',
#     'data/acceptable/m2n6/4/final/tlst_m2n6_test.csv',
#     'data/acceptable/m2n6/5/final/tlst_m2n6_test.csv',
#     'data/acceptable/m2n6/6/final/tlst_m2n6_test.csv',
#     'data/acceptable/m2n6/7/final/tlst_m2n6_test.csv',
#     'data/acceptable/m2n6/8/final/tlst_m2n6_test.csv',
#     ]

# filetslst =[    
#     'data/acceptable/m2n6/1/final/tslst_m2n6_test.csv',
#     'data/acceptable/m2n6/2/final/tslst_m2n6_test.csv',
#     'data/acceptable/m2n6/3/final/tslst_m2n6_test.csv',
#     'data/acceptable/m2n6/4/final/tslst_m2n6_test.csv',
#     'data/acceptable/m2n6/5/final/tslst_m2n6_test.csv',
#     'data/acceptable/m2n6/6/final/tslst_m2n6_test.csv',
#     'data/acceptable/m2n6/7/final/tslst_m2n6_test.csv',
#     'data/acceptable/m2n6/8/final/tslst_m2n6_test.csv',
#     ]
# filetslstout  = 'data/acceptable/m2n6/final/tslst_m2n6_final.csv'
# filetlstout = 'data/acceptable/m2n6/final/tlst_m2n6_final.csv'


# numTasks = 7
# filetlst = [
#     'data/acceptable/m2n7/1/final/tlst_m2n7.csv',
#     'data/acceptable/m2n7/2/final/tlst_m2n7.csv',
#     'data/acceptable/m2n7/3/final/tlst_m2n7.csv',
#     'data/acceptable/m2n7/4/final/tlst_m2n7.csv',
#     'data/acceptable/m2n7/5/final/tlst_m2n7.csv',
#     'data/acceptable/m2n7/6/final/tlst_m2n7.csv',
#     'data/acceptable/m2n7/7/final/tlst_m2n7.csv',
#     ]

# filetslst =[    
#     'data/acceptable/m2n7/1/final/tslst_m2n7.csv',
#     'data/acceptable/m2n7/2/final/tslst_m2n7.csv',
#     'data/acceptable/m2n7/3/final/tslst_m2n7.csv',
#     'data/acceptable/m2n7/4/final/tslst_m2n7.csv',
#     'data/acceptable/m2n7/5/final/tslst_m2n7.csv',
#     'data/acceptable/m2n7/6/final/tslst_m2n7.csv',
#     'data/acceptable/m2n7/7/final/tslst_m2n7.csv',
#     ]
# filetslstout  = 'data/acceptable/m2n7/final/tslst_m2n7_final.csv'
# filetlstout = 'data/acceptable/m2n7/final/tlst_m2n7_final.csv'


# numTasks = 8
# filetlst = [
#     'data/acceptable/m2n8/1/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8/2/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8/3/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8/4/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8/5/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8/6/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8/7/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8/8/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8/9/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8/10/final/tlst_m2n8.csv',
#     ]

# filetslst =[    
#     'data/acceptable/m2n8/1/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8/2/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8/3/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8/4/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8/5/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8/6/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8/7/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8/8/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8/9/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8/10/final/tslst_m2n8.csv',
#     ]
# filetslstout  = 'data/acceptable/m2n8/final/tslst_m2n8_final.csv'
# filetlstout = 'data/acceptable/m2n8/final/tlst_m2n8_final.csv'


# numTasks = 8
# filetlst = [
#     'data/acceptable/m2n8_pseudo/1/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/2/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/3/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/4/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/5/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/6/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/7/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/8/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/9/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/10/final/tlst_m2n8.csv',
#     ]

# filetslst =[    
#     'data/acceptable/m2n8_pseudo/1/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/2/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/3/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/4/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/5/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/6/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/7/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/8/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/9/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/10/final/tslst_m2n8.csv',
#     ]
# filetslstout  = 'data/acceptable/m2n8_pseudo/final/tslst_m2n8_final.csv'
# filetlstout = 'data/acceptable/m2n8_pseudo/final/tlst_m2n8_final.csv'


# numTasks = 9
# filetlst = [
#     'data/acceptable/m2n8_pseudo/1/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/2/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/3/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/4/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/5/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/6/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/7/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/8/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/9/final/tlst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/10/final/tlst_m2n8.csv',
#     ]

# filetslst =[    
#     'data/acceptable/m2n8_pseudo/1/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/2/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/3/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/4/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/5/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/6/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/7/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/8/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/9/final/tslst_m2n8.csv',
#     'data/acceptable/m2n8_pseudo/10/final/tslst_m2n8.csv',
#     ]
# filetslstout  = 'data/acceptable/m2n8_pseudo/final/tslst_m2n8_final.csv'
# filetlstout = 'data/acceptable/m2n8_pseudo/final/tlst_m2n8_final.csv'



assert(len(filetlst) == len(filetslst))


tslst = None
tlst = None

for _, (tsfname, tfname) in enumerate(zip(filetslst, filetlst)):
    if not os.path.exists(tfname):
        print (tfname, tfname, " not existed")
        continue
    print(tsfname, tfname)
    ts = pd.read_csv(tsfname)
    tl = pd.read_csv(tfname)
    if tslst is None:
        tslst = ts
        tlst = tl
    else:
        tslst = tslst.append(ts)
        tlst = tlst .append(tl)

assert (len(tslst) * numTasks == len(tlst))



tslst['tsi'] = [i for i in range(0, len(tslst))]
tlst['i'] = [i for i in range(0, len(tlst))]

tslst.to_csv(filetslstout)
tlst.to_csv(filetlstout)
print(tslst)

print("#{} taskset, #{} tasks. Write to {} and {}".format(len(tslst), len(tlst), filetslstout, filetlstout))