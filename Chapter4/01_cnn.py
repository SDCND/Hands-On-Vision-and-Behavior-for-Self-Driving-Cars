import cv2
import keras
import tensorflow as tf
from keras.datasets import mnist, cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D, AveragePooling2D
from keras.models import load_model
from keras.callbacks import ModelCheckpoint
#from keras.optimizers import Adam
from tensorflow.keras.optimizers import Adam # - Works
from keras.losses import categorical_crossentropy
import os
from time import time
import numpy as np

import sys
sys.path.append('../')

from utils import show_history, rgb2gray, bgr2gray, save
from tensorflow.keras.utils import to_categorical

use_mnist = True

name = "mnist" if use_mnist else "cifar10"
batch_size = 16
num_classes = 10
epochs = 5
dir_save = os.path.join(os.getcwd(), 'models')
train = True

print("Dataset in use: ", name.upper())

# Loading test and training datasets
if use_mnist:
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    print(x_train.shape)
    x_train = np.reshape(x_train, np.append(x_train.shape, (1)))
    print(x_train.shape)
    x_test = np.reshape(x_test, np.append(x_test.shape, (1)))
else:
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()

save(name + "_train.jpg", cv2.hconcat([x_train[0], x_train[1], x_train[2], x_train[3], x_train[4]]))
save(name + "_test.jpg", cv2.hconcat([x_test[0], x_test[1], x_test[2], x_test[3], x_test[4]]))
print('X Train', x_train.shape, ' - X Test', x_test.shape)
print('Y Train', y_train.shape, ' - Y Test', y_test.shape)
print('First 5 labels, train:', y_train[0], y_train[1], y_train[2], y_train[3], y_train[4])
print('First 5 labels, test:', y_test[0], y_test[1], y_test[2], y_test[3], y_test[4])
#y_train = keras.utils.to_categorical(y_train, num_classes)
#y_test = keras.utils.to_categorical(y_test, num_classes)
y_train = to_categorical(y_train, num_classes)
y_test = to_categorical(y_test, num_classes)

model_name = name + ".h5"
checkpoint = ModelCheckpoint(model_name, monitor='val_loss', mode='min', verbose=1, save_best_only=True)


def create_model_1():
    model = Sequential()
    # Convolutional layers
    model.add(Conv2D(64, (7, 7), input_shape=x_train.shape[1:], activation='relu'))
    model.add(MaxPooling2D())

    model.add(Conv2D(filters=128, kernel_size=(5,5), padding="same"))
    model.add(MaxPooling2D())

    model.add(Conv2D(filters=192, kernel_size=(3,3), strides=(1,1), padding="same", activation = "relu"))
    model.add(Conv2D(filters=128, kernel_size=(3,3), strides=(1,1), padding="same", activation = "relu"))

    model.add(MaxPooling2D(pool_size=(3,3), strides=(2,2), padding="valid"))

    # Fully Connected layers
    model.add(Flatten())
    model.add(Dense(units = 1024, activation = "relu"))
    model.add(Dense(units = 256, activation = "relu"))


    model.add(Dense(num_classes))
    model.add(Activation('softmax'))

    return model

def create_model_2_lenet():
    model = Sequential()
    # Convolutional layers

    model.add(Conv2D(filters=6, kernel_size=(5, 5), activation='relu', padding='same', input_shape=x_train.shape[1:]))
    model.add(MaxPooling2D())

    model.add(Conv2D(filters=16, kernel_size=(5, 5), activation='relu'))
    model.add(MaxPooling2D())

    # Fully Connected layers
    model.add(Flatten())
    model.add(Dense(units=120, activation='relu'))
    model.add(Dense(units=84, activation='relu'))
    model.add(Dense(units=num_classes, activation='softmax'))

    return model

def create_model_2_lenet_bigger():
    model = Sequential()
    # Convolutional layers
    model.add(Conv2D(filters=64, kernel_size=(3, 3), activation='relu', input_shape=x_train.shape[1:]))
    model.add(AveragePooling2D())

    model.add(Conv2D(filters=256, kernel_size=(3, 3), activation='relu'))
    model.add(AveragePooling2D())

    # Fully Connected layers
    model.add(Flatten())
    model.add(Dense(units=512, activation='relu'))
    model.add(Dense(units=256, activation='relu'))
    model.add(Dense(units=num_classes, activation = 'softmax'))

    return model


if train:
    model = create_model_2_lenet()
    model.summary()
    opt = Adam()

    model.compile(loss=categorical_crossentropy, optimizer=opt, metrics=['accuracy'])
    start = time()
    history_object = model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(x_test, y_test), shuffle=True, callbacks=[checkpoint])
    print("Training time:", time()-start)

    show_history(history_object)
else:
    model = load_model(os.path.join(dir_save, model_name))
    model.summary()
    print("H5 Output: " + str(model.output.op.name))
    print("H5 Input: " + str(model.input.op.name))

    # Score trained model.
    scores = model.evaluate(x_test, y_test, verbose=1)
    print('Validation loss:', scores[0])
    print('Validation accuracy:', scores[1])


