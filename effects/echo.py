from pydub import AudioSegment
from pydub.utils import ratio_to_db

def add_reverb(file,delay,decay,wetness): #nazwa pliku ,opóźnienie w ms ,zanik od 0 do 2 domyślnie 1, wetness od 0 do 2 domyślnie 1
    audio = AudioSegment.from_wav(file)
    repetitions = 5 #przykładowa ilość nałożonych na siebie sygnałów opóźnionych

    audio_delayed_in = AudioSegment.silent(duration=delay) + audio #tworzenie wejściowego sygnału opóźnionego do pętli
    audio_decayed = audio_delayed_in.apply_gain(ratio_to_db(decay)) #manipulacja głośnością opóżnienia
    audio_delayed_out = audio_decayed
    for i in range(repetitions-1):
        audio_delayed_in = AudioSegment.silent(duration=delay) + audio_delayed_out #dodawanie opóźnienia przez dodanie ciszy na początku o zadanym czasie trwwania
        audio_decayed = audio_delayed_in.apply_gain(ratio_to_db(decay)) #manipulacja głośnością jednego opóżnienia
        audio_delayed_out = audio_decayed.overlay(audio_delayed_out) #nakładanie na siebie opóźnionych ścierzek

    audio_wet = audio_delayed_out.apply_gain(ratio_to_db(wetness)) #wetness, manipulacja głośnością całego opóźnienia
    audio_reverbed = audio_wet.overlay(audio)
    audio_reverbed.export(file+".wav", format="wav")

