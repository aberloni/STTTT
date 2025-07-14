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

import time
import datetime

today = datetime.datetime.today().strftime(conf.FILE_DATE_FORMAT)
output_raw = today + "_" + conf.OUTPUT_RAW + conf.FILE_EXT
output_translated = today + "_" + conf.OUTPUT_TRANSLATED + conf.FILE_EXT

# https://stackoverflow.com/questions/1466000/difference-between-modes-a-a-w-w-and-r-in-built-in-open-function
print("raw file @ "+str(output_raw))

with open(output_raw, "w") as f:
    f.close()

# current line qty in file
lineHead = 0
with open(output_raw, "r", encoding="utf-8") as f:
    lines = f.readlines()

    print(lines)

    lineHead = len(lines) - 1

    if lineHead < 0 : 
        lineHead = 0

    print("head starts @ "+str(lineHead))

    f.close()

open(output_translated, "a+", encoding="utf-8").close()

print("head @ "+str(lineHead))

def listen_print_loop(responses: object) -> str:
    
    num_chars_printed = 0
    words_count = 0

    global lineHead

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
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            
            line = transcript + overwrite_chars
            #sys.stdout.write(line + "\r")
            #sys.stdout.flush()

            transcriptOverride(output_raw, line, lineHead)

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

            #print(transcript + overwrite_chars)
            line = transcript + overwrite_chars
            print(".")
            
            if conf.CAN_STOP:
                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                pattern = conf.STOP
                stopped = re.search(r"("+pattern+")", transcript, re.I)
                #if re.search(r"\b("+conf.STOP+")\b", transcript, re.I):
                if stopped:
                    print("Exiting..")
                    break
            
            print("> "+line)
            
            transcriptOverride(output_raw, line, lineHead)
            asyncio.run(TranslateText(line, lineHead))
            
            lineHead = lineHead + 1
            print("head @ "+str(lineHead))
            
            words_count = 0
            num_chars_printed = 0

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

        transcriptOverride(output_translated, loca.text, lineIndex)

# "-> None" ? https://stackoverflow.com/questions/38286718/what-does-def-main-none-do

def main() -> None:

    """Transcribe speech from audio file."""
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    # language_code = "en-US"  # a BCP-47 language tag
    
    # models:
    # https://cloud.google.com/speech-to-text/docs/reference/rest/v1p1beta1/RecognitionConfig
    
    # https://cloud.google.com/speech-to-text/docs/speech-to-text-requests#select-model

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=conf.RATE,
        language_code=languages.LANG,
        model="latest_long",
        #model="command_and_search",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    ScriptLockToggle(True)

    with streams.MicrophoneStream(conf.RATE, conf.CHUNK) as stream:
        
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        print("speech.listening")
        
        #ScriptLockToggle(True)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)



def ScriptLockToggle(state):
    lockFileName = "lock" + conf.FILE_EXT
    if state:
        with open(lockFileName, "w") as f:
            f.close()
    else:
        os.remove(lockFileName)


# https://www.geeksforgeeks.org/python/detect-script-exit-in-python/
@atexit.register
def ApplicationQuit():
    print("[QUIT]")
    ScriptLockToggle(False)

if __name__ == "__main__":
    main()
