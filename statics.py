
OUTPUT_FOLDER = "locals/"

# where the text is appended
OUTPUT_RAW = "output_raw"
OUTPUT_TRANSLATED = "output_translated"

FILE_DATE_FORMAT = "%Y-%m-%d"
FILE_EXT = ".peeps"

SPLIT_WORD_COUNT = 3

# AUDIO

SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

STREAMING_LIMIT = 240000

CAN_STOP = True
STOP = "stop|exit|quitter"
