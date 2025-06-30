
# TRANSCRIPTION

# https://en.wikipedia.org/wiki/IETF_language_tag#List_of_common_primary_language_subtags
# a BCP-47 language tag

# STT language target
LANG = "en-US"

# TRANSLATION

# Translation source to destination
# see googletrans.LANGUAGES for list of possible languages
LANG_TRANSL_SRC = "en"
LANG_TRANSL_DEST = "fr"

# https://py-googletrans.readthedocs.io/en/latest/#googletrans.models.Translated

SPLIT_WORD_COUNT = 3

# EXPORT FILES

# where the text is appended
OUTPUT_RAW = "output_raw"
OUTPUT_TRANSLATED = "output_translated"

FILE_DATE_FORMAT = "%Y-%m-%d"
FILE_EXT = ".txt"

# STOP detection

CAN_STOP = True
STOP = "stop|exit"

# AUDIO

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

AUDIO_DEVICE_INDEX = 2

# NOTES

# Models
# https://cloud.google.com/speech-to-text/docs/reference/rest/v1/RecognitionConfig

# ONLY for EN
# latest_long : Best for long form content like media or conversation.
