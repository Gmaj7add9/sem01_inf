import numpy as np


def apply_distortion(samples, threshold_db=0, level=50, gain_db=0):
    """
    Apply distortion effect to audio samples.

    Parameters:
    samples (np.array): Input audio data as numpy array (16-bit PCM)
    threshold_db (int): Threshold in dB where distortion begins (-50 to 50)
    level (int): Distortion intensity from dial (0 to 100)
    gain_db (int): Output gain in dB (-50 to 50)

    Returns:
    np.array: Processed audio samples
    """
    # Convert to float32 and normalize to [-1, 1]
    samples = samples.astype(np.float32) / 32768.0

    # Convert threshold from dB to linear amplitude
    threshold = 10 ** (threshold_db / 20.0)
    # Normalize threshold to [0, 1] range
    threshold = np.clip(threshold, 0.0, 1.0)

    # Convert level from dial range to [0, 1]
    level = level / 100.0

    # Convert gain from dB to linear multiplier
    gain_linear = 10 ** (gain_db / 20.0)

    # Create a copy for processing
    processed = samples.copy()

    # Apply distortion
    mask = np.abs(processed) > threshold
    if np.any(mask):
        # Calculate distortion only where signal exceeds threshold
        excess = np.abs(processed[mask]) - threshold

        # Apply soft clipping curve based on level
        curve = threshold + (1.0 - threshold) * (1.0 - np.exp(-level * excess))

        # Preserve original signal sign
        processed[mask] = np.sign(processed[mask]) * curve

    # Apply gain
    processed *= gain_linear

    # Hard clip to prevent overflow
    processed = np.clip(processed, -1.0, 1.0)

    # Convert back to 16-bit PCM range
    return (processed * 32768.0).astype(np.int16)