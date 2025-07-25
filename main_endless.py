
import LiveTranscriber

#if __name__=="__main__":stream_gpt.LiveTranscriber(conf.LANG, conf.AUDIO_DEVICE_INDEX).run()

import LiveBuffer

LiveBuffer.InitBuffer()

LiveTranscriber.LiveTranscriber().run()
