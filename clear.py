import os, sys

if sys.platform != "win32":
    print("clear: unsupported platform", sys.platform)
    sys.exit(2)
    
os.system('cls')

