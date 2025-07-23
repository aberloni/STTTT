
OUTPUT_FOLDER = "locals/"

# where the text is appended
OUTPUT_RAW = "output_raw"
OUTPUT_TRANSLATED = "output_translated"

FILE_DATE_FORMAT = "%Y-%m-%d"
FILE_EXT = ".peeps"

SPLIT_WORD_COUNT = 3

# AUDIO

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

CAN_STOP = True
STOP = "stop|exit|quitter"
