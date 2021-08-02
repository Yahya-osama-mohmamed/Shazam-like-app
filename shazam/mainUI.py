import UI3 as ui
from PyQt5 import QtWidgets, QtGui
import logging
from functools import partial
from Spectrogram import spectrogram
from Functions import mixSongs, PerceptualHash, HashDistance, mapRanges, ReadMp3
from updateDB import readJson

class voiceRecognizer(ui.Ui_MainWindow):
    
    def __init__(self, starterWindow: QtWidgets.QMainWindow):
        # Initializer
        super(voiceRecognizer, self).setupUi(starterWindow)
        self.spectroHashKey = "spectrohash"  # Key used to get the spectrogram Hash
        self.featureKey = "features"  # key used to get mel Hash
        self.audFiles = [None, None]  # List Containing both songs
        self.audRates = [None, None]  # List contains Songs Rates which must be equal
        self.lineEdits = [self.aud1Text, self.aud2Text]
        self.testHash = None  #  Mix output  hash
        self.audMix = None  #  Mix output  Audio File
        self.featureMixHash = []  # Holds the features extracted from Mix
        self.results = []  # Holds the Results with each song
        self.songsPath = "task-songs/"  # path to songs directory
        self.dbPath = "hasheddb.json"  # path to database directory
        self.spectrogram = spectrogram()._spectrogram  # Spectrogram Extraction function
        self.extractFeatures = spectrogram().spectralFeatures  # Feature Extraction function
        self.loadBtns = [self.audLoad1, self.audLoad2]  # loading buttons collected
        self.logger = logging.getLogger()  
        self.logger.setLevel(logging.DEBUG)
        #self.ratioSlider.valueChanged.connect(self._CallMixer)

        # CONNECTIONS
        for btn in self.loadBtns:
            btn.clicked.connect(partial(self.loadFile, btn.property("indx")))

        self.finderBtn.clicked.connect(self._CallMixer)

        self.resultsTable.hide()
        self.label_2.hide()



    def loadFile(self, indx):
       
        self.statusbar.showMessage("Loading Audio File %s"%indx)
        audFile, audFormat = QtWidgets.QFileDialog.getOpenFileName(None, "Load Audio File %s"%(indx),
                                                                                 filter="*.mp3")
        self.logger.debug("Audio File %s Loaded"%indx)

        # CHECK CONDITIONS
        if audFile == "":
            self.logger.debug("loading cancelled")
            self.statusbar.showMessage("Loading cancelled")
            pass
        else:
            self.logger.debug("starting extraction of data")
            audData, audRate = ReadMp3(audFile, 60000)
            self.logger.debug("extraction successful")
            self.audFiles[indx-1] = audData
            self.audRates[indx-1] = audRate
            self.lineEdits[indx-1].setText(audFile.split('/')[-1])
            self.statusbar.showMessage("Loading Done")
            self.logger.debug("Loading done")

    def _CallMixer(self):
     
        print("Slider Value is %s"%self.ratioSlider.value())
        self.statusbar.showMessage("Finding Matches ...")
        self.logger.debug("starting searching process")

        if (self.audFiles[0] is not None) and (self.audFiles[1] is not None):
            self.logger.debug("loaded two different songs ")
            self.audMix = mixSongs(self.audFiles[0], self.audFiles[1], w=self.ratioSlider.value()/100)

        else:
            self.logger.debug("loaded only one song")
            if self.audFiles[0] is not None : self.audMix = self.audFiles[0]
            if self.audFiles[1] is not None: self.audMix = self.audFiles[1]
            if self.audFiles[0] is None and self.audFiles[1] is None:
                self.showMessage("Warning", "You need to at least load one Audio File",
                                 QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Warning)

        if self.audMix is not None:
            self.logger.debug("starting Extraction")

            self.spectro = self.spectrogram(self.audMix, self.audRates[0])[-1]
            self.testHash = PerceptualHash(self.spectro)

            for feature in self.extractFeatures(self.audMix, self.spectro, self.audRates[0]):
                self.featureMixHash.append(PerceptualHash(feature))

            self.HashCompare()
        self.statusbar.clearMessage()

    def HashCompare(self):
       
        self.logger.debug("comparing hashes ... ")
        self.statusbar.showMessage("Loading results .. ")

        for songName, songHashes in readJson(self.dbPath):
            self.spectroDiff = HashDistance(songHashes[self.spectroHashKey], self.testHash)
            self.featureDiff = 0

            for i, feature in enumerate(songHashes[self.featureKey]):
                self.featureDiff += HashDistance(feature, self.featureMixHash[i])

            self.avg = (self.spectroDiff + self.featureDiff)/4
            self.results.append((songName, (abs(1 - mapRanges(self.avg, 0, 255, 0, 1)))*100))
            

        self.results.sort(key= lambda x: x[1], reverse=True)
        #print(self.results)

        self.statusbar.clearMessage()

        self.TableConfig()

    def TableConfig(self):
   
        self.label_2.show()
        self.resultsTable.setColumnCount(2)
        self.resultsTable.setRowCount(len(self.results))

        for row in range(len(self.results)):
            self.resultsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(self.results[row][0]))
            self.resultsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(str(round(self.results[row][1], 2))+"%"))
            self.resultsTable.item(row, 0).setBackground(QtGui.QColor(255, 255, 255))
            self.resultsTable.item(row, 1).setBackground(QtGui.QColor(255, 255,255))
            self.resultsTable.verticalHeader().setSectionResizeMode(row, QtWidgets.QHeaderView.Stretch)

        self.resultsTable.setHorizontalHeaderLabels(["Found Matches", "Percentage"])

        for col in range(2):
            self.resultsTable.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            self.resultsTable.horizontalHeaderItem(col).setBackground(QtGui.QColor(255, 255,255))

        self.resultsTable.show()

        self.results.clear()

    def showMessage(self, header, message, button, icon):
        
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(header)
        msg.setText(message)
        msg.setIcon(icon)
        msg.setStandardButtons(button)
        self.logger.debug("messege shown with %s %s "%(header, message))
        msg.exec_()

if __name__ == '__main__':
    import sys
    logging.basicConfig(filename="logs/logfile.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = voiceRecognizer(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
