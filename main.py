from flask import Flask, render_template, url_for, request, redirect, session, make_response, jsonify

from datetime import datetime
import string
import time
import datetime
import os
import numpy as np
import json

from string import punctuation
from utils import load_wav_mags, retrieve_label, load_spectrograms, trim_wav

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')


@app.route('/fetchLabels', methods=['POST'])
def fetchLabels():
    
    req = request.get_json()['input']
    out = {}

    reqId = req.split('/')[-1].split('.')[0]
    f = open(os.path.join('static','data','labels.json'),) 
    data = json.load(f)

    if reqId not in data:
        if int(reqId.split('_')[-1]) < 0:
            newId = max( [ int(i.split('_')[-1].split('.')[0]) for i in data.keys() ] )
        else:
            newId = 0
            
        req = req.split('_')[0]+'_'+str(newId)+'.wav'

    # mel spectrogram
    _, ar, _ = load_spectrograms(req)
    ar = [[float(j) for j in i] for i in np.transpose(ar)]

    out['ar'] = ar

    lbl = retrieve_label(req)

    if len(lbl) == 0:
        lbl = [1 for i in range(len(ar[0]))]

    out['label'] = lbl
    out['id'] = req

    # load labels if any from json + wav array for requested path
    return make_response(jsonify(out), 200)

@app.route('/saveLabels', methods=['POST'])
def saveLabels():
    
    req = request.get_json()

    reqId = req['input'].split('/')[-1].split('.')[0]
    f = open(os.path.join('static','data','labels.json'),) 
    data = json.load(f)

    data[reqId] = {
        'label': req['label']
    }

    with open(os.path.join('static','data','labels.json'), 'w') as f:
        json.dump(data, f)

    return {'msg': f'Successfully saved {reqId}!'}

@app.route('/previewLabels', methods=['POST'])
def previewLabels():
    
    req = request.get_json()

    reqId = req['input'].split('/')[-1].split('.')[0]
    label = req['label']

    previewFpath = trim_wav(req['input'], label)

    return {'msg': previewFpath}


app.secret_key = 'SECRET KEY'

if __name__ == "__main__":

    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True,use_reloader=False)