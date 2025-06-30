# What's this ?

A quick project to handle SPEECH (microphone) to TEXT to TRANSLATION (text)

# What does it do ?

- Start recording using the microphone and send chunk of audio to GSpeech.
- Receive the transcribed string after some time (often short, depends on the language & setup)
- Log the result in the console
- Dump each query in a "raw" txt file
- Translate each new line and dump it in another "translated" file

# Dependencies

Python 			: I used 3.11.9
STT 			: Google Speech (AI)	(paid service)

# Libs

Speech					: google speech lib
Audio					: pyaudio				(free)
Translation 			: googletrans 			(free somehow ?)

# How to install

- You'll need a google project https://console.cloud.google.com
- Activate the Speech to text API (require a credit card)
- Install google cloud CLI
	windows installer : https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe

In powershell/bash

	pip install --upgrade google-cloud-speech
	pip install pyaudio
	pip install googletrans

In gcloud CLI

	gcloud init

- login (it will open a browser)
- pick your project (the ID is the one you can find on the project picker on console.cloud.google.com)

	gcloud auth application-default login

# How to use

- Setup the conf file :

AUDIO_DEVICE_INDEX 	: Find the right index of the microphone you wanna use. You can run the util script that will list devices available.
LANG 				: Input language for STT transcription
LANG_TRANSL_SRC 	: Source language for translation
LANG_TRANSL_DEST 	: Destination language for translation

- Run main.py (using python, in a terminal)

*in python terminal*

- [audio] when microphone starts
- [listen] after first ping/pong with google
- [exit] when script ends

# Documentations 

**Google STT home**

https://cloud.google.com/speech-to-text?hl=en

**Transcribe streaming audio from a microphone (python)**

https://cloud.google.com/speech-to-text/docs/samples/speech-transcribe-streaming-mic?hl=en#speech_transcribe_streaming_mic-python

**googletrans**

https://py-googletrans.readthedocs.io/en/latest/

**gcloud init**

https://cloud.google.com/docs/authentication/set-up-adc-local-dev-environment


# Troubleshoot

	google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found

need to auth using gcloud cli

	gcloud auth application-default login
