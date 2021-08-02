from PIL import Image
import imagehash
from imagehash import hex_to_hash
import numpy as np
from scipy import signal
import librosa as l
from pathlib import Path
from pydub import AudioSegment


def loadPath(folderPath: str) -> tuple:
   
    basePath = Path(folderPath)
    filesInPath = (item for item in basePath.iterdir() if item.is_file())
    for item in filesInPath:
        yield (item.stem, item.relative_to(basePath.parent))
        #print (item.stem, item.relative_to(basePath.parent))


def ReadMp3(filePaths: str, fMilliSeconds: float = None) -> tuple:
  
    if fMilliSeconds:
        audioFile = AudioSegment.from_mp3(filePaths)[:fMilliSeconds]
    else:
        audioFile = AudioSegment.from_mp3(filePaths)
    data = np.array(audioFile.get_array_of_samples())
    rate = audioFile.frame_rate
    return data, rate


def mixSongs(song1: np.ndarray, song2: np.ndarray, dType: str = 'int16', w: float = 0.5) -> np.ndarray:
    
    return (w*song1 + (1.0-w)*song2).astype(dType)


def PerceptualHash(arrayData: "np.ndarray") -> str:
 
    dataInstance = Image.fromarray(arrayData)
    return imagehash.phash(dataInstance, hash_size=16).__str__()


def HashDistance(hash1: str, hash2: str) -> int:
    
    return hex_to_hash(hash1) - hex_to_hash(hash2)



def mapRanges(inputValue: float, inMin: float, inMax: float, outMin: float, outMax: float):
   
    slope = (outMax-outMin) / (inMax-inMin)
    return outMin + slope*(inputValue-inMin)

