import PySimpleGUI as sg
import serial
import time
from SerialSender import SerialSender


# convert "12300" to "1234" (123 * 10e4)



class StimProgramWindow:
    width = 500
    height = 500
    programOrder = []
    window = None

    # def __init__(self, keys):

    def open(self):
        text = ""
        try:
            file = open('program.txt', 'r')
            text = file.read()
            file.close()
        except FileNotFoundError:
            pass


        self.layout = [

            [sg.Button("reset", key="-RESET-")],
            [sg.Checkbox(key=f'CHECKBOX{15 - i}', text=f'{15 - i}') for i in range(16)],
            [sg.Text("#of bursts: "),
             sg.Input(key="-CHANNELBURSTNUMBER-", size=(10, 1), default_text='1'), sg.Text(expand_x=True),
             sg.Button(button_text="+", key="-CHANNELINDEXADD-")],
            [sg.Text("CH\tN\tV\tA\tB\tC\tD", font=("Comic Sans MS", 15))],
            [
                sg.Multiline(key="PROGRAMCODE", expand_x=True, expand_y=True, default_text=text, font=("Comic Sans MS", 15))
            ],
            [sg.Button(button_text="Set program", key="-SETSTIMPROGRAM-"), sg.Button(button_text="\U0001f4be", font=('Arial', 16), key="SAVEPROGRAM")]
        ]

        self.window = sg.Window("Stimwindow", layout=self.layout)
        self.window.Finalize()
        self.window.set_min_size((self.width, self.height))

    def setProgram(self, serialSender: SerialSender):
        if len(self.programOrder) > 30:
            raise Exception("Program too long!")


        for index, i in enumerate(self.programOrder):

            serialSender.send('add channel', index, i)
            serialSender.send('AWIDTH', int(i[3]), index)
            serialSender.send('BWIDTH', int(i[4]), index)
            serialSender.send('CWIDTH', int(i[5]), index)
            serialSender.send('DWIDTH', int(i[6]), index)
            time.sleep(0.1)

        serialSender.send('valid channels', len(self.programOrder))

    def addToProgram(self, burst: str, values: dict):

        if not burst.isdigit():
            sg.popup("Wrong format!", keep_on_top=True, no_titlebar=True, grab_anywhere=True)
        else:

            sum = 0
            for i in range(16):
                sum += pow(2, i) * values[f'CHECKBOX{i}']

            channelsToOpen = '0x' + '{:0>2}'.format(hex(bytes([sum >> 8])[0])[2:]) + '{:0>2}'.format(hex(bytes([sum & 0xff])[0])[2:])
            self.window['PROGRAMCODE'].update(channelsToOpen + ' ' + burst + ' 127\n', append=True)

    def removeFromProgram(self, index):
        self.programOrder.pop(index)

    def resetProgram(self):
        self.programOrder.clear()

    def getDataFromText(self, text: str):

        self.programOrder.clear()
        text = text.split('\n')
        for i in text:
            if i[:2] == "//":
                continue
            i = i.split('\t')

            if len(i) < 7:
                raise IndexError(f'Wrong format')
            self.programOrder.append((i[0], i[1], i[2], i[3], i[4], i[5], i[6]))

    def close(self):
        self.window.close()
