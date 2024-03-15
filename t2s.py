import torch, os
import wave
import pyogg
from random import randint

def wav2opus(filename):
    # Read a wav file to obtain PCM data
    wave_read = wave.open(filename, "rb")

    # Extract the wav's specification
    channels = wave_read.getnchannels()
    samples_per_second = wave_read.getframerate()
    bytes_per_sample = wave_read.getsampwidth()
    original_length = wave_read.getnframes()

    # Create a OpusBufferedEncoder
    opus_buffered_encoder = pyogg.OpusBufferedEncoder()
    opus_buffered_encoder.set_application("audio")
    opus_buffered_encoder.set_sampling_frequency(samples_per_second)
    opus_buffered_encoder.set_channels(channels)
    opus_buffered_encoder.set_frame_size(20) # milliseconds
    
    # Create an OggOpusWriter
    output_filename = filename.replace('wav', 'opus')
    ogg_opus_writer = pyogg.OggOpusWriter(
        output_filename,
        opus_buffered_encoder)

    # Calculate the desired frame size (in samples per channel)
    desired_frame_duration = 20/1000 # milliseconds
    desired_frame_size = int(desired_frame_duration * samples_per_second)

    # Loop through the wav file's PCM data and write it as OggOpus
    chunk_size = 1000 # bytes
    while True:
        # Get data from the wav file
        pcm = wave_read.readframes(chunk_size)
        #print(pcm)
        # Check if we've finished reading the wav file
        if len(pcm) == 0:
            break

        # Encode the PCM data
        ogg_opus_writer.write(
            memoryview(bytearray(pcm))) # FIXME
        
    # We've finished writing the file
    ogg_opus_writer.close()
    wave_read.close()
    os.remove(filename)

    return output_filename
        
def t2s_init():
    device = torch.device('cpu')
    torch.set_num_threads(4)
    local_file_ru = 'model.pt'
    
    model = torch.package.PackageImporter(local_file_ru).load_pickle('tts_models', 'model')
    model.to(device)

    speaker = 'en_' + str(randint(0, 100))
    print('Silero initialized')
    return model, speaker

def t2s(text, model, speaker):
    sample_rate = 48000

    audio = model.apply_tts(text=text, speaker=speaker, sample_rate=sample_rate)
    result = model.save_wav(text=text, speaker=speaker,
                    sample_rate=sample_rate, audio_path='voice.wav')
    result = wav2opus(result)

    return result

# EOF
