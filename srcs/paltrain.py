
import sys
import tensorflow as tf

from pal.paldata import PalData
from pal.palmodel import PalModel


numProcs = sys.argv[0]
numTasks = sys.argv[1]

datasets = {"m2n4": [54000, 5900],
        "m2n5" : [960000, 11830],
        "m2n6" : [300000,4990],
        "m2n7" : [120000, 5315]}

print("preparing dataset...")
paldata = PalData(numProc=numProcs, numTasks=numTasks)

# paldata.load_csv()
# paldata.data_aug()
# paldata.save_numpy_tofile("paldata_m{}_n{}_ts_preproc.npy".format(numProcs, numTasks), 
#                           "paldata_m{}_n{}_tl_preproc.npy".format(numProcs, numTasks)) 

paldata.load_numpy_fromfile("data/paldata_m{}_n{}_ts_preproc.npy".format(numProcs, numTasks), 
                          "data/paldata_m{}_n{}_tl_preproc.npy".format(numProcs, numTasks)) 


# with tf.device('/device:GPU:2'):
   
ds = datasets["m{}n{}".format(numProcs, numTasks)]
X, Y = paldata.next_batch(ds[0])
X_test, Y_test = paldata.next_batch(ds[1])


palmodel = PalModel(numProcs=numProcs, numTasks=numTasks, nb_epochs=60, leanring_rate=0.01)
palmodel.train(X, Y)
palmodel.save_model()
# palmodel.load_model()
# accuracy, _, Y_test_hat_scheduable = palmodel.eval(X, Y)

# print(accuracy)