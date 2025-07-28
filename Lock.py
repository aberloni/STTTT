import statics
import os, sys

""" true : lock is present """
def CheckLockPresence():
    lockFileName = "lock" + statics.FILE_EXT
    return os.path.exists(lockFileName)

""" toggle script lock """
def ScriptLockToggle(setLock):
    lockFileName = "lock" + statics.FILE_EXT
    
    if setLock and not CheckLockPresence():
        open(lockFileName, "w").close()
    elif not setLock:
        os.remove(lockFileName)

    print("lock:" + str(setLock))

""" kill script is lock file is removed by something else """
def CheckAppStop():

    if not CheckLockPresence():
        print("/! script lock missing")
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
