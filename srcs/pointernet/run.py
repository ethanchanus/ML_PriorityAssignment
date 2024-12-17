from keras import layers
from keras.models import Model
from keras.layers import LSTM, Input
from keras.callbacks import LearningRateScheduler
from keras.utils.np_utils import to_categorical
# from . 
from PointerLSTM import PointerLSTM
import pickle
import tsp_data as tsp
import numpy as np
import keras


def scheduler(epoch):
    if epoch < nb_epochs/4:
        return learning_rate
    elif epoch < nb_epochs/2:
        return learning_rate*0.5
    return learning_rate*0.1


# import numpy as np
# import tensorflow as tf
# from tensorflow import keras
# from tensorflow.keras import layers


# model = keras.Sequential()
# model.add(layers.Embedding(input_dim=1000, output_dim=64))

# # The output of GRU will be a 3D tensor of shape (batch_size, timesteps, 256)
# model.add(layers.GRU(256, return_sequences=True))

# # The output of SimpleRNN will be a 2D tensor of shape (batch_size, 128)
# model.add(layers.SimpleRNN(128))

# model.add(layers.Dense(10))

# model.summary()

# encoder_vocab = 1000
# decoder_vocab = 2000

# encoder_input = layers.Input(shape=(None,))
# encoder_embedded = layers.Embedding(input_dim=encoder_vocab, output_dim=64)(
#     encoder_input
# )

# # Return states in addition to output
# output, state_h, state_c = layers.LSTM(64, return_state=True, name="encoder")(
#     encoder_embedded
# )


# exit(0)


print("preparing dataset...")
t = tsp.Tsp()

# X, Y = t.next_batch(10000)
# x_test, y_test = t.next_batch(1000)
# # X, Y = t.next_batch(50)
# # x_test, y_test = t.next_batch(100)

# np.save("X.npy", X)
# np.save("Y.npy", Y)
# np.save("x_test.npy", x_test)
# np.save("y_test.npy", y_test)
# print(X.shape)

X = np.load("X.npy")
Y = np.load("Y.npy")
x_test = np.load("x_test.npy")
y_test = np.load("y_test.npy")

for i in [X,Y, x_test, y_test]:
    print(i.shape)
    

# YY = []
# for y in Y:
#     YY.append(to_categorical(y))
# YY = np.asarray(YY)
YY = to_categorical(Y)

# print(np.sum(YY- to_categorical(Y)))
# print(y_test.shape)
# print(y_test[1])
# z=to_categorical(y_test)
# print(z.shape, z[1])


hidden_size = 128
seq_len = 10
nb_epochs = 50
learning_rate = 0.1
batch_size = 64
print("building model...")
main_input = Input(shape=(seq_len, 2), name='main_input')

encoder,state_h, state_c = LSTM(hidden_size,return_sequences = True, name="encoder",return_state=True)(main_input)

decoder = PointerLSTM(hidden_size, name="decoder")(encoder,states=[state_h, state_c])

model = Model(main_input, decoder)
print(model.summary())
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.load_weights('model_weight_{}.hdf5'.format(nb_epochs))
# model.fit(X, YY, epochs=nb_epochs, batch_size=batch_size) #, verbose=False)
# model.save_weights('model_weight_{}.hdf5'.format(nb_epochs))

print('evaluate : ',model.evaluate(x_test,to_categorical(y_test)))
y_test_hat = model.predict(x_test)
print(x_test.shape, y_test_hat.shape)
print(np.argmax(y_test_hat,axis=-1))
# print( y_test_hat)
