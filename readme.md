# What's this ?

A quick project to handle SPEECH (microphone) to TEXT to TRANSLATION (text)

# What does it do ?

- Start recording using the microphone and send chunk of audio to GSpeech.
- Receive the transcribed string after some time (often short, depends on the language & setup)
- Log the result in the console
- Dump each query in a "raw" txt file
- Translate each new line and dump it in another "translated" file

# Dependencies

STT 			: Google Speech (AI)	(paid service)

# Libs

Translation 	: googletrans 			(free somehow ?)

# How to install/use

- You'll need a google project https://console.cloud.google.com
- Activate the Speech to text API (require a credit card)
- Install google cloud CLI https://cloud.google.com/sdk/docs/install

In gcloud CLI

	gcloud init

- Set conf file stuff to your liking
- Run this python script

# Documentations 

**Google STT home**

https://cloud.google.com/speech-to-text?hl=en

**Transcribe streaming audio from a microphone (python)**

https://cloud.google.com/speech-to-text/docs/samples/speech-transcribe-streaming-mic?hl=en#speech_transcribe_streaming_mic-python

**googletrans**

https://py-googletrans.readthedocs.io/en/latest/

**gcloud init**

https://cloud.google.com/docs/authentication/set-up-adc-local-dev-environment
