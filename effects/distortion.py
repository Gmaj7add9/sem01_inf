from librosa import *
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

def apply_Distortion(y, threshold): #y = audio data
    threshold=abs(threshold)
    y_distorted=np.clip(y,-threshold, threshold)
    y_distorted=y_distorted/np.max(np.abs(y_distorted))
    return y_distorted
