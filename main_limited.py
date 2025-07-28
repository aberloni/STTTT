import re

from google.cloud import speech

import asyncio

import streams

import languages

import conf,statics
import LiveBuffer, Lock

LiveBuffer.InitBuffer()

""" 
    given responses object is a StreamingResponseIterator
    for loop will never end
    and call each iteration when new content is added/available
"""
def listen_print_loop(responses: object) -> str:
    
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

        if(Lock.CheckAppStop()): return

        if not result.is_final:
            
            # print("x"+str(len(result.alternatives)) + " " + str(alt.confidence) + " > " + line)

            LiveBuffer.OverrideTranscript(line)

            num_chars_printed = len(transcript)

            # translate every N words
            sps = line.split()
            cnt = len(sps)
            if cnt > words_count:
                if cnt % statics.SPLIT_WORD_COUNT == 0:
                    words_count = cnt
                    
                    #print("count ? "+str(words_count)+" = "+line)
                    
                    asyncio.run(LiveBuffer.TranslateText(line))
                    
        else: # FINAL

            if statics.CAN_STOP:
                
                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                pattern = statics.STOP
                stopped = re.search(r"("+pattern+")", transcript, re.I)

                if stopped:
                    
                    print("[command.exit]")
                    
                    Lock.ApplicationQuit() # release lock

                    break
            
            # didn't stop, yet

            print(" . "+line) #is final !
            
            LiveBuffer.OverrideTranscript(line)
            asyncio.run(LiveBuffer.TranslateText(line))
            
            LiveBuffer.IncrementHead()
            

    print("listen.stop")
    return transcript


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
        sample_rate_hertz=statics.RATE,
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
    Lock.ScriptLockToggle(True)

    with streams.MicrophoneStream(statics.RATE, statics.CHUNK) as stream:
        
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

if __name__ == "__main__":
    main()
