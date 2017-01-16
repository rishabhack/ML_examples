'''
https://blog.keras.io/building-powerful-image-classification-models-using-very-little-data.html

script originaly for fine-tunning
```
data/
    train/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
    validation/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
```
'''

import os
import h5py
import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras.models import Sequential
from keras.layers import Convolution2D, MaxPooling2D, ZeroPadding2D
from keras.layers import Activation, Dropout, Flatten, Dense
import pandas as pd

from keras import backend as K 
K.set_image_dim_ordering('th')

# path to the model weights files.
VGG16_weights_path = '/home/pablo/Documents/VGG16/vgg16_weights.h5'
top_model_weights_path = 'bottleneck_top_model.h5'
# dimensions of our images.
img_width, img_height = 150, 150

# train_data_dir = 'data/train'
# validation_data_dir = 'data/validation'
test_data_dir = '/home/pablo/Documents/Git_repositories/data_examples/DogsVsCats/data/test_small'
# nb_train_samples = 2000
# nb_validation_samples = 800
nb_predict_samples = len(os.listdir(os.path.join(test_data_dir, 'test')))
# nb_epoch = 50

# build the VGG16 network
model = Sequential()
model.add(ZeroPadding2D((1, 1), input_shape=(3, img_width, img_height)))

model.add(Convolution2D(64, 3, 3, activation='relu', name='conv1_1'))
model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(64, 3, 3, activation='relu', name='conv1_2'))
model.add(MaxPooling2D((2, 2), strides=(2, 2)))

model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(128, 3, 3, activation='relu', name='conv2_1'))
model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(128, 3, 3, activation='relu', name='conv2_2'))
model.add(MaxPooling2D((2, 2), strides=(2, 2)))

model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(256, 3, 3, activation='relu', name='conv3_1'))
model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(256, 3, 3, activation='relu', name='conv3_2'))
model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(256, 3, 3, activation='relu', name='conv3_3'))
model.add(MaxPooling2D((2, 2), strides=(2, 2)))

model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(512, 3, 3, activation='relu', name='conv4_1'))
model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(512, 3, 3, activation='relu', name='conv4_2'))
model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(512, 3, 3, activation='relu', name='conv4_3'))
model.add(MaxPooling2D((2, 2), strides=(2, 2)))

model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(512, 3, 3, activation='relu', name='conv5_1'))
model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(512, 3, 3, activation='relu', name='conv5_2'))
model.add(ZeroPadding2D((1, 1)))
model.add(Convolution2D(512, 3, 3, activation='relu', name='conv5_3'))
model.add(MaxPooling2D((2, 2), strides=(2, 2)))

# load the weights of the VGG16 networks
# (trained on ImageNet, won the ILSVRC competition in 2014)
# note: when there is a complete match between your model definition
# and your weight savefile, you can simply call model.load_weights(filename)
assert os.path.exists(VGG16_weights_path), 'Model weights not found (see "VGG16_weights_path" variable in script).'
f = h5py.File(VGG16_weights_path)
for k in range(f.attrs['nb_layers']):
    if k >= len(model.layers):
        # we don't look at the last (fully-connected) layers in the savefile
        break
    g = f['layer_{}'.format(k)]
    weights = [g['param_{}'.format(p)] for p in range(g.attrs['nb_params'])]
    model.layers[k].set_weights(weights)
f.close()
print('Model loaded.')

# build a classifier model to put on top of the convolutional model
top_model = Sequential()
top_model.add(Flatten(input_shape=model.output_shape[1:]))
top_model.add(Dense(256, activation='relu'))
top_model.add(Dropout(0.5))
top_model.add(Dense(1, activation='sigmoid'))

# note that it is necessary to start with a fully-trained
# classifier, including the top classifier,
# in order to successfully do fine-tuning
top_model.load_weights(top_model_weights_path)

# add the model on top of the convolutional base
model.add(top_model)

# # set the first 25 layers (up to the last conv block)
# # to non-trainable (weights will not be updated)
# for layer in model.layers[:25]:
#     layer.trainable = False

# compile the model with a SGD/momentum optimizer
# and a very slow learning rate.
model.compile(loss='binary_crossentropy',
              optimizer=optimizers.SGD(lr=1e-4, momentum=0.9),
              metrics=['accuracy'])

# # prepare data augmentation configuration
# train_datagen = ImageDataGenerator(
#         rescale=1./255,
#         shear_range=0.2,
#         zoom_range=0.2,
#         horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1./255)

# train_generator = train_datagen.flow_from_directory(
#         train_data_dir,
#         target_size=(img_height, img_width),
#         batch_size=32,
#         class_mode='binary')

# validation_generator = test_datagen.flow_from_directory(
#         validation_data_dir,
#         target_size=(img_height, img_width),
#         batch_size=32,
#         class_mode='binary')

# # fine-tune the model
# model.fit_generator(
#         train_generator,
#         samples_per_epoch=nb_train_samples,
#         nb_epoch=nb_epoch,
#         validation_data=validation_generator,
# nb_val_samples=nb_validation_samples)

test_generator = test_datagen.flow_from_directory(
        test_data_dir,
        target_size=(img_height, img_width),
        batch_size=32,
        class_mode=None,
        shuffle=False)

# predicttion
predictions = model.predict_generator(test_generator, nb_predict_samples)
# save predicitions
np.save('test_data_predictions', predictions)

# load predictions
test_prediction = np.load('test_data_predictions.npy')
print(test_prediction)


print(os.listdir(os.path.join(test_data_dir, 'test')))
images_IDs = [ j.split('.')[0] for j in os.listdir(os.path.join(test_data_dir, 'test')) ]
df = pd.DataFrame()
df['id'] = images_IDs
df['label'] = test_prediction
print(df)
df.to_csv('sub.csv', index=False)
