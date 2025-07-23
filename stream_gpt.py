import queue, re, sys, time
from google.cloud import speech
import pyaudio
import conf

STREAMING_LIMIT = 240000
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)

LANG = conf.LANG
INDEX_MIC = conf.AUDIO_DEVICE_INDEX

class LiveTranscriber:
    def __init__(self):
        self.client = speech.SpeechClient()
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code=LANG,
            max_alternatives=1,
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config, interim_results=True
        )
        self.mic = self.ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)

    class ResumableMicrophoneStream:
        def __init__(self, rate, chunk_size):
            self._rate = rate
            self.chunk_size = chunk_size
            self._num_channels = 1
            self._buff = queue.Queue()
            self.closed = True
            self.start_time = self._time()
            self.restart_counter = 0
            self.audio_input = []
            self.last_audio_input = []
            self.result_end_time = 0
            self.is_final_end_time = 0
            self.final_request_end_time = 0
            self.bridging_offset = 0
            self.last_transcript_was_final = False
            self.new_stream = True
            self._audio_interface = pyaudio.PyAudio()
            self._audio_stream = self._audio_interface.open(
                format=pyaudio.paInt16,
                channels=self._num_channels,
                rate=self._rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._fill_buffer,
                input_device_index=INDEX_MIC
            )
        def _time(self): return int(round(time.time() * 1000))
        def __enter__(self): self.closed=False;return self
        def __exit__(self,*a): self._audio_stream.stop_stream();self._audio_stream.close();self.closed=True;self._buff.put(None);self._audio_interface.terminate()
        def _fill_buffer(self, in_data, *a, **k): self._buff.put(in_data); return None, pyaudio.paContinue
        def generator(self):
            while not self.closed:
                data=[]
                if self.new_stream and self.last_audio_input:
                    chunk_time=STREAMING_LIMIT/len(self.last_audio_input)
                    if chunk_time:
                        if self.bridging_offset<0: self.bridging_offset=0
                        if self.bridging_offset>self.final_request_end_time: self.bridging_offset=self.final_request_end_time
                        chunks_from_ms=round((self.final_request_end_time - self.bridging_offset)/chunk_time)
                        self.bridging_offset=round((len(self.last_audio_input)-chunks_from_ms)*chunk_time)
                        data.extend(self.last_audio_input[chunks_from_ms:])
                    self.new_stream=False
                chunk=self._buff.get()
                self.audio_input.append(chunk)
                if chunk is None: return
                data.append(chunk)
                while True:
                    try:
                        chunk=self._buff.get(block=False)
                        if chunk is None: return
                        data.append(chunk)
                        self.audio_input.append(chunk)
                    except queue.Empty: break
                yield b"".join(data)

    def listen_print_loop(self,responses,stream):
        for response in responses:
            if self._time()-stream.start_time>STREAMING_LIMIT:
                stream.start_time=self._time();break
            if not response.results:continue
            result=response.results[0]
            if not result.alternatives:continue
            transcript=result.alternatives[0].transcript
            rs,rm=0,0
            if result.result_end_time.seconds: rs=result.result_end_time.seconds
            if result.result_end_time.microseconds: rm=result.result_end_time.microseconds
            stream.result_end_time=int((rs*1000)+(rm/1000))
            corrected=stream.result_end_time - stream.bridging_offset + (STREAMING_LIMIT*stream.restart_counter)
            if result.is_final:
                
                print("."+transcript)

                stream.is_final_end_time=stream.result_end_time
                stream.last_transcript_was_final=True
                if re.search(r"\b(exit|quit)\b",transcript,re.I): print("Exiting...");stream.closed=True;break
            else:
                
                print(">"+transcript)
                
                stream.last_transcript_was_final=False

    def run(self):
        with self.mic as stream:
            while not stream.closed:
                print(f"\n{STREAMING_LIMIT*stream.restart_counter}: NEW REQUEST")
                stream.audio_input=[]
                audio_generator=stream.generator()
                requests=(speech.StreamingRecognizeRequest(audio_content=c) for c in audio_generator)
                responses=self.client.streaming_recognize(self.streaming_config,requests)
                self.listen_print_loop(responses,stream)
                if stream.result_end_time>0: stream.final_request_end_time=stream.is_final_end_time
                stream.result_end_time=0
                stream.last_audio_input=stream.audio_input
                stream.audio_input=[]
                stream.restart_counter+=1
                if not stream.last_transcript_was_final: print()
                stream.new_stream=True
    def _time(self): return int(round(time.time()*1000))

# if __name__=="__main__":
    # LiveTranscriber().run()
