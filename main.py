import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
from PyQt5.QtCore import QTimer
from threading import Thread

from design import *
from communication import Comm_Events, Communication
from recognition import listen


class Interface(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        
        self.recognition_thread = Thread(target=self._recognition_loop)
        
        self._comm = Communication(dispatch=self._dispatch_event)
        self.progress_state = 0
        
        self._state = {
            "red": False,
            "green": False,
            "yellow": False
        }
        
        self._colors = {
            "red_True": "rgb(255, 94, 97)",
            "green_True": "rgb(142, 255, 124)",
            "yellow_True": "rgb(255, 241, 131)",
            "red_False": "red",
            "green_False": "green",
            "yello_False": "yellow"
        }
        
        self.button_green.clicked.connect(lambda: self.handle_button_click(self.button_green))
        self.button_yellow.clicked.connect(lambda: self.handle_button_click(self.button_yellow))
        self.button_red.clicked.connect(lambda: self.handle_button_click(self.button_red))
        
        self.quitButton.clicked.connect(self.quit)
        
        self.checkBox.clicked.connect(self.recognition_thread.start)
        
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.progressBar.setValue(self.progress_state))
        self.timer.setInterval(100)
        self.timer.start()
        
    def handle_button_click(self, btn: QPushButton) -> None:
        color = btn.objectName().split("_")[1]
        self._state[color] = not self._state[color]
        bg_color = self._colors.get(f"{color}_{self._state[color]}", "orange")
        btn.setStyleSheet(f"{btn.styleSheet()} background-color: {bg_color};")
        
        self._comm.write(f"led_{color}:{self._state[color]}".lower())
        
    def _dispatch_event(self, event_type: str, event_message: str|dict|Exception= None) -> None:
        """ Disparador de eventos da comunicação com Arduino """
        if event_type == Comm_Events.CONNECTED:
            self.status_message.setText("Conectado")
            
        elif event_type == Comm_Events.COMMUNICATION_ERROR:
            self.status_message.setText("Erro de conxão")
            print(event_message)
            
        elif event_type == Comm_Events.READ:
            try:
                sinal = int(event_message)
                self.progress_state = round(((1024 - sinal) / 1024) * 100)
            except Exception as e:
                print(e)
            
        elif event_type == Comm_Events.READ_ERROR:
            print('Read_Error', event_message)
        
    def _recognition_loop(self):
        while self.checkBox.isChecked():
            print("listen...")
            text = listen()

            if text is not None:
                text = text.lower()
                target = ""
                val = ""
                if "vermelho" in text or "vermelha" in text:
                    target = "led_red"
                elif "amarelo" in text or "amarela" in text:
                    target = 'led_yellow'
                elif "verde" in text:
                    target = 'led_green'
                    
                if "ligar" in text or "liga" in text or "acende" in text or "acenda" in text or "ligue" in text:
                    val = ":true"
                    
                if "desligar" in text or "desliga" in text or "apague" in text or "desligue" in text:
                    val = ":false"
                    
                print(text)
                if target != "" and val != "":
                    print(target+val)
                    self._comm.write(target+val)
            
    def quit(self) -> None:
        self._comm.end()
        self.checkBox.setChecked(False)
        quit()
    
    def closeEvent(self, event) -> None:
        self.quit()
        event.accept()


if __name__ == '__main__':
    qt = QApplication(sys.argv)
    interface = Interface()
    interface.show()
    qt.exec_()