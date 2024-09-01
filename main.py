import sys
import os
import queue
from threading import Thread, Lock
from time import sleep
from datetime import datetime
import subprocess
import psutil
import threading
from micro import Micro

from PyQt5.QtWidgets import (QApplication, QToolBar, QWidget, QGridLayout,
                             QFrame, QAction, QLabel, QComboBox, QPushButton, QCheckBox,
                             QTextEdit, QDockWidget, QTextBrowser, QLineEdit, QFileDialog,
                             QMessageBox, QWidgetAction, QProgressBar
                            )
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QTextCharFormat, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QRadioButton
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt

# Serial communication modules
import serial
import serial.tools.list_ports

# Add root directory to the user python paths
rootDir = os.getcwd()
sys.path.append(rootDir)

# Author information
AUTHOR_NAME = "Aaron Escoboza"

# Software version information
SW_VERSION = "1.0"

# Global paths
UI_PATH = rootDir + "\\index.ui"

class GuiMicroControl(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi(UI_PATH, self)
        self.micro = Micro()

        self.logQueue = queue.Queue()
        self.initWidgets()
        self.refreshPorts()

        self.show()

    def initWidgets(self):
        """ Initialize signal/slot communication and initial values """
        # GPIO I/O widgets
        self.onButton.clicked.connect(self.slotOn)
        self.offButton.clicked.connect(self.slotOff)
        self.readPinButton.clicked.connect(self.slotReadPin)

        # Combobox: GPIOs
        for gpio in self.micro.gpios:
            self.gpioSelector.addItem(gpio.upper())

        # Line: Pin numbers
        minPinNumber, maxPinNumber = self.micro.pins
        for pinNumber in range(minPinNumber, maxPinNumber + 1):
            self.pinSelector.addItem(str(pinNumber).upper())

        # General information widgets
        self.heapButton.clicked.connect(self.slotHeapButton)
        self.ticksButton.clicked.connect(self.slotTicksButton)
        self.clockButton.clicked.connect(self.slotClockButton)
        self.versionButton.clicked.connect(self.slotVersionButton)
        self.helpButton.clicked.connect(self.slotHelpButton)
        self.statusButton.clicked.connect(self.slotStatusButton)

        # RTC widgets
        self.setTimeButton.clicked.connect(self.slotSetTimeButton)
        self.getTimeButton.clicked.connect(self.slotGetTimeButton)

        # PWM widgets
        self.setFreqDutyButton.clicked.connect(self.slotFeqDutyButton)

        # Serial communication widgets
        self.portSelector.currentTextChanged.connect(self.slotPortSelectorPressed)
        self.baudrateSelector.currentTextChanged.connect(self.slotBaudrateSelectorPressed)
        self.refreshButton.clicked.connect(self.slotRefreshPorts)
        self.clearButton.clicked.connect(self.slotClean)
        self.startConnectionButton.clicked.connect(self.slotStartConnection)

        # Update combobox with supported baudrates
        for baud in self.micro.baudRates:
            self.baudrateSelector.addItem(baud)
        self.baudrateSelector.setCurrentText('115200')

        # Tool bar actions
        self.actionSave.triggered.connect(self.slotActionSave)
        self.actionSettings.triggered.connect(self.slotActionSettings)
        self.actionHelp.triggered.connect(self.slotActionSave)


    #########################################################################
    #
    #                               START - SLOTS
    #
    #########################################################################

    def slotPortSelectorPressed(self):
        """ TODO """
        pass

    def slotBaudrateSelectorPressed(self):
        """ TODO """
        pass

    def slotActionSave(self) -> None:
        """ TODO """
        pass
    def slotActionSettings(self) -> None:
        """ TODO """
        pass
    def slotActionHelp(self) -> None:
        """ TODO """
        pass

    def slotHeapButton(self) -> None:
        """ TODO """
        try:
            heap = self.micro.get_heap_info()
            if not heap:
                self.writeToLog(f'Could not read from device\n', "red")
                return
            self.writeToLog(heap)
        except Exception as e:
            self.writeToLog(f'Error: {e}\n')

    def slotTicksButton(self) -> None:
        """ TODO """
        try:
            ticks = self.micro.get_ticks()
            if not ticks:
                self.writeToLog(f'Could not read from device\n', "red")
                return
            self.writeToLog(ticks)
        except Exception as e:
            self.writeToLog(f'Error: {e}\n')

    def slotClockButton(self) -> None:
        """ TODO """
        try:
            heap = self.micro.get_heap_info()
            if not heap:
                self.writeToLog(f'Could not read from device\n', "red")
                return
            self.writeToLog(heap)
        except Exception as e:
            self.writeToLog(f'Error: {e}\n')

    def slotVersionButton(self) -> None:
        """ TODO """
        try:
            version = self.micro.get_version()
            if not version:
                self.writeToLog(f'Could not read from device\n', "red")
                return
            self.writeToLog(f'Software version:\n {version}\n')
        except Exception as e:
            self.writeToLog(f'Error: {e}\n')

    def slotHelpButton(self) -> None:
        """ TODO """
        try:
            help = self.micro.help()
            if not help:
                self.writeToLog(f'Could not read from device\n', "red")
                return
            self.writeToLog(f'{help}')
        except Exception as e:
            self.writeToLog(f'Error: {e}\n')

    def slotStatusButton(self) -> None:
        """ TODO """
        try:
            status = self.micro.get_stats()
            if not status:
                self.writeToLog(f'Could not read from device\n', "red")
                return
            self.writeToLog(f'{status}')
        except Exception as e:
            self.writeToLog(f'Error: {e}\n')

    def slotSetTimeButton(self) -> None:
        """ Slot to set a new RTC time """
        # Validate time
        hour = self.hourLineEdit.text()
        minutes = self.minLineEdit.text()
        if len(hour) < 1:
            self.showErrorMessage("Invalid hour")
            return
        if len(minutes) < 1:
            self.showErrorMessage("Invalid minutes")
            return

        try:
            response = self.micro.set_rtc_time(hour, minutes)
            self.writeToLog(f'Response:\n{response}\n')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotGetTimeButton(self) -> None:
        """ Slot to get the RTC time from the microcontroller """
        try:
            response = self.micro.get_rtc_time()
            self.writeToLog(f'Response:\n{response}\n')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotFeqDutyButton(self) -> None:
        """ Slot to set the frequency and the duty cycle """
        try:
            freq =  self.freqLineEdit.text()
            duty = self.dutyCycleLineEdit.text()
            if len(freq) < 1:
                raise Exception("Invalid frequency")
            if len(duty) < 1:
                raise Exception("Invalid duty cycle")
            response = self.micro.set_pwm_freq(int(freq), int(duty))
            self.writeToLog(f'Response:\n{response}\n')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotRefreshPorts(self):
        if len(self.ports) < 1:
            self.showErrorMessage("Error: Not valid ports found")

    def slotOn(self):
        """ Slot to turn on a pin """
        gpio = self.gpioSelector.currentText()
        pin = self.pinSelector.currentText()
        try:
            response = self.micro.gpio_write(gpio, pin, 1)
            self.writeToLog(f'Response: {response}\n')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotOff(self):
        """ Slot to off on a pin """
        gpio = self.gpioSelector.currentText()
        pin = self.pinSelector.currentText()
        try:
            response = self.micro.gpio_write(gpio, pin, 0)
            self.writeToLog(f'Response: {response}\n')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotReadPin(self):
        """ Slot to read a GPIO pin """
        gpio = self.gpioSelector.currentText()
        pin = self.pinSelector.currentText()
        try:
            response = self.micro.gpio_read(gpio, pin)
            self.writeToLog(f'Response: {response}\n')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotClean(self):
        self.log.clear()
        self.clearLogQueue()

    def slotStartConnection(self):
        """ Slot to process the connection and disconnection from the
            the serial port.
        """
        # Validate the selected port
        portDescription = self.portSelector.currentText()
        if len(portDescription) < 1:
            self.showErrorMessage("No port selected")
            return

        # Get port name based on the selected port description
        for port in self.ports:
            if port.description == portDescription:
                portName = port.name

        # Get serial port parameters from widgets
        baudrate = self.baudrateSelector.currentText()

        # Handle connection and disconnection states
        try:
            if self.micro.is_open():
                self.micro.close()
            else: # Serial device not opened
                # Open the serial port with the user

                if not self.micro.open(portName, baudrate):
                    self.writeToLog("Could not open serial port\n", "red")
                    return

                # Check if the microcontroller can response to a ping command
                response = self.micro.ping()
                if response.strip() == "ok":
                    self.writeToLog("Device connected\n", "green")
                else:
                    self.writeToLog("Device did not response\n", "red")
        except Exception as e:
            self.showErrorMessage(f'Error{e}')

    #########################################################################
    #
    #                               END - SLOTS
    #
    #########################################################################

    def writeToLog(self, text, color = 'white'):
        """ Write a text to the log dock/text widget """
        cursor = self.log.textCursor()
        cursor.movePosition(cursor.End)
        format_ = QTextCharFormat()

        format_.setForeground(QColor(color))
        cursor.insertText(text, format_)
        self.log.setTextCursor(cursor)
        self.log.ensureCursorVisible()

    def refreshPorts(self):
        self.ports = []
        self.portSelector.clear()
        tmpPorts = serial.tools.list_ports.comports()
        for port in tmpPorts:
            if "USB" in port.hwid:
                self.portSelector.addItem(port.description)
                self.ports.append(port)

    def clearLogQueue(self):
        """ Clear the queue by removing all items """
        while not self.logQueue:
            self.logQueue.get()

    def showErrorMessage(self, text):
        """ Pops up an error window  """
        # Create a message box and initialize i
        icon = QMessageBox.Icon(QMessageBox.Icon.Critical)
        messageBox = QMessageBox()
        messageBox.setIcon(icon)
        # messageBox.setWindowIcon(QIcon(self.appRootPath + self.iconPaths["mainIcon"]))
        messageBox.setWindowTitle("Error")
        messageBox.setText(text)
        messageBox.setStyleSheet("""
            QMessageBox {
                background-color: #F0F0F0; /* Light gray background */
                color: black; /* Text color */
                border: 2px solid #00BFFF; /* Border color */
            }
        """)

        # Add buttons to the message box
        messageBox.addButton(QMessageBox.Ok)

        # Show the message box
        messageBox.exec_()

def main():
    app = QApplication(sys.argv)
    instance = GuiMicroControl()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
