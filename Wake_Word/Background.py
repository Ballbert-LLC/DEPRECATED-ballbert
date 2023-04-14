from pydub import AudioSegment

# ask the user to input the path to the audio file
print("Please input the path to the audio file:")
audio_path = input()

# load the audio file using pydub
print("Loading audio file...")
audio = AudioSegment.from_file(audio_path)

for x in range(0, 100):

    segement_length_ms = 2000

    # extract the first two seconds of the audio
    first_two_seconds = audio[x*segement_length_ms:x*(segement_length_ms+1)]

    # ask the user to input the path to save the new file
    new_file_path = f"background_sound/{x}.wav"

    # save the first two seconds to a new file using pydub
    first_two_seconds.export(new_file_path, format="wav")

print("Done.")
