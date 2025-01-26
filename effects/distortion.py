from pydub import AudioSegment
import numpy as np

def apply_distortion(audio_segment, gain=20, ceiling=32767):
    samples = np.array(audio_segment.get_array_of_samples())
    
    samples = samples * gain
    
    samples = np.clip(samples, -ceiling, ceiling)
    distorted = AudioSegment(
        samples.astype(np.int16).tobytes(), 
        frame_rate=audio_segment.frame_rate,
        sample_width=2, 
        channels=audio_segment.channels
    )
    
    return distorted
