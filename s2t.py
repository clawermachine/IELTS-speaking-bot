from vosk import Model, KaldiRecognizer
import os
import wave
import pyaudio
import json
import librosa
import soundfile as sf  

def ogg2wav(file, Fs):
    data, samplerate = sf.read(file)
    new_file = file.replace('ogg', 'wav')
    data_resampled = librosa.resample(data, orig_sr=samplerate, target_sr=Fs)
    sf.write(new_file, data_resampled, Fs)
    length = librosa.get_duration(path=file)
    os.remove(file)
    return new_file, length
    
def download_model():

    import requests, zipfile
    from io import BytesIO

    url = 'https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip'
    filename = url.split('/')[-1]

    req = requests.get(url)
    zipfile= zipfile.ZipFile(BytesIO(req.content))
    zipfile.extractall('models/')

def s2t_init():
    lang = 'en-large'
    paths = {'en-small': r"models\vosk-model-small-en-us-0.15",
             'en-large': r"models\vosk-model-en-us-0.42-gigaspeech"}

    if lang[-5:] == 'small':
        Fs = 44100
    elif lang[-5:] == 'large':
        Fs = 8000

    if not os.path.isdir(paths[lang]):
        download_model()
        
    assert os.path.isdir(paths[lang]), 'Silero model not found'
    
    model = Model(paths[lang]) # полный путь к модели
  
    rec = KaldiRecognizer(model, Fs)
    print('Vosk initailized')
    
    return rec, Fs

def s2t(file, rec, Fs):
    
    file, length = ogg2wav(file, Fs)
    wf = wave.open(file, 'rb')
    result = ''
    last_n = False

    
    while True:
        data = wf.readframes(Fs)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())['text']
            
            if res != '':
                result += f" {res}"
                last_n = False
            elif not last_n:
                result += '\n'
                last_n = True

    res = json.loads(rec.FinalResult())['text']
    result += f" {res}"
    
    wf.close()
    os.remove(file)
    return result, length

# EOF
