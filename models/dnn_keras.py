# Copyright 2018 Abien Fred Agarap
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""DNN-ReLU class written using Keras/TensorFlow"""
from __future__ import print_function

__version__ = '0.1.0'
__author__ = 'Abien Fred Agarap'

from keras import backend as K
from keras import callbacks
from keras.models import Sequential
from keras.layers import Activation
from keras.layers import Dense
from keras.layers import Dropout
from keras.utils.generic_utils import get_custom_objects
import numpy as np
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedKFold
import sys


class DNN:

    def __init__(self, **kwargs):
        """Instantiates DNN-ReLU class

        :param kwargs:
        """
        assert 'activation' in kwargs, 'KeyNotFound : {}'.format('activation')
        assert type(kwargs['activation']) is str, \
            'Expected data type : str, but {} is {}'.format(kwargs['activation'], type(kwargs['activation']))

        assert 'dropout_rate' in kwargs, 'KeyNotFound : {}'.format('dropout_rate')
        assert type(kwargs['dropout_rate']) is float, \
            'Expected data type : float, but {} is {}'.format(kwargs['dropout_rate'], type(kwargs['dropout_rate']))

        assert 'loss' in kwargs, 'KeyNotFound : {}'.format('loss')
        assert type(kwargs['loss']) is str, \
            'Expected data type : str, but {} is {}'.format(kwargs['loss'], type(kwargs['loss']))

        assert 'optimizer' in kwargs, 'KeyNotFound : {}'.format('optimizer')
        assert type(kwargs['optimizer']) is str, \
            'Expected data type : str, but {} is {}'.format(kwargs['optimizer'], type(kwargs['optimizer']))

        assert 'num_classes' in kwargs, 'KeyNotFound : {}'.format('num_classes')
        assert type(kwargs['num_features']) is int, \
            'Expected data type : int, but {} is {}'.format(kwargs['num_classes'], type(kwargs['num_classes']))

        assert 'num_features' in kwargs, 'KeyNotFound : {}'.format('num_features')
        assert type(kwargs['num_features']) is int, \
            'Expected data type : int, but {} is {}'.format(kwargs['num_features'], type(kwargs['num_features']))

        assert 'num_neurons' in kwargs, 'KeyNotFound : {}'.format('num_neurons')
        assert type(kwargs['num_neurons']) is list, \
            'Expected data type : list, but {} is {}'.format(kwargs['num_neurons'], type(kwargs['num_neurons']))

        def __graph__():

            get_custom_objects().update({'swish': Activation(DNN.swish)})

            if kwargs['activation'] == 'swish':
                activation = DNN.swish
            else:
                activation = kwargs['activation']

            model = Sequential()
            model.add(Dense(kwargs['num_neurons'][0],
                            activation=activation,
                            input_dim=kwargs['num_features']))
            model.add(Dropout(kwargs['dropout_rate']))

            for num_neurons in kwargs['num_neurons'][1:]:
                model.add(Dense(num_neurons, activation=activation))
                model.add(Dropout(kwargs['dropout_rate']))

            model.add(Dense(kwargs['num_classes'], activation='relu'))

            model.compile(loss=kwargs['loss'], optimizer=kwargs['optimizer'], metrics=['accuracy'])

            self.model = model

        sys.stdout.write('<log> Building graph...\n')
        __graph__()
        sys.stdout.write('</log>\n')

    def train(self, **kwargs):
        """Trains the instantiated DNN-ReLU class

        :param kwargs:
        :return:
        """

        assert 'batch_size' in kwargs, 'KeyNotFound : {}'.format('batch_size')
        assert type(kwargs['batch_size']) is int, \
            'Expected data type : int, but {} is {}'.format(kwargs['batch_size'], type(kwargs['batch_size']))

        assert 'n_splits' in kwargs, 'KeyNotFound : {}'.format('n_splits')
        assert type(kwargs['n_splits']) is int, \
            'Expected data type : int, but {} is {}'.format(kwargs['n_splits'], type(kwargs['n_splits']))

        assert 'log_path' in kwargs, 'KeyNotFound : {}'.format('log_path')
        assert type(kwargs['log_path']) is str, \
            'Expected data type : str, but {} is {}'.format(kwargs['log_path'], type(kwargs['log_path']))

        assert 'validation_split' in kwargs, 'KeyNotFound : {}'.format('validation_split')
        assert type(kwargs['validation_split']) is float, \
            'Expected data type : float, but {} is {}'.format(kwargs['validation_split'],
                                                              type(kwargs['validation_split']))

        assert 'verbose' in kwargs, 'KeyNotFound : {}'.format('verbose')
        assert 0 <= kwargs['verbose'] <= 2, 'ValueError : {} must be >= 0 and <= 2'.format('verbose')
        assert type(kwargs['verbose']) is int, \
            'Expected data type : int, but {} is {}'.format(kwargs['verbose'], type(kwargs['verbose']))

        seed = 7
        kfold = StratifiedKFold(n_splits=kwargs['n_splits'], shuffle=True, random_state=seed)
        cvscores = []

        train_features, train_labels = kwargs['train_features'], kwargs['train_labels']

        tbCallback = callbacks.TensorBoard(log_dir=kwargs['log_path'], histogram_freq=0,
                                           write_graph=True, write_images=True)

        for train, validate in kfold.split(train_features, np.argmax(train_labels, 1)):
            self.model.fit(train_features[train], train_labels[train],
                           epochs=kwargs['epochs'], batch_size=kwargs['batch_size'], verbose=kwargs['verbose'],
                           validation_split=kwargs['validation_split'],
                           callbacks=[tbCallback])
            score = self.model.evaluate(train_features[validate], train_labels[validate],
                                        verbose=kwargs['verbose'])
            print('{} : {}, {} : {}'.format(self.model.metrics_names[0], score[0],
                                            self.model.metrics_names[1], score[1]))
            cvscores.append(score[1])
        print('==========')
        print('CV acc : {}, CV stddev : +/- {}'.format(np.mean(cvscores), np.std(cvscores)))

    def evaluate(self, **kwargs):
        """Evaluates the trained model

        :param kwargs:
        :return:
        """

        assert 'batch_size' in kwargs, 'KeyNotFound : {}'.format('batch_size')
        assert type(kwargs['batch_size']) is int, \
            'Expected data type : int, but {} is {}'.format(kwargs['batch_size'], type(kwargs['batch_size']))

        assert 'class_names' in kwargs, 'KeyNotFound : {}'.format('class_names')
        assert type(kwargs['class_names']) is list, \
            'Expected data type : list, but {} is {}'.format(kwargs['class_names'], type(kwargs['class_names']))

        test_features, test_labels = kwargs['test_features'], kwargs['test_labels']

        score, accuracy = self.model.evaluate(test_features=test_features, test_labels=test_labels,
                                              batch_size=kwargs['batch_size'])

        print('Test loss : {}\nTest accuracy : {}'.format(score, accuracy))

        test_predictions = self.model.predict(test_features)
        test_predictions = np.argmax(test_predictions, axis=1)

        class_names = kwargs['class_names']
        report = classification_report(np.argmax(test_labels, axis=1), test_predictions, target_names=class_names)
        conf_matrix = confusion_matrix(np.argmax(test_labels, axis=1), test_predictions)

        return report, conf_matrix

    @staticmethod
    def swish(x):
        """Returns non-linearity through Swish

        :param x: The input vector for non-linearity
        """
        return K.sigmoid(x) * x
