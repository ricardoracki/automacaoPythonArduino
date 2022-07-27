from enum import Enum
from time import sleep
from typing import Callable
import serial
from PyQt5.QtCore import QThread
from threading import Thread


class Comm_Events(Enum):
    CONNECTED = "CONNECTED"
    READ = "READ"
    WRITING = "WRITING"
    COMMUNICATION_ERROR = "COMMUNICATION_ERROR"
    READ_ERROR = "READ_ERROR"
    CLOSING_CONNECTION = "CLOSING_CONNECTION"
    CONNECTION_CLOSED = "CONNECTION_CLOSED"


class Communication(serial.Serial):
    def __init__(self, port="COM5", baudrate=9600, timeout=0.2, dispatch: Callable=None, *args, **kwargs):
        self._dispatch = dispatch
        self.connected = False
 
        
        try:
            super().__init__(port, baudrate, timeout=timeout)
            self._dispatch(Comm_Events.CONNECTED)
            self.connected = True
            # self.th = QThread()
            self.th = Thread(target=self._read_loop)
            # self.th.started.connect(self._read_loop)
            self.th.start()
            
        except Exception as e:
            self._dispatch(Comm_Events.COMMUNICATION_ERROR, e)
    
    def write(self, command: str) -> None:
        self._dispatch(Comm_Events.WRITING, command)
        super().write(command.encode())
        
    def _read_loop(self) -> None:
        while self.connected:
            try: 
                self.read_from_port()
            except:
                print("Error in read")
        sleep(0.1)
        
    def read_from_port(self) -> None:
        try:
            read = super().readline().decode()
            if read != "":
                self._dispatch(Comm_Events.READ, read)

        except Exception as e:
            self._dispatch(Comm_Events.READ_ERROR, e)
            
    def end(self) -> None:
        self._dispatch(Comm_Events.CLOSING_CONNECTION)
        try:
            super().close()
            self.connected = False
            self._dispatch(Comm_Events.CLOSING_CONNECTION)
        except Exception as e:
            self._dispatch(Comm_Events.COMMUNICATION_ERROR, e)
