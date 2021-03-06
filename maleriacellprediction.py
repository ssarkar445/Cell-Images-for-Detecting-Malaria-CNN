# -*- coding: utf-8 -*-
"""MaleriaCellPrediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uihqoRRu0lW3czbVC68FhQQGH8dkhOr2
"""

# Installation required if not present
# !pip install Tensorflow
# !pip install tqdm
# !pip install tflearm

# Commented out IPython magic to ensure Python compatibility.
# Import required packages
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.layers import (Dense,Conv2D,Dropout,MaxPool2D,
                                     MaxPooling2D,Flatten)
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import log_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from tqdm import tqdm
from random import shuffle

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import optim
import cv2
# %matplotlib inline
import warnings
warnings.filterwarnings('ignore')

# importing drive and authentication
from google.colab import drive
drive.mount('/content/drive',force_remount=False)

# Change the location as per your drive
TRAIN_DIR_INFECTED =r'C:\Users\sumasark\Downloads\Kaggle\Maleria\cell_images\cell_images\Parasitized'
TRAIN_DIR_UNINFECTED =r'C:\Users\sumasark\Downloads\Kaggle\Maleria\cell_images\cell_images\Uninfected'
LR_RATE=1e-3
IMG_SIZE=28

MODEL_NAME = 'maleria--{}--{}.model'.format(LR_RATE,'2conv-basic')

# Preprocess raw images into numpy arrays

training_data = []
def create_data_infected():
    try:
        for img in tqdm(os.listdir(TRAIN_DIR_INFECTED)):
            path = os.path.join(TRAIN_DIR_INFECTED,img)
            img = cv2.imread(path,cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img,(IMG_SIZE,IMG_SIZE))
            training_data.append([np.array(img),np.array([1,0])])
    except Exception as e:
        print(str(e))   

def create_data_uninfected():
    try:
        for img in tqdm(os.listdir(TRAIN_DIR_UNINFECTED)):
            path = os.path.join(TRAIN_DIR_UNINFECTED,img)
            img = cv2.imread(path,cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img,(IMG_SIZE,IMG_SIZE))
            training_data.append([np.array(img),np.array([0,1])])
    except Exception  as e:
        print(str(e))
        
def prepare_train():
    try:
        create_data_infected()
        create_data_uninfected()
    except Exception as e:
        print(str(e))
    shuffle(training_data)
    np.save('training_data.npy',training_data)
    return training_data

# Loading the preprocessed file for train_sest_split and modeling
df = np.load('/content/drive/My Drive/DataSets/training_data.npy',allow_pickle=True)

X = []
y = []
for img,labels in df:
  X.append(img)
  y.append(labels)

X = np.array(X).reshape(-1,IMG_SIZE,IMG_SIZE,1)
X = X/255.0
y = [np.argmax(x) for x in y]
train_X,test_X,train_y,test_y = train_test_split(X,y,test_size=0.2,random_state=101)
train_y = np.asarray(train_y).astype('float32').reshape((-1,1))
test_y = np.asarray(test_y).astype('float32').reshape((-1,1))

# Define model defination using sequential model from keras
# This is a basic model add more layers as per need
model = Sequential()
model.add(Conv2D(filters = 64, kernel_size=(3,3),input_shape=X.shape[1:],activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2)))

model.add(Conv2D(filters = 64, kernel_size=(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2)))

model.add(Flatten()) 
model.add(Dense(64))

model.add(Dense(1,activation='sigmoid'))

# Checking the model summary
model.summary()

# This part is additional use tensorboard for analysis using graph
!pip install tensorboard
from tensorflow.keras.callbacks import TensorBoard
import time

NAME = 'maleria-cell-cnn-64x2-{}'.format(int(time.time()))
tensorboard = TensorBoard(log_dir='/content/drive/My Drive/logs/{}'.format(NAME))

# Compiling and running the model as the number of image is high it will take some time
# And i am doing it for 20 epochs
model.compile(optimizer='adam',loss='binary_crossentropy',metrics=['accuracy'])
model.fit(train_X,train_y,batch_size=32,epochs=20,validation_split=0.3,callbacks=[tensorboard])

# Saving the model into disk for avoiding retraining
model.save("/content/drive/My Drive/model_cnn_iter_40.h5")

# Loading the model back to disk this can be done is separate file also
import tensorflow as tf 
classifierLoad = tf.keras.models.load_model('/content/drive/My Drive/model_cnn_iter_40.h5')

# Checking model after load
classifierLoad.summary()

# Prediction on the test set
pred_y = classifierLoad.predict_classes(test_X)

# Calculating different metrics add more as per needs
from sklearn.metrics import log_loss,roc_auc_score,accuracy_score,roc_curve,precision_recall_curve

loss = log_loss(test_y,pred_y)
print('loss:',loss)
auc = roc_auc_score(test_y,pred_y)
print('auc:',auc)
accuracy = accuracy_score(test_y,pred_y)
print('accuracy={}'.format(accuracy))

# Checking ROC Curve
fpr,tpr,thresh = roc_curve(test_y,pred_y)
plt.plot(fpr,tpr)

# Checking Precision recall curve
p,r,th = precision_recall_curve(test_y,pred_y)
plt.plot(r,p)

'''
# Check Model ModelCheckpoint tensorflow
# Transfer Learning

from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input

IMG_SIZE = [28,28]
vgg = VGG16(input_shape=IMG_SIZE + [1],weights='imagenet',include_top=False)
'''

