import os
import numpy as np
from module_autoencoder import Autoencoder
from keras.layers import Input
from keras.preprocessing.image import ImageDataGenerator
from keras import callbacks

from skimage.transform import resize
from keras.datasets import cifar10
(x_train, y_train), (x_test, y_test) = cifar10.load_data()


vgg16_weights = 'model_weights/vgg16_initial_encoder_weights.h5'

input_shape = ( 48, 48, 3)
ec_input = Input( input_shape, name='ec_input')
ae = Autoencoder( ec_input)
ae.model.load_weights( vgg16_weights, by_name=True)

ae.freeze_encoder()
ae.model.compile( loss='binary_crossentropy', optimizer='adadelta')

resize_train = []
resize_test  = []
for im in x_train:
    resize_train.append( resize( im, input_shape[:2]))
for im in x_test:
    resize_test.append(  resize( im, input_shape[:2]))
x_train = np.asarray( resize_train)
x_test  = np.asarray( resize_test)

del resize_train
del resize_test

train_datagen = ImageDataGenerator( rescale=1./255)
train_flow = train_datagen.flow( x_train, x_train, batch_size=64)

test_datagen = ImageDataGenerator( rescale=1./255)
test_flow = test_datagen.flow( x_test, x_test, batch_size=64)

# configure model checkpoints
if not os.path.exists( 'model_weights/checkpoints'):
    os.makedirs( 'model_weights/checkpoints')
fileCheckpoint = 'model_weights/checkpoints/' \
                + 'train_ae_' \
                + 'epoch_{epoch:03d}-{val_loss:.2f}.h5'
modelCheckpoint = callbacks.ModelCheckpoint( filepath=fileCheckpoint, save_weights_only=True)

ae.model.fit_generator( train_flow, steps_per_epoch=len(x_train)/64,
                        validation_data=test_flow, validation_steps=len(x_test)/64,
                        callbacks=[modelCheckpoint],
                        epochs=1500)