
import numpy as np
import librosa
import os, copy
from scipy import signal
from os import path
from scipy.io.wavfile import write
import json
import time

from hyperparams import Hyperparams as hp


def get_spectrograms(fpath):
    '''Parse the wave file in `fpath` and
    Returns normalized melspectrogram and linear spectrogram.

    Args:
      fpath: A string. The full path of a sound file.

    Returns:
      mel: A 2d array of shape (T, n_mels) and dtype of float32.
      mag: A 2d array of shape (T, 1+n_fft/2) and dtype of float32.
    '''
    # Loading sound file
    y, sr = librosa.load(fpath, sr=hp.sr)

    # Trimming
    y, _ = librosa.effects.trim(y)

    # Preemphasis
    y = np.append(y[0], y[1:] - hp.preemphasis * y[:-1])

    # stft
    linear = librosa.stft(y=y,
                          n_fft=hp.n_fft,
                          hop_length=hp.hop_length,
                          win_length=hp.win_length)

    # magnitude spectrogram
    mag = np.abs(linear)  # (1+n_fft//2, T)

    # mel spectrogram
    mel_basis = librosa.filters.mel(hp.sr, hp.n_fft, hp.n_mels)  # (n_mels, 1+n_fft//2)
    mel = np.dot(mel_basis, mag)  # (n_mels, t)

    # to decibel
    mel = 20 * np.log10(np.maximum(1e-5, mel))
    mag = 20 * np.log10(np.maximum(1e-5, mag))

    # normalize
    mel = np.clip((mel - hp.ref_db + hp.max_db) / hp.max_db, 1e-8, 1)
    mag = np.clip((mag - hp.ref_db + hp.max_db) / hp.max_db, 1e-8, 1)

    # Transpose
    mel = mel.T.astype(np.float32)  # (T, n_mels)
    mag = mag.T.astype(np.float32)  # (T, 1+n_fft//2)

    return mel, mag

def spectrogram2wav(mag):
    '''# Generate wave file from linear magnitude spectrogram

    Args:
      mag: A numpy array of (T, 1+n_fft//2)

    Returns:
      wav: A 1-D numpy array.
    '''
    # transpose
    mag = mag.T

    # de-noramlize
    mag = (np.clip(mag, 0, 1) * hp.max_db) - hp.max_db + hp.ref_db

    # to amplitude
    mag = np.power(10.0, mag * 0.05)

    # wav reconstruction
    wav = griffin_lim(mag**hp.power)

    # de-preemphasis
    wav = signal.lfilter([1], [1, -hp.preemphasis], wav)

    # trim
    wav, _ = librosa.effects.trim(wav)

    return wav.astype(np.float32)

def griffin_lim(spectrogram):
    '''Applies Griffin-Lim's raw.'''
    X_best = copy.deepcopy(spectrogram)
    for i in range(hp.n_iter):
        X_t = invert_spectrogram(X_best)
        est = librosa.stft(X_t, hp.n_fft, hp.hop_length, win_length=hp.win_length)
        phase = est / np.maximum(1e-8, np.abs(est))
        X_best = spectrogram * phase
    X_t = invert_spectrogram(X_best)
    y = np.real(X_t)

    return y

def invert_spectrogram(spectrogram):
    '''Applies inverse fft.
    Args:
      spectrogram: [1+n_fft//2, t]
    '''
    return librosa.istft(spectrogram, hp.hop_length, win_length=hp.win_length, window="hann")

def load_spectrograms(fpath):
    '''Read the wave file in `fpath`
    and extracts spectrograms'''

    fname = os.path.basename(fpath)

    mel, mag = get_spectrograms(fpath)

    t = mel.shape[0]

    # Marginal padding for reduction shape sync.
    num_paddings = hp.r - (t % hp.r) if t % hp.r != 0 else 0
    mel = np.pad(mel, [[0, num_paddings], [0, 0]], mode="constant")
    mag = np.pad(mag, [[0, num_paddings], [0, 0]], mode="constant")

    # Reduction
    mel = mel[::hp.r, :]
    return fname, mel, mag

def mp3_to_wav(fpath):

  # run in terminal!! does not work in VS code for whatever reason..

  from pydub import AudioSegment

  AudioSegment.converter = r"C:\\Users\\dimaz\\Downloads\\ffmpeg\\ffmpeg\\bin\\ffmpeg.exe"
  AudioSegment.ffprobe = r"C:\\Users\\dimaz\\Downloads\\ffmpeg\\ffmpeg\\bin\\ffprobe.exe"

  src = f"{fpath}.mp3"
  dst = f"{fpath}.wav"

  # convert wav to mp3                                                            
  sound = AudioSegment.from_mp3(src)
  sound.export(dst, format="wav")

  print('Success!')

def split_large_wav(fpath, interval_seconds, template):

  print('Begun reading')
  y, sr = librosa.load(f'{fpath}.wav', sr=hp.sr)

  interval_sr = interval_seconds*hp.sr

  print('Begun writing')

  for i in range( len(y) // (interval_sr) ):

    l, r = i*interval_sr, (i+1)*interval_sr

    write(os.path.join('static','data','samples',f'{template}_{i}.wav'), hp.sr, y[l:r])

    if i % 10 == 0:
      print(i)

def load_wav_mags(fpath):
  y, sr = librosa.load(fpath, sr=hp.sr)

  intervals_per_second = 100

  target_len = intervals_per_second * ( len(y) // hp.sr )

  out = []

  for i in range(target_len):
    l, r = i*(hp.sr // intervals_per_second), (i+1)*(hp.sr // intervals_per_second)

    ar = y[l:r]

    val = float(np.mean(np.abs(ar)))

    out.append(val)

  return out

def retrieve_label(fpath):
  
  f = open(os.path.join('static','data','labels.json'),) 
  data = json.load(f)

  return data[fpath.split('.')[0].split('/')[-1]]['label']

def trim_wav(fpath, label):

  outFpath = os.path.join('static','data',f'preview{time.strftime("%Y%m%d%H%M%S")}.wav')

  for path in os.listdir(os.path.join('static','data')):
    if path.startswith('preview'):
      os.remove(os.path.join('static','data',path))

  y, sr = librosa.load(fpath, sr=hp.sr)

  sr_per_interval = len(y) // len(label)

  out = []

  for i, v in enumerate(label):
    if v == 1:
      l, r = i*sr_per_interval, (i+1)*sr_per_interval

      out += list(y[l:r])

  out = np.array(out)

  write(outFpath, hp.sr, out)

  return outFpath

def load_batch(fnames, batch_labels):

  maxLen = 0
  for i, val in enumerate(batch_labels):
    maxLen = max( maxLen, len(val) )

  out = []

  for fname in fnames:
    _, mel, _ = load_spectrograms( os.path.join('static', 'data', 'samples', f'{fname}.wav') )

    mel = np.pad(mel, [[0, maxLen-mel.shape[0]], [0, 0]], mode="constant")

    out.append(mel)

  for i, val in enumerate(batch_labels):
    batch_labels[i] = np.pad(val, [maxLen-val.shape[0], 0], mode="constant")

  return np.asarray(out), np.asarray(batch_labels)
