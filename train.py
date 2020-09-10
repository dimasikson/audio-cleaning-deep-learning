
from __future__ import print_function, division

from hyperparams import Hyperparams as hp
import tensorflow as tf
from utils import *
from modules import buildModel
import json
import time
from tensorflow.keras.callbacks import TensorBoard

import pandas as pd
import numpy as np

# ###### 04/09/20 ######
# training 0-500
# validation 501-524

def train(n_epochs, level_1, n_levels, levels_repeat, batch_size, max_sample_num = 500):

    modelName = f'audioCleaning_levels-{n_levels}_repeat-{levels_repeat}_level1-{level_1}_' + str(int(time.time()))

    # load labels
    f = open(os.path.join('static','data','labels.json'),) 
    data = json.load(f)

    labels = {}

    for k, v in data.items():

        if (len(v['label']) > 0) & ( int( k.split('_')[-1] ) <= max_sample_num ):
            labels[k] = v['label']

    # build model object
    model = buildModel(
        inputs = (None,hp.n_mels),
        level_1 = level_1,
        n_levels = n_levels,
        levels_repeat = levels_repeat,
        lr=1e-3,
        decay=1e-5,
        dropout=True
    )

    print(model.summary())

    # training loop
    for i in range(n_epochs):

        n_batches = len(labels.keys()) // batch_size

        if len(labels.keys()) % n_batches >= batch_size // 2:
            n_batches += 1

        dfLabels = pd.DataFrame({
            'fname': [i for i in labels.keys()],
            'label': [np.asarray(i) for i in labels.values()]
        }).sample( len(labels.keys()) )

        dfLabels.loc[:,'batch_num'] = np.arange( len(labels.keys()) )
        dfLabels.loc[:,'batch_num'] = dfLabels.loc[:,'batch_num'] // batch_size

        for j in range(n_batches):

            # load batch
            fnames = list(dfLabels.loc[dfLabels.loc[:,'batch_num'] == j, 'fname'])

            batch_labels = list(dfLabels.loc[dfLabels.loc[:,'batch_num'] == j, 'label'])
            batch_samples, batch_labels, _ = load_batch(fnames, batch_labels)

            # fit on batch
            loss = model.train_on_batch(
                x = batch_samples,
                y = batch_labels
            )

            print(loss)

    # save model    
    model.save('savedModels/' + modelName + '.h5')


train(
    n_epochs = 10,
    level_1 = 20, # hp.n_mels
    n_levels = 0, 
    levels_repeat = 1,
    batch_size = 32,
    max_sample_num = 500
)

