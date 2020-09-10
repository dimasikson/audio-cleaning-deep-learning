# Audio-cleaning-with-Deep-Learning

# 1. What is this project? Why is it useful?

This project helps significantly speed up cleaning large amounts of audio, it uses deep learning to classify raw audio into sections to be removed vs kept. Primarily we remove sections in the audio that are:
  - silences
  - mic breathing
  - other miscellaneous sounds, e.g. mic touching, etc.

![alt text](https://i.gyazo.com/8ccd8f611b4a73b2a405c90c6c039e65.png)

Primary use case was to pre-process podcast audio and other audio spoken content.

Additionally this project features a small data labeling web app, see section 3.3

# 2. How well does it perform?

The larger model in terms of # of parameters performs at 99% recall and 92% precision. As explained below, higher recall results in much better listening experience than higher precision, so these results are good. 

![alt text](https://i.gyazo.com/cc38e0b2e210bbd63355f5a38d2e1061.png)

Below are test samples:
  - original clip, 30 seconds: https://soundcloud.com/dmitri-ivanov-933106925/raw-test-podcast-editing-dl-1
  - manually edited 'correct' clip, 20 seconds: https://soundcloud.com/dmitri-ivanov-933106925/correct-test-podcast-editing-dl
  - machine generated clip, 22 seconds: https://soundcloud.com/dmitri-ivanov-933106925/edited-test

Note about the generated clip above: predictions are generated as probability between 0.0 and 1.0, and I have found that rounding the outputs above 0.15 to 1 results in the best listening experience. There is a trade-off between precision and recall illustrated below and I have found having higher recall much better than precision.

![alt text](https://i.gyazo.com/4ce067ba8bcd12046af6249e4957cec8.png)

# 3. How it was done:
## 3.1 Data gathering

I had a 97 minute podcast recorded, stored as mp3. I split it up into 5 second wav files, refer to 1st cell in the notebook: https://github.com/dimasikson/Audio-cleaning-with-Deep-Learning/blob/master/testNotebook.ipynb

## 3.2 Model

### Input: audio mel spectrogram, shape (t, M)
### Labels: binary array, shape (t, 1)

Where:
  - t - timesteps
  - M - number of frequency banks

More on audio transformation into mel spectrograms: https://towardsdatascience.com/getting-to-know-the-mel-spectrogram-31bca3e2d9d0

The model consists only of Convolutional 1D layers, below is the summary:

![alt text](https://i.gyazo.com/61faad7373e5f6e27ec3f94293414d47.png)

Model construction roughly inspired by: https://attardi.org/pytorch-and-coreml/

![](https://attardi.org/static/af9a10acd36978e8a185d820c89a55d5/b06ae/diagram.png)

## 3.3 Data labeling web app

In order to obtain labeled data, I had to build a small application where I could manually label the audio and export the arrays. Using Flask with vanilla JS for this.

An alternative approach could be to edit the audio in an existing software and export timestamps, but I have not found a sotfware that allows that.

Below is a screenshot of the web app:

![](https://i.gyazo.com/7369a9176874d99eb8ce7319b1806cdd.png)

### The way to use it:
  - draw in the bordered rectangle below the charts to label the audio
  - click next to save

# 4. Instructions to recreate

### STEP 0: install requirements

### STEP 1: to pre-process your audio file, run 1st cell in notebook (also uncomment functions), change the fpath to where your raw audio file is stored
Notebook: https://github.com/dimasikson/Audio-cleaning-with-Deep-Learning/blob/master/testNotebook.ipynb

### STEP 2: use web app to label files for training
instrcutions:
  - go to static/index.js and change the variable "template" to your audio name template
  - initiate "python main.py"
  - label your audio by drawing in the white box, click next / previous to save. Labels will appear in static/data/labels.json

### STEP 3: train your model by initiating "python train.py"

### STEP 4: for inference, use 2nd cell from the notebook

# 5. Sources
  - https://towardsdatascience.com/getting-to-know-the-mel-spectrogram-31bca3e2d9d0
  - https://attardi.org/pytorch-and-coreml/
  - https://arxiv.org/abs/1710.08969
