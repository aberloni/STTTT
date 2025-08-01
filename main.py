import LiveTranscriber
import LiveBuffer
import Locker

# make sure lock is not present when starting
Locker.RemLock()

print("init.buffer")
LiveBuffer.InitBuffer()

print("init.run transcriber")
LiveTranscriber.LiveTranscriber().run()
