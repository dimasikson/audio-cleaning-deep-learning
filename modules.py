
from __future__ import print_function, division

from hyperparams import Hyperparams as hp
import tensorflow as tf
from utils import *


def buildModel(inputs, level_1, n_levels, levels_repeat, training=True, dropout=True, lr=1e-3, decay=1e-5):

    i = 1

    inpt = tf.keras.layers.Input(shape=inputs, dtype=tf.float32, name="AudioEnc"+str(i)); i += 1    

    x = tf.keras.layers.Conv1D(
            filters=level_1,
            kernel_size=3,
            dilation_rate=1,
            padding="same",
            use_bias=True,
            name="AudioEnc"+str(i)
    )(inpt); i += 1
    if dropout:
        x = tf.keras.layers.Dropout(rate=hp.dropout_rate)(x)

    for j in range(n_levels):
        for _ in range(levels_repeat):
           
            x = tf.keras.layers.Conv1D(
                filters= 2 ** (n_levels - j),
                kernel_size=3,
                dilation_rate=1,
                padding="same",
                use_bias=True,
                name="AudioEnc"+str(i)
            )(x); i += 1
            if dropout:
                x = tf.keras.layers.Dropout(rate=hp.dropout_rate)(x)

    out = tf.keras.layers.Conv1D(
        filters= 1,
        kernel_size=3,
        dilation_rate=1,
        padding="same",
        activation='sigmoid',
        use_bias=True,
        name="AudioEnc"+str(i)
    )(x); i += 1

    model = tf.keras.Model(inputs=[inpt], outputs=[out])

    modelLoss = tf.keras.losses.BinaryCrossentropy()
    model.compile(
        loss=modelLoss,
        optimizer=tf.keras.optimizers.Adam(lr=lr, decay=decay),
        metrics=['accuracy']
    )

    return model
