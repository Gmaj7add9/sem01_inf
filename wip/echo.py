import numpy as np


def add_reverb(audio, delay, decay, wetness):
    # Ensure input is numpy array of float32
    audio = np.asarray(audio, dtype=np.float32)

    # Create reverb buffer same length as input
    reverb = np.zeros_like(audio)

    # Generate multiple echo layers
    current_echo = audio.copy()
    for i in range(5):  # 5 echo layers
        # Create delayed version
        delayed = np.zeros_like(audio)
        delay_samples = int(delay * (i + 1))

        if delay_samples > 0:
            delayed[delay_samples:] = current_echo[:-delay_samples]

        # Apply decay and add to reverb
        current_echo *= decay
        reverb += delayed * current_echo

    # Mix original and reverb based on wetness
    processed = audio * (1 - wetness) + reverb * wetness

    # Clip to prevent overflow
    processed = np.clip(processed, -32768, 32767)

    return processed.astype(np.int16)