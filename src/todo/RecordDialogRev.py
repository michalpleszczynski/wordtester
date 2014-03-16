from __future__ import division

import pyaudio
import wave
import sys
import time

from PyQt4.QtCore import SIGNAL, QThread, QString
from PyQt4.QtGui import QDialog, QApplication, QAction

import ui_RecordDialog

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 60

RECORDING = False
PLAYING = False

class RecordDialog(QDialog, ui_RecordDialog.Ui_RecordDialog):
    def __init__(self, parent = None):
        super(RecordDialog, self).__init__(parent)
        self.setupUi(self)

        self.threads = []
        self.fname = 'test.wav'
        self.recordNStopButton.setText("Record")
        self.timeLabel.setText("00:00")

        recordAction = self.createAction("Start or stop recording", self.record, "SPACE")
        playAction = self.createAction("Play/Stop", self.play, "CTRL+P")
        self.addActions((recordAction,playAction))

        self.connect(self.recordNStopButton, SIGNAL("clicked()"), self.record)
        self.connect(self.playButton, SIGNAL("clicked()"), self.play)

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

    def record(self):
        global PLAYING
        global RECORDING
        if PLAYING:
            return
        if not RECORDING:
            self.playButton.setEnabled(False)
            self.threads.append(RecordThread(self.fname))
            self.threads.append(TimerThread())
            self.connect(self.threads[-1], SIGNAL("updateTime(QString)"), self.timeLabel.setText)
            RECORDING = True
            self.recordNStopButton.setText("Stop recording..")
            self.threads[-2].start()
            self.threads[-1].start()
        else:
            RECORDING = False
            self.playButton.setEnabled(True)
            self.recordNStopButton.setText("Record")

    def getLengthOfWav(self):
        wf = wave.open(self.fname,'rb')
        length = wf.getnframes()/wf.getframerate()
        wf.close()
        return length

    def play(self):
        global PLAYING
        global RECORDING
        if RECORDING:
            return
        if not PLAYING:
            lengthOfWav = self.getLengthOfWav()
            self.recordNStopButton.setEnabled(False)
            self.threads.append(PlayThread(self.fname))
            self.connect(self.threads[-1],SIGNAL("finished"),self.finished)
            self.threads.append(TimerThread(lengthOfWav))
            self.connect(self.threads[-1], SIGNAL("updateTime(QString)"), self.timeLabel.setText)
            PLAYING = True
            self.playButton.setText("Playing..")
            self.threads[-2].start()
            self.threads[-1].start()
        else:
            PLAYING = False
            self.playButton.setText("Play")
            self.recordNStopButton.setEnabled(True)

    def finished(self):
        global PLAYING
        PLAYING = False
        self.playButton.setText("Play")
        self.recordNStopButton.setEnabled(True)

class RecordThread(QThread):
    def __init__(self, fname, parent = None):
        super(RecordThread, self).__init__(parent)

        self.all = []
        self.p = pyaudio.PyAudio()
        self.fname = fname

    def run(self):
        self.record()
        self.writeToWave()
        return

    def __del__(self):
        self.wait()

    def record(self):
        stream = self.p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = CHUNK)

        self.all = []
        for i in range(0, RATE // CHUNK * RECORD_SECONDS):
            data = stream.read(CHUNK)
            self.all.append(data)
            global RECORDING
            if not RECORDING:
                break

        stream.close()
        self.p.terminate()

    def writeToWave(self):
        data = ''.join(self.all)
        wf = wave.open(self.fname, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()

class PlayThread(QThread):
    def __init__(self, fname, parent = None):
        super(PlayThread, self).__init__(parent)

        self.fname = fname

    def run(self):
        self.play()
        self.emit(SIGNAL("finished"))
        return

    def __del__(self):
        self.wait()

    def play(self):
        wf = wave.open(self.fname, 'rb')

        p = pyaudio.PyAudio()

        # open stream
        stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)        

        # read data
        data = wf.readframes(CHUNK)

        # play stream
        while data != '':
            stream.write(data)
            data = wf.readframes(CHUNK)
            global PLAYING
            if not PLAYING:
                break

        stream.close()
        p.terminate()
        wf.close()


class TimerThread(QThread):
    def __init__(self, maxTime = None, parent = None):
        super(TimerThread, self).__init__(parent)

        self.maxTime = maxTime

    def run(self):
        global RECORDING
        global PLAYING
        startTime = time.time()
        while RECORDING or PLAYING:
            time.sleep(0.1)
            if self.maxTime is None:
                self.emit(SIGNAL("updateTime(QString)"),QString("Time: %.1f" % (time.time() - startTime)))
            else:
                self.emit(SIGNAL("updateTime(QString)"),QString("Time: %(is).1f/%(max).1f" \
                % {'is':(time.time() - startTime), 'max':self.maxTime}))

    def __del__(self):
        self.wait()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = RecordDialog()
    form.show()
    app.exec_()