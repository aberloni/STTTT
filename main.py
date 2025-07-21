import re

from google.cloud import speech

import googletrans

import asyncio

import conf
import languages

import streams
import os

import atexit

# Audio recording parameters
#RATE = 16000
#CHUNK = int(RATE / 10)  # 100ms

import datetime

today = datetime.datetime.today().strftime(conf.FILE_DATE_FORMAT)

path_raw = conf.OUTPUT_FOLDER + today + "_" + conf.OUTPUT_RAW + conf.FILE_EXT
path_translated = conf.OUTPUT_FOLDER + today + "_" + conf.OUTPUT_TRANSLATED + conf.FILE_EXT

# https://stackoverflow.com/questions/1466000/difference-between-modes-a-a-w-w-and-r-in-built-in-open-function
print("raw file @ "+str(path_raw))

# first wipe files &/OR make sure they exists
with open(path_raw, "w", encoding="utf-8") as f:
    f.close()

with open(path_translated, "w", encoding="utf-8") as f:
    f.close()

# current line qty in file
lineHead = 0
with open(path_raw, "r", encoding="utf-8") as f:
    lines = f.readlines()

    print(lines)

    lineHead = len(lines) - 1

    if lineHead < 0 : 
        lineHead = 0

    print("head starts @ "+str(lineHead))

    f.close()

open(path_translated, "a+", encoding="utf-8").close()

print("head @ "+str(lineHead))

""" 
    given responses object is a StreamingResponseIterator
    for loop will never end
    and call each iteration when new content is added/available
"""
def listen_print_loop(responses: object) -> str:
    
    num_chars_printed = 0
    words_count = 0

    global lineHead
    
    print("listen.start")
    
    for response in responses:

        if not response.results:
            continue
        
        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        alt = result.alternatives[0]
        transcript = alt.transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))
        line = transcript + overwrite_chars
        print(" > "+line)

        # RESULT DOCUMENTATION
        # https://cloud.google.com/speech-to-text/docs/reference/rpc/google.cloud.speech.v1p1beta1#speechrecognitionalternative

        """ kill script is lock file is removed by something else """
        if not CheckLockPresence():
            print("/! script lock missing")
            ApplicationQuit()
            return

        if not result.is_final:
            
            # print("x"+str(len(result.alternatives)) + " " + str(alt.confidence) + " > " + line)

            transcriptOverride(path_raw, line, lineHead)

            num_chars_printed = len(transcript)

            # translate every N words
            sps = line.split()
            cnt = len(sps)
            if cnt > words_count:
                if cnt % conf.SPLIT_WORD_COUNT == 0:
                    words_count = cnt
                    
                    #print("count ? "+str(words_count)+" = "+line)
                    
                    asyncio.run(TranslateText(line, lineHead))
                    
        else: # FINAL

            if conf.CAN_STOP:
                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                pattern = conf.STOP
                stopped = re.search(r"("+pattern+")", transcript, re.I)
                #if re.search(r"\b("+conf.STOP+")\b", transcript, re.I):
                if stopped:
                    
                    print("[command.exit]")
                    
                    ApplicationQuit() # release lock

                    break
            
            # didn't stop, yet

            print(" . "+line) #is final !
            
            transcriptOverride(path_raw, line, lineHead)
            asyncio.run(TranslateText(line, lineHead))
            
            lineHead = lineHead + 1
            print("head @ "+str(lineHead))
            
            words_count = 0
            num_chars_printed = 0

    print("listen.stop")
    return transcript


def transcriptOverride(fname, line, lineIndex):

    # remove empty spaces
    line = line.strip()
    if len(line) <= 0:
        return

    with open(fname, "r", encoding="utf-8") as f:
        lines = f.readlines()
        f.close()

    while len(lines) <= lineIndex:
        lines.append("")
    
    lines[lineIndex] = line + "\n"
    
    with open(fname, "w", encoding="utf-8") as f:
        
        f.writelines(lines)
        f.close()


async def TranslateText(line, lineIndex):
    async with googletrans.Translator() as tr:
        loca = await tr.translate(text=line, 
                                  src=googletrans.LANGUAGES[languages.LANG_TRANSL_SRC], 
                                  dest=googletrans.LANGUAGES[languages.LANG_TRANSL_DST])

        transcriptOverride(path_translated, loca.text, lineIndex)

# "-> None" ? https://stackoverflow.com/questions/38286718/what-does-def-main-none-do

def main() -> None:

    """Transcribe speech from audio file."""
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    # language_code = "en-US"  # a BCP-47 language tag
    
    # https://cloud.google.com/speech-to-text/docs/reference/rest/v1p1beta1/RecognitionConfig
    
    # models:
    # https://cloud.google.com/speech-to-text/docs/speech-to-text-requests#select-model

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=conf.RATE,
        language_code=languages.LANG,
        model="latest_long",
        #model="latest_short",
        #model="command_and_search",
    )

    # Doc.StreamingRecognitionConfig
    # https://cloud.google.com/python/docs/reference/speech/latest/google.cloud.speech_v1p1beta1.types.StreamingRecognitionConfig

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, 
        #single_utterance=True,
        interim_results=True # If false or omitted, only is_final=true result(s) are returned. 
    )

    # set lock
    ScriptLockToggle(True)

    with streams.MicrophoneStream(conf.RATE, conf.CHUNK) as stream:
        
        audio_generator = stream.generator() # while stream not closed

        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        print("speech.listening")
        
        #ScriptLockToggle(True)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)

""" true : lock is present """
def CheckLockPresence():
    lockFileName = "lock" + conf.FILE_EXT
    return os.path.exists(lockFileName)

""" toggle script lock """
def ScriptLockToggle(state):
    lockFileName = "lock" + conf.FILE_EXT
    if state:
        open(lockFileName, "w").close()
    else:
        os.remove(lockFileName)

    print("lock:" + str(state))


# https://www.geeksforgeeks.org/python/detect-script-exit-in-python/
@atexit.register
def ApplicationQuit():
    print("[QUIT]")
    
    if CheckLockPresence():
        ScriptLockToggle(False)

if __name__ == "__main__":
    main()
