from scipy import signal
import json
import librosa as l
from numpy import ndarray

class spectrogram():
    """
    Responsible for creating spectrograms for any .wav file
    implements the following:
    - reads a loaded wav file data and creates the associated spectrum
    - save the spectrum created in an arbitrary file
    """
    def __init__(self):
      
        self.sampleFreqs = None
        self.sampleTime = None
        self.colorMesh = None
        self.features = None
        self.container = None
    
    def _spectrogram(self, songData: ndarray, songSampleRate:int=22050, windowType: str="hann")->tuple:
       
        if len(songData.shape) == 2:
            print("song is stereo")
            print("Converting ..")
            self.sampleFreqs, self.sampleTime, self.colorMesh = signal.spectrogram(songData[:, 0],
                                                                                   fs=songSampleRate, window=windowType)
        else:
            self.sampleFreqs, self.sampleTime, self.colorMesh = signal.spectrogram(songData,
                                                                                   fs=songSampleRate, window=windowType)
        return (self.sampleFreqs, self.sampleTime, self.colorMesh)
   
    def spectralFeatures(self, song: "ndarray"= None, S: "ndarray" = None, sr: int = 22050, window:'str'='hann'):
       
        return (l.feature.melspectrogram(y=song, S=S, sr=sr, window=window),
                l.feature.mfcc(y=song.astype('float64'), sr=sr),
                l.feature.chroma_stft(y= song, S=S, sr=sr, window=window))

if __name__ == '__main__':
    

    from scipy.io import wavfile
    sampleRate, songdata = wavfile.read("tests/Adele_Million_Years_Ago_10.wav")
    spectrum = spectrogram()
    spectrum(songdata, sampleRate,"hann", featureize=True)
    



