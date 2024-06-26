import PySimpleGUI as sg
import serial
import time
from SerialSender import SerialSender


# convert "12300" to "1234" (123 * 10e4)



class TimingProgramWindow:
    width = 500
    height = 500
    programOrder = []
    window = None

    # def __init__(self, keys):

    def open(self):
        self.layout = [

            [sg.Button("reset", key="-TIMINGRESET-")],
            [
                sg.Multiline(key="TIMINGPROGRAMCODE", expand_x=True, expand_y=True)
            ],
            [sg.Button(button_text="Set timing program", key="-TIMINGPROGRAM-")]
        ]

        self.window = sg.Window("Timingwindow", layout=self.layout)
        self.window.Finalize()
        self.window.set_min_size((self.width, self.height))

    def setProgram(self, serialSender: SerialSender):
        if len(self.programOrder) > 100:
            raise Exception("Program too long!")


        for index, i in enumerate(self.programOrder):

            serialSender.send('AWIDTH', int(i[0]), index)
            serialSender.send('BWIDTH', int(i[1]), index)
            serialSender.send('CWIDTH', int(i[2]), index)
            serialSender.send('DWIDTH', int(i[3]), index)
            time.sleep(0.1)

        serialSender.send('valid timing steps', len(self.programOrder))

    def getDataFromText(self, text: str):

        self.programOrder.clear()
        text = text.split('\n')
        for i in text:
            i = i.split(' ')

            self.programOrder.append((i[0], i[1], i[2], i[3]))

    def resetProgram(self):
        self.programOrder.clear()

    def close(self):
        self.window.close()
