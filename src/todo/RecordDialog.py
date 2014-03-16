import pyaudio
import wave
import sys
import time

from PyQt4.QtCore import SIGNAL, QThread
from PyQt4.QtGui import QAction, QDialog, QApplication

import ui_RecordDialog

SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


class RecordThread(QThread):
    def __init__(self, fname, parent = None):
        super(RecordThread, self).__init__(parent)
        self.stopped = False
        self.recordDevice = pyaudio.PyAudio()
        self.recordStream = None
        self.all = []
        self.fname = fname
        self.connect(self, SIGNAL("stopRecording"), self.stopRecording)

    def record(self):
        self.recordStream = self.recordDevice.open(format = FORMAT, channels = CHANNELS, \
                            rate = RATE, input = True, frames_per_buffer = SIZE)
        print "recording"
        while not self.stopped:
            try:
                data = self.recordStream.read(SIZE)
            except IOError as e:
                print 'stracona ramka, chyba'
            self.all.append(data)
        print "done recording"

    def stopRecording(self):
        self.stopped = True
        self.recordStream.close()
        self.recordDevice.terminate()
        print 'stopped'
        self.dataToWave()

    def run(self):
        self.record()

    def __del__(self):
        self.wait()

    def dataToWave(self):
        data = ''.join(self.all)
        if self.fname is not None:
            wf = wave.open(str(self.fname), 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.recordDevice.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(data)
            wf.close()
        print 'plik: ' + self.fname


class TimeItThread(QThread):
    def __init__(self, label, parent = None):
        super(TimeItThread, self).__init__(parent)
        self.timeLabel = label
        self.startTime = None
        self.stopped = False

    def run(self):
        print 'measuring time'
        self.startTime = time.time()
        while not self.stopped:
            self.emit(SIGNAL("updateTime(QString)"),"Time: %.2f" % (time.time() - self.startTime))
            
    def __del__(self):
        self.wait()

    def stop(self):
        self.stopped = True

class PlayWave(QThread):
    def __init__(self, fname, parent = None):
        super(PlayWave, self).__init__(parent)
        self.fname = str(fname)
        self.stopped = False
        self.playDevice = pyaudio.PyAudio()
        self.wf = None
        self.stream = None


    def run(self):
        self.wf = wave.open(self.fname, 'rb')
        self.stream = self.playDevice.open(format =
                                        self.playDevice.get_format_from_width(self.wf.getsampwidth()),
                                        channels = self.wf.getnchannels(),
                                        rate = self.wf.getframerate(),
                                        output = True)

        data = self.wf.readframes(SIZE)

        while data != '' and not self.stopped:
            self.stream.write(data)
            data = self.wf.readframes(SIZE)
        self.stop()

    def stop(self):
        self.stopped = True
        self.stream.close()
        self.playDevice.terminate()

class RecordDialog(QDialog, ui_RecordDialog.Ui_RecordDialog):
    def __init__(self, parent = None):
        super(RecordDialog, self).__init__(parent)
        self.setupUi(self)

        self.fname = "test.wav"
        self.recording = False
        self.waveData = None
        self.playing = False
        self.threads = []

        self.recordNStopButton.setText("Record")
        self.timeLabel.setText("Time: 00.00")
        
        startEndRecordingAction = self.createAction("Start or end recording", self.recordNStopButton.toggle, "CTRL+R")
        self.addAction(startEndRecordingAction)

        self.connect(self.recordNStopButton, SIGNAL("toggled(bool)"),
                    self.changeRecordingState)
        self.connect(self.playButton, SIGNAL("toggled(bool)"),
                    self.changePlayingState)


    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def updateTime(self, text):
        self.timeLabel.setText(text)

    def changeRecordingState(self, toggled = None):
        print 'changeState'
        self.recording = not self.recording
        if self.recording:
            self.playButton.setEnabled(False)
            self.recordNStopButton.setText("Stop recording..")
            self.threads.append(RecordThread(self.fname))
            self.threads[-1].start()
            self.threads.append(TimeItThread(self.timeLabel))
            self.disconnect(self, SIGNAL("updateTime(QString)"), self.updateTime)
            self.connect(self, SIGNAL("updateTime(QString)"), self.updateTime)
            self.threads[-1].start()
        else:
            self.recordNStopButton.setText("Record")
            self.emit(SIGNAL("stopRecording"))
            self.threads = []
            self.playButton.setEnabled(True)
            print 'koniec nagrywania'

    def changePlayingState(self, toggled = None):
        print 'playing'
        self.playing = not self.playing
        if self.playing:
            self.recordNStopButton.setEnabled(False)
            self.playButton.setText("Pause..")
            self.threads.append(PlayWave(self.fname))
            self.threads[-1].start()
            self.threads.append(TimeItThread(self.timeLabel))
            self.disconnect(self, SIGNAL("updateTime(QString)"), self.updateTime)
            self.connect(self, SIGNAL("updateTime(QString)"), self.updateTime)
            sefl.threads[-1].start()
        else:
            self.playButton.setText("Play")
            self.recordNStopButton.setEnabled(True)
            self.threads = []
            print 'koniec grania'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = RecordDialog()
    form.show()
    app.exec_()
