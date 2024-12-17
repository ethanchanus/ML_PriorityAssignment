from keras import layers
from keras.models import Model
from keras.layers import LSTM, Input
from keras.utils.np_utils import to_categorical
from pointernet.PointerLSTM import PointerLSTM
import pickle
import numpy as np
import keras
from schedule import rta_lc_guan09 as rtalc
from rtmodel import tasks
import tensorflow as tf


class PalModel():
    def __init__(self, numProcs=2, numTasks=4, hidden_size=512, nb_epochs=5, leanring_rate=0.01, batch_size=512) -> None:
        self.m = numProcs
        self.n = numTasks
        
        self.hidden_size = hidden_size
        self.nb_epochs = nb_epochs
        self.learning_rate = leanring_rate
        self.batch_size = batch_size
        
        seq_len = self.n #10

        print("Building PAL model...")
        main_input = Input(shape=(seq_len, 2), name='main_input')

        encoder,state_h, state_c = LSTM(hidden_size,return_sequences = True, name="encoder",return_state=True)(main_input)

        decoder = PointerLSTM(hidden_size, name="decoder")(encoder,states=[state_h, state_c])

        model = Model(main_input, decoder)
        model.compile(optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy'])

        print(model.summary())
        self.model = model

        pass
    
    def train(self, X, Y):
        
        # hidden_size=512, nb_epochs=5, leanring_rate=0.01, batch_size=512
        YY = to_categorical(Y)

        # cp_callback = tf.keras.callbacks.ModelCheckpoint(
        #     filepath='model_weight_m{}n{}.hdf5'.format(self.m, self.n), 
        #     verbose=1, 
        #     # save_weights_only=True,
        #     # save_freq= int(5)
        #     )
        self.model.fit(X, YY, epochs=self.nb_epochs, batch_size=self.batch_size,
                    #    callbacks=[self.save_model]
                       )
        
        
    def save_model(self):
        self.model.save_weights('data/model_weight_m{}n{}.hdf5'.format(self.m, self.n))

        
    def load_model(self):
        self.model.load_weights('data/model_weight_m{}n{}.hdf5'.format(self.m, self.n))

    def eval(self, X_test, Y_test):
        Y_test_hat_pa = self.model.predict(X_test)
        Y_test_hat_pa = np.argmax(Y_test_hat_pa, axis=2)
        Y_test_hat_scheduable = []
    
        for tsidx, tspa in enumerate(Y_test_hat_pa):
            ts = tasks.TaskSystem([
                tasks.SporadicTask(ti[0], ti[1]) for _, ti in enumerate(X_test[tsidx][tspa])])
        
            bSched = rtalc.is_schedulable_rta_lc(self.m, ts)
            
            Y_test_hat_scheduable.append(bSched)
        
        nSchedulable = np.sum(Y_test_hat_scheduable)
        accuracy  = nSchedulable/Y_test.shape[0]
        
        return accuracy, nSchedulable, Y_test_hat_scheduable
    