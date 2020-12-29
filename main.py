# Author: George Papadopoulos
# E-mail: georgepap2001@gmail.com

# import library
# https://realpython.com/python-speech-recognition/
import speech_recognition as sr
import os

# Convert .mp3 to .wav
# https://stackoverflow.com/questions/32073278/python-convert-mp3-to-wav-with-pydub
import subprocess

# Get .wav file duration
# https://stackoverflow.com/questions/7833807/get-wav-file-length-or-duration
import wave
import contextlib

# Split .wav file
# https://stackoverflow.com/questions/37999150/how-to-split-a-wav-file-into-multiple-wav-files
from pydub import AudioSegment

# Remove folders
import shutil

# Check if the audio is .wav file type
def audio_file_is_wav(audio_file_path):
    if (audio_file_path.endswith('.wav')):
        return True
    else:
        return False


# Create temp folder in current working directory
def create_tmp_folder():
    try:
        os.mkdir(os.getcwd() + '\\temp')
    except OSError:
        # Folder could not create
        return False
    else:
        # Folder created
        return True


# Create Temp subfolder
def create_tmp_sbfolder():
    # Check if Temp folder exists
    if (not check_temp_folder()):
        # Temp folder is NOT exists
        # Create Temp folder
        create_tmp_folder()

    # Check if Temp folder exists
    if (check_temp_folder()):
        # Temp folder exists
        try:
            os.mkdir(os.getcwd() + '\\temp\\splittedAudio')
        except OSError:
            # Folder could not create
            return False
        else:
            # Folder created
            return True


# Temp folder checker (checking if folder exists)
def check_temp_folder():
    if (os.path.isdir('./temp')):
        return True
    else:
        return False

# Deleting the Temp folder
def delete_temp_folder():
    try:
        shutil.rmtree('./temp')
    except OSError:
        # Deletion of the folder failed
        return False
    else:
        # Deletion of the folder succeeded
        return True

# Convert any audio file to .wav file type
def convert_audio_to_wav(audio_file_path):
    subprocess.call(['ffmpeg', '-i', audio_file_path,
                     os.getcwd() + '\\temp\\' + os.path.basename(audio_file_path).replace('mp3', 'wav')])


# Speech Recognition - Returns string with the contents
def speech_recognition(audio_file_path, language):
    # Initialize main list to save audio transcript
    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()

    # Reading Audio file as source
    # listening the audio file and store in audio_text variable

    with sr.AudioFile(audio_file_path) as source:
        audio_text = r.listen(source)
        # recognize_() method will throw a request error if the API is unreachable, hence using exception handling
        try:
            # using google speech recognition
            return r.recognize_google(audio_text, language=language)
        except:
            # Could not recognize anything - Returns empty string
            return ''


# Get .wav file duration - Returns duration in seconds
def get_wav_duration(audio_file_path):
    with contextlib.closing(wave.open(audio_file_path, 'r')) as f:
        return f.getnframes() / float(f.getframerate())


# Break audio file to separate files with max 2 minutes duration - Returns the splitter counter
def break_wav_file(audio_file_path):
    # Call function to create a subfolder
    # Check if subfolder created
    if (create_tmp_sbfolder()):
        # Setup timers to split audio
        timer1 = 0  # 0s
        # Check if wav duration in less that 60s
        if (round(get_wav_duration(audio_file_path)) < 60):
            # Duration is less than 60s
            # Set timer2 as the end of the wav duration
            timer2 = round(get_wav_duration(audio_file_path)) * 1000
        else:
            # Duration is greater than 60s
            # Set timer2 to 60s
            timer2 = 60000

        cnt = 0
        while (timer2 >= round(get_wav_duration(audio_file_path))):
            newAudio = AudioSegment.from_wav(audio_file_path)
            newAudio = newAudio[timer1:timer2]
            newAudio.export('./temp/splittedAudio/splittedWav' + str(cnt) + '.wav',
                            format="wav")  # Exports to a wav file in the current path.
            cnt += 1
            timer1 = timer2 + 1
            # Check if wav duration in less that 60s
            if (round(get_wav_duration(audio_file_path)) * 1000 == timer2):
                # timer2 is equal with the total .wav duration
                # break the while loop
                break
                # Check if the total duration of .wav file is equal with timer2
            elif (round(get_wav_duration(audio_file_path)) * 1000 < timer2 + 60000):
                # Duration is less than 60s
                # Set timer2 as the end of the wav duration
                timer2 = round(get_wav_duration(audio_file_path)) * 1000
            else:
                # Duration is greater than 60s
                # Set timer2 to 60s
                timer2 = timer2 + 60000

        return cnt
    else:
        print('Could not create Temp subfolder')

