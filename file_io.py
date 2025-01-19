from pydub import AudioSegment
from pydub.playback import play
import os


def read_audio_file(file_path):
    try:
        # sprawdz czy plik istnieje
        if not os.path.exists(file_path):
            raise FileNotFoundError("Błąd: Plik nie istnieje")

        # znajdz rozszerzenie file.wav
        file_ext = str(file_path[-4:])

        # Load the audio file
        print("Ładowanie pliku...")
        if file_ext == '.mp3':
            audio = AudioSegment.from_mp3(file_path)
        elif file_ext == '.wav':
            audio = AudioSegment.from_wav(file_path)
        elif file_ext == '.ogg':
            audio = AudioSegment.from_ogg(file_path)
        else:
            # na wypadek gdyby format byl inny niż standardowe
            audio = AudioSegment.from_file(file_path)


        # informacje o pliku w kolejnosci: dlugosc (w sekundach), ilosc kanałów, rozmiar próbki, rozdzielczosc pliku
        file_Info=(str(len(audio)),str(audio.channels),str(audio.sample_width),str(audio.frame_rate))

        return(audio,file_Info)
    except Exception as e:
        print(f"Błąd: {str(e)}")

def save_audio_file(audio, output_path,**kwargs):
    try:
        #domyslnie używamy mp3
        parameters = {'format': 'mp3','bitrate':'192k','tags':{}}
        parameters.update(kwargs) #zmien domyslne argumenty jezeli takie zostaną podane
        audio.export(output_path,**parameters)
        print('Zapisano')
    except Exception as e:
        print(f'Błąd podczas zapisywania: {str(e)}')



if __name__ == "__main__":
    file_path = "file01.wav"  # test
    file_Audio,file_Info=read_audio_file(file_path)
    save_audio_file(file_Audio,'saved_file.mp3')