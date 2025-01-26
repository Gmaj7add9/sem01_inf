import numpy as np


def equalize(audio, sample_rate, treble, mid, bass):
    # Ensure input is numpy array of float32
    audio = np.asarray(audio, dtype=np.float32)

    # Compute FFT
    fft = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1 / sample_rate)

    # Apply frequency-specific gains
    for i, freq in enumerate(freqs):
        if freq < 250:  # Bass
            fft[i] *= bass / 100
        elif 250 <= freq < 4000:  # Mid
            fft[i] *= mid / 100
        else:  # Treble
            fft[i] *= treble / 100

    # Inverse FFT
    processed = np.fft.irfft(fft)

    # Clip to prevent overflow
    processed = np.clip(processed, -32768, 32767)

    return processed.astype(np.int16)