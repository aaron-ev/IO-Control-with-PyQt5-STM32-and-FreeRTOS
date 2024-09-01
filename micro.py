"""
    Author: Aaron Escoboza
    Github: https://github.com/aaron-ev
    File name: micro.py
    Description: Classes to abstract a microcontroller and access to
                 it's main capabilities.
"""

from serial import Serial
import serial.tools.list_ports

class Micro():
    """ Class to control a microcontroller via a serial device """
    baudRates = ['1200','2400','4800','9600','38400', '115200', '230400']
    channels = ['1', '2', '3', '4']
    gpios  = ['a','b','c','d','e','h']
    pins = (0, 15)
    commands = {
            'heap':"heap\n",
            'clk':"clk\n",
            'ticks':"ticks\n",
            'version':"version\n",
            'stats': "stats\n",
            'help': "help\n",
            'stats': "stats\n",
            'gpioWrite': "gpio-w",
            'gpioRead': "gpio-r",
            'rtcSet': "rtc-s",
            'rtcGet': "rtc-g\n",
            'pwmSetFreq': "pwm-f",
            'pwmSetDuty': "pwm-d",
            'pwmMonitor': "pwmMonitor",
            'ping': "ping\n",
            }
    maxFreq =  10000 # In Hz
    maxDutyCycle = 100 # (0 - 100)%

    def __init__(self):
        self.readTerminationCondition = '<'
        self.dev = None
        self.isOpen = False

    def _write(self, command: str = "version") -> str:
        """ Write to the serial device interface
            Parameters:
            command: Any command in commands attribute
        """
        print(f'Command:\n{command}\n')
        try:
            self.dev.write(command.encode())
            return self._read()
        except Exception as e:
            self._print(f'Error: {e}')
        return ''

    def _read(self, timeout: int = 1) -> str:
        """ Write to the serial device interface
            Parameters:
            timeout: Read timeout, it will block until timeout has reached or
            termination condition is read.
        """
        self.dev.timeout = timeout
        dataRead = b''
        response = b''
        while True:
            dataRead = self.dev.read()
            if dataRead == '': # Could not read within the timeout
                self._print(f'Could not read with timeout: {timeout}\n')
                break
            if dataRead.decode() == self.readTerminationCondition:
                break
            response += dataRead
        return response.decode()

    def _print(self, text: str) -> str:
        print(f'MICRO: {text}')

    def get_version(self) -> str:
        """ Get SW version """
        return self._write(self.commands['version'])

    def gpio_write(self, gpio: str, pin: int, state: bool) -> str:
        """ Write a logical value to a GPIO pin
            Parameters:
            gpio: GPIO peripheral
            pin: Pin to read
            Return value: ok in case of positive response, no_ok otherwise
        """
        command = self.commands['gpioWrite'] + f' {gpio.lower()} {pin} {state}\n'
        return self._write(command)

    def gpio_read(self, gpio: str, pin: int) -> str:
        """ Read a GPIO pin
            Parameters:
            gpio: GPIO peripheral
            pin: Pin to read
            Return value: Pin state
        """
        command = self.commands['gpioRead'] + f' {gpio.lower()} {pin}\n'
        return self._write(command)

    def help(self) -> str:
        """ Reads any help information """
        return self._write(self.commands['help'])

    def get_statistics(self) -> str:
        """ Reads any help information """
        return self._write(self.commands['stats'])

    def get_ticks(self) -> str:
        """ Get the OS tick counter number """
        return self._write(self.commands['ticks'])

    def get_heap_info(self) -> str:
        """ Get OS heap consumption """
        return self._write(self.commands['heap'])

    def get_clk_info(self) -> str:
        """ Get microcontroller CLK information """
        return self._write(self.commands['clk'])

    def get_stats(self) -> str:
        """ Get microcontroller general information """
        return self._write(self.commands['stats'])

    def open(self, port: str, baudrate: int = 9600, dataLen: int = 8,
             parity: str = 'N', stopBits: int = 1) -> bool:
        """ Open a serial port """
        if parity.lower() == "odd":
            parity = 'O'
        elif parity.lower() == "even":
            parity = 'E'
        else:
            parity = 'N'

        try:
            self.dev = serial.Serial(port,
                                         baudrate = baudrate,
                                         bytesize = dataLen,
                                         parity = parity,
                                         stopbits = stopBits,
                                         timeout = 1
                                        )
            return True
        except Exception as e:
            print(f'Exception {e}\n')
        return False

    def close(self) -> None:
        self.dev.close()

    def is_open(self) -> bool:
        """ Check if a serial communication is opened """
        return self.isOpen

    def get_rtc_time(self) -> str:
        """ Get microcontroller RTC time """
        return self._write(self.commands['rtcGet'])

    def set_rtc_time(self, hour: int, minutes: int, seconds: int = 0)  -> str:
        """ Set a new RTC time
            Parameters:
            hour: New hour
            minutes: New minutes
            seconds: New seconds
        """
        command = self.commands['rtcSet'] + f' {hour} {minutes} {seconds}\n'
        return self._write(command)

    def set_pwm_freq(self, freq: int, duty: int) -> str:
        """ Set a new PWM frequency and duty cycle
            Parameters:
            freq: Desired frequency
            duty: Desired duty cycle
        """
        if (freq < 0 or freq > self.maxFreq):
            raise Exception(f'Invalid frequency, valid range 1 - {self.maxFreq}')
        if (duty < 0 or duty > self.maxDutyCycle):
            raise Exception(f'Invalid duty cycle, valid range 1 - {self.maxDutyCycle}')

        # Frequency and duty cycle are written in two consecutive
        command = self.commands['pwmSetFreq'] + f' {freq}\n'
        response = self._write(command)
        command = self.commands['pwmSetDuty'] + f' {duty}\n'
        response += self._write(command)
        return response

    def ping(self) -> str:
        """ Ping the microcontroller
            Response: Ok in case of positive response
        """
        command = self.commands['ping']
        return self._write(command)
