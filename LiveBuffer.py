import os

import datetime
import asyncio

import googletrans

import statics, ConfLanguages

today = datetime.datetime.today().strftime(statics.FILE_DATE_FORMAT)

path_raw = statics.OUTPUT_FOLDER + today + "_" + statics.OUTPUT_RAW + statics.FILE_EXT
path_translated = statics.OUTPUT_FOLDER + today + "_" + statics.OUTPUT_TRANSLATED + statics.FILE_EXT

words_count = 0
lineHead = 0

""" 
make sure file & parent folder exists
"""
def FileSanity(path):
    print("sanity check file @ "+path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.close()

# https://stackoverflow.com/questions/1466000/difference-between-modes-a-a-w-w-and-r-in-built-in-open-function

def InitBuffer():
    
    global lineHead

    # first wipe files &/OR make sure they exists
    FileSanity(path_raw)
    FileSanity(path_translated)

    # current line qty in file
    lineHead = 0
    with open(path_raw, "r", encoding="utf-8") as f:
        lines = f.readlines()

        print(lines)

        lineHead = len(lines) - 1

        if lineHead < 0 : 
            lineHead = 0

        print("head starts @ "+str(lineHead))

        f.close()

    open(path_translated, "a+", encoding="utf-8").close()

    print("head @ "+str(lineHead))
    

def OverrideTranscript(line):
    BufferOverride(path_raw, line)

def OverrideTranslation(line):
    BufferOverride(path_translated, line)

def BufferOverride(fname, line):

    # remove empty spaces
    line = line.strip()
    if len(line) <= 0:
        return

    with open(fname, "r", encoding="utf-8") as f:
        lines = f.readlines()
        f.close()

    while len(lines) <= lineHead:
        lines.append("")
    
    lines[lineHead] = line + "\n"
    
    with open(fname, "w", encoding="utf-8") as f:
        
        f.writelines(lines)
        f.close()


def IncrementHead():
    global lineHead, words_count

    lineHead = lineHead + 1
    
    print("head @ "+str(lineHead))
    
    # reset word count
    words_count = 0

"""
counting words in streamed transcript
meant to trigger a translation while someone is talking too much
"""
def TranscriptSolve(transcript):
    
    global words_count

    # translate every N words
    sps = transcript.split()
    cnt = len(sps)
    if cnt > words_count:
        if cnt % statics.SPLIT_WORD_COUNT == 0:
            words_count = cnt
            
            #print("count ? "+str(words_count)+" = "+line)
            DoTranslate(transcript)

"""
trigger a query for translation
"""
def DoTranslate(transcript):
    asyncio.run(TranslateText(transcript))

async def TranslateText(line):
    async with googletrans.Translator() as tr:
        loca = await tr.translate(text=line, 
                                  src=googletrans.LANGUAGES[ConfLanguages.LANG_TRANSL_SRC], 
                                  dest=googletrans.LANGUAGES[ConfLanguages.LANG_TRANSL_DST])

        OverrideTranslation(loca.text)
