
# AUDIO

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# TRANSCRIPTION

# https://en.wikipedia.org/wiki/IETF_language_tag#List_of_common_primary_language_subtags
# a BCP-47 language tag

# list of possible language to set in LANG
lang_en = "en-US"
lang_fr = "fr"

# AI language target
LANG = lang_en

# https://py-googletrans.readthedocs.io/en/latest/#googletrans.models.Translated

# where the text is appended
OUTPUT_RAW = "output_raw"
OUTPUT_TRANSLATED = "output_translated"

FILE_DATE_FORMAT = "%Y-%m-%d"

FILE_EXT = ".txt"

CAN_STOP = True
STOP = "stop|exit"


# Models
# https://cloud.google.com/speech-to-text/docs/reference/rest/v1/RecognitionConfig

# ONLY for EN
# latest_long : Best for long form content like media or conversation.