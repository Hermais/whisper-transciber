; Define a flag variable
ignoreShortcut := false

#j::
; Check if the flag is set to true
if (ignoreShortcut)
{
    ; If the flag is true, reset it to false and exit
    ignoreShortcut := false
    return
}

; If the flag is false, run the program and set the flag to true
Run, "C:\Users\gombi\AppData\Local\Programs\Python\Python312\python.exe" "D:\Python_Projects\whisper_transcriber\whisper_transcriber_manager.py"
ignoreShortcut := true
return
