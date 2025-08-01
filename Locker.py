import statics
import os, sys

lockFileName = "lock" + statics.FILE_EXT

""" true : lock is present """
def CheckLockPresence():
    global lockFileName
    presence = os.path.exists(lockFileName)
    return presence

def RemLock():
    global lockFileName
    if CheckLockPresence():
        print("removing "+lockFileName)
        os.remove(lockFileName)

""" toggle script lock """
def ScriptLockToggle(setLock):
    global lockFileName
    
    hasLock = CheckLockPresence()

    if setLock and not hasLock:
        print(" +LOCK")
        open(lockFileName, "w").close()
    elif not setLock and hasLock:
        print(" -LOCK")
        os.remove(lockFileName)

""" kill script is lock file is removed by something else """
def CheckAppStop():

    if not CheckLockPresence():
        print("/! script lock is missing")
        ApplicationQuit()
        return True
    
    return False


# https://www.geeksforgeeks.org/python/detect-script-exit-in-python/
def ApplicationQuit():

    print("[QUIT]")

    # remove lock if present
    if CheckLockPresence():
        ScriptLockToggle(False)

    print(" > exit()")
    sys.exit()
