import re
import pprint
import os
import json
import shutil

TORRENT_DIR = '/volume1/@appstore/transmission/var/torrents'
SORTED_DIR = '/volume1/Media/Sorted'
DOWNLOAD_DIR = '/volume1/Media/Uncategorized'

TRACKERS = {
    "broadcasthe.net": "TV",
    "passthepopcorn": "Movies",
    "what.cd": "Misc"
}

def tokenize(text, match=re.compile("([idel])|(\d+):|(-?\d+)").match):
    i = 0
    while i < len(text):
        m = match(text, i)
        s = m.group(m.lastindex)
        i = m.end()
        if m.lastindex == 2:
            yield "s"
            yield text[i:i+int(s)]
            i = i + int(s)
        else:
            yield s

def decode_item(next, token):
    if token == "i":
        # integer: "i" value "e"
        data = int(next())
        if next() != "e":
            raise ValueError
    elif token == "s":
        # string: "s" value (virtual tokens)
        data = next()
    elif token == "l" or token == "d":
        # container: "l" (or "d") values "e"
        data = []
        tok = next()
        while tok != "e":
            data.append(decode_item(next, tok))
            tok = next()
        if token == "d":
            data = dict(zip(data[0::2], data[1::2]))
    else:
        raise ValueError
    return data

def decode(text):
    try:
        src = tokenize(text)
        data = decode_item(src.next, src.next())
        for token in src: # look for more tokens
            raise SyntaxError("trailing junk")
    except (AttributeError, ValueError, StopIteration):
        raise SyntaxError("syntax error")
    return data

def getTorrentFileInfo():
    fileArr = []
    for root, subFolders, files in os.walk(TORRENT_DIR):
        for file in files:
            filePath = os.path.join(root,file)

            data = open(filePath, "rb").read()
            torrent = decode(data)

            fileNameArr = file.split('.')
            fileNameArr.pop()
            fileNameArr.pop()
            fileNameArr.pop()

            announceUrl = torrent['announce']
            fileArr.append({'announce': announceUrl, 'fileName': '.'.join(fileNameArr)})
    
    return fileArr

def getDownloadedFiles():
    fileArr = []
    for root, subFolders, files in os.walk(DOWNLOAD_DIR):
        for file in files:
            filePath = os.path.join(root,file)
            fileArr.append(filePath)
    
    return fileArr

def copyFileToFolder(torrentArr, fullPath):
    for tracker, folderName in TRACKERS.items():
        if torrentArr['announce'].find(tracker) >= 0:
            folderToCopyTo = folderName

    if folderToCopyTo and not os.path.exists(SORTED_DIR + '/' + folderToCopyTo + '/' + fullPath.split('/')[-1]): 
        print 'Copying "' + fullPath + '" to "' + folderToCopyTo + '" Folder'
        # shutil.copy(fullPath, SORTED_DIR + '/' + folderToCopyTo)
        os.link(fullPath, SORTED_DIR + '/' + folderToCopyTo + '/' + fullPath.split('/')[-1])

if __name__ == "__main__":
    torrentFiles = getTorrentFileInfo()
    downloadedFile = getDownloadedFiles()

    for torrentFile in torrentFiles:
        for dledFile in downloadedFile:
            if dledFile.find(torrentFile['fileName']) >= 0 and dledFile.find('@Syno') == -1:
                copyFileToFolder(torrentFile, dledFile)
