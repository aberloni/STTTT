import queue
import re
import sys

from google.cloud import speech

import pyaudio

import googletrans

import asyncio

import conf

# Audio recording parameters
#RATE = 16000
#CHUNK = int(RATE / 10)  # 100ms

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

class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self: object, rate: int = conf.RATE, chunk: int = conf.CHUNK) -> None:
        """The audio -- and generator -- is guaranteed to be on the main thread."""
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self: object) -> object:
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
            input_device_index=conf.AUDIO_DEVICE_INDEX
        )

        print("[audio]")
        
        self.closed = False

        return self

    def __exit__(
        self: object,
        type: object,
        value: object,
        traceback: object,
    ) -> None:
        """Closes the stream, regardless of whether the connection was lost or not."""
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()
        print("[exit]")

    def _fill_buffer(
        self: object,
        in_data: object,
        frame_count: int,
        time_info: object,
        status_flags: object,
    ) -> object:
        """Continuously collect data from the audio stream, into the buffer.

        Args:
            in_data: The audio data as a bytes object
            frame_count: The number of frames captured
            time_info: The time information
            status_flags: The status flags

        Returns:
            The audio data as a bytes object
        """
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self: object) -> object:
        """Generates audio chunks from the stream of audio data in chunks.

        Args:
            self: The MicrophoneStream object

        Returns:
            A generator that outputs audio chunks.
        """
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

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
                                  src=googletrans.LANGUAGES[conf.LANG_TRANSL_SRC], 
                                  dest=googletrans.LANGUAGES[conf.LANG_TRANSL_DEST])

        transcriptOverride(output_translated, loca.text, lineIndex)


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
        language_code=conf.LANG,
        model="latest_long",
        #model="command_and_search",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(conf.RATE, conf.CHUNK) as stream:
        
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        print("[LISTEN]")
        
        # Now, put the transcription responses to use.
        listen_print_loop(responses)


if __name__ == "__main__":
    main()