# Convert double size list to one list
def convert_to_one_list(text_list):
    one_list = []
    for sublist in text_list:
        for item in sublist:
            one_list.append(item)

    return one_list

# Speech to text MAIN program
def speech_to_text_main(audio_file_src, language):
    # Setting the export list
    transcript_contents = []
    # Check if file is .wav
    if (not audio_file_is_wav(audio_file_src)):
        # File is NOT .wav
        # Create tmp folder
        # Check if tmp folder is created
        if (create_tmp_folder()):
            # Folder created
            # Convert audio file to .wav
            convert_audio_to_wav(audio_file_src)
        else:
            # Folder could not create
            print('Temp folder could not create')
    else:
        # Temp folder exists
        print('Temp Folder already exists')

    # Check if file is .wav. If True then Run speech recognition
    if (audio_file_is_wav(audio_file_src)):
        # Check if audio duration is above 2 minutes
        if (round(get_wav_duration(audio_file_src)) > 121):
            # Audio duration is adove 2 minutes
            # Breaking the file into smaller (60s) files
            splitted_files_counter = break_wav_file(audio_file_src)
            cnt = 0
            while cnt != splitted_files_counter - 1:
                transcript_contents.append(
                    speech_recognition('./temp/splittedAudio/splittedWav' + str(cnt) + '.wav', language).split(' '))
                cnt += 1
        else:
            # Audio duration is below 2 minutes
            # Do the speech recognition
            transcript_contents.append(speech_recognition(audio_file_src, language))
    # If file is not .wav then check if temp folder has created
    elif (not audio_file_is_wav(audio_file_src) and check_temp_folder()):
        transcript = speech_recognition(os.getcwd() + '\\temp\\' + os.path.basename(audio_file_src).replace('mp3', 'wav'), language)
        # Check if audio duration is above 2 minutes
        if (round(get_wav_duration(os.getcwd() + '\\temp\\' + os.path.basename(audio_file_src).replace('mp3', 'wav'))) > 121):
            # Audio duration is adove 2 minutes
            # Breaking the file into smaller (60s) files
            splitted_files_counter = break_wav_file(os.getcwd() + '\\temp\\' + os.path.basename(audio_file_src).replace('mp3', 'wav'))
            cnt = 0
            while cnt != splitted_files_counter - 1:
                transcript_contents.append(speech_recognition('./temp/splittedAudio/splittedWav' + str(cnt) + '.wav', language).split(' '))
                cnt += 1
        else:
            # Audio duration is below 2 minutes
            # Do the speech recognition
            transcript_contents.append(speech_recognition(os.getcwd() + '\\temp\\' + os.path.basename(audio_file_src).replace('mp3', 'wav'), language))


    # Check if transcript is NOT empty
    if transcript_contents:
        # Transcript is NOT empty
        # Check if temp folder exists
        if (check_temp_folder()):
            # Temp folder exists
            # Removing the temp folder
            delete_temp_folder()
        # Transcript is READY and available in transcript_contents variable (list)
        # Put your logic below that point
        print(transcript_contents)
        print(convert_to_one_list(transcript_contents))
        print(type(transcript_contents))
    else:
        # Transcript is empty
        print('Could not recognise speech. File is too large.')

# break_wav_file('E:\\European School Radio\\Audio to Text\\575711.wav')
speech_to_text_main('E:\\European School Radio\\Audio to Text\\5757.mp3', 'el-GR')
