from Functions import *
from Spectrogram import spectrogram

import json

def updateDB(filePath:str, fileOut:str, mode: str = "a"):
    """
    Responsible for creating the database from a folder given.

    ============= ==========================================
    **Arguments**
    filePath      A string path to the input file with the database songs.
    fileOut       A string path to the output directory to save the json file.
    mode          String used to write in json file.
    ============= ==========================================
    """
    d = {}

    for audFile, path in loadPath(filePath):
        data, rate = ReadMp3(path, 60000)
        _, _, mesh = spectrogram()._spectrogram(data, rate)

        feats = spectrogram().spectralFeatures(data, mesh, rate)
        features = []
        spectrohash = PerceptualHash(mesh)
        for feature in feats :
            features.append(PerceptualHash(feature))

        d.update({audFile: {"spectrohash": spectrohash, "features": features}})
        print("%s is hashed" % audFile)

    with open(fileOut+"db.json", mode) as outfile:
        json.dump(d, outfile, indent=4)


def readJson(file):
    """
    Reads a specified json file and return its contents.

    """
    
    with open(file) as jsonFile:
        data = json.load(jsonFile)
    for song in data:
        yield song, data[song]


if __name__ == '__main__':
    import sys
    import warnings

    warnings.filterwarnings("ignore")
    updateDB(r'C:\Users\yehia\Downloads\Voice-Recognition-App-master\task-songs',r'C:\Users\yehia\Downloads\Voice-Recognition-App-master\hashed',"w")
    
    '''
    if sys.argv[1] and sys.argv[2]:
        updateDB(sys.argv[1], sys.argv[2], "w")
    else:
        for i in readJson("db.json"):
            print(i)
            print("File paths not given")

    print("End of Script")
    '''
