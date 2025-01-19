import numpy as np
from scipy.io.wavfile import  write
from scipy.io import wavfile

def equalize(file, treble, mid, bass):  #nazwa pliku, 0.5 < soprany, midy, basy < 1.5 domyślnie 1
    sample_rate, audio = wavfile.read(file)
    for i in range(audio.ndim): #korekta przeprowadzana jest dla każdego kanału
        audio_channel = audio[:, i]
        FFT = np.fft.fft(audio_channel)  #wektor amplitud
        N = FFT.size
        FFT_equalized = FFT

        for j in range(N):
            element_frequency = (j/N)*sample_rate  #częstotliwość dla danego elementu (wzór matematyczny)
            if element_frequency < 250:  #niskie częstotliwości
                FFT_equalized[j] *= bass
            elif 250 <= element_frequency <= 4000:  #średnie częstotliwości
                FFT_equalized[j] *= mid
            elif element_frequency > 4000:  #wysokie częstotliwości
                FFT_equalized[j] *= treble
        audio[:, i] = np.fft.ifft(FFT_equalized)  #transformacja danych
    audio = audio.astype(np.int16)  #zmiana danych na odpowiadające dla przetwornika 16-bitowego
    write(file+".wav", sample_rate, audio)  #podmiana oryginalnego pliku

equalize("sweet_loop.wav",1.3,1.3,0.5)
