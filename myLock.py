import threading

lock = dict()

urllistLock = threading.Lock()
wordlistLock = threading.Lock()
linkLock = threading.Lock()
linkwordLock = threading.Lock()
wordlocationLock = threading.Lock()

lock["urllist"] = urllistLock
lock["wordlist"] = wordlistLock
lock["link"] = linkLock
lock["linkword"] = linkwordLock
lock["wordlocation"] = wordlocationLock 
