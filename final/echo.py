import numpy as np


def add_reverb(audio_data, delay_ms, decay, wetness):
    """
    Apply a simple reverb effect to audio data using delay lines.

    Parameters:
    audio_data (numpy.ndarray): Input audio signal
    delay_ms (float): Delay time in milliseconds (0-100ms)
    decay (float): Decay factor (0.1-1.0)
    wetness (float): Wet/dry mix ratio (0-1.0)

    Returns:
    numpy.ndarray: Processed audio signal
    """
    # Convert parameters to appropriate ranges
    delay_ms = np.clip(delay_ms * 100, 1, 100)  # Scale 0-1 to 1-100ms
    decay = np.clip(decay, 0.1, 1.0)
    wetness = np.clip(wetness, 0, 1.0)

    # Convert delay to samples (assuming 44100 Hz sample rate)
    sample_rate = 44100
    delay_samples = int((delay_ms / 1000.0) * sample_rate)

    # Create output buffer
    output = np.zeros_like(audio_data, dtype=np.float32)

    # Convert input to float32 for processing
    audio_float = audio_data.astype(np.float32)

    # Create multiple delay lines with different delays and decays
    delays = [
        int(delay_samples * 1.0),
        int(delay_samples * 1.5),
        int(delay_samples * 2.0)
    ]

    decays = [
        decay * 0.8,
        decay * 0.6,
        decay * 0.4
    ]

    # Apply delay lines
    for delay, decay_factor in zip(delays, decays):
        if delay <= 0:
            continue

        # Add delayed and attenuated signal
        delayed_signal = np.zeros_like(audio_float)
        delayed_signal[delay:] = audio_float[:-delay] * decay_factor
        output += delayed_signal

    # Normalize the wet signal
    if np.max(np.abs(output)) > 0:
        output = output / np.max(np.abs(output)) * np.max(np.abs(audio_float))

    # Mix dry and wet signals
    mixed = (1 - wetness) * audio_float + wetness * output

    # Normalize final output to prevent clipping
    if np.max(np.abs(mixed)) > 0:
        mixed = mixed / np.max(np.abs(mixed)) * np.max(np.abs(audio_float))

    # Convert back to int16
    return mixed.astype(np.int16)