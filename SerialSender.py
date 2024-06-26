import typing

import serial
import PySimpleGUI as sg
import asyncio

from BLE import sendBLE


# def parseInput(inputString: str, allowZero: bool = True) -> str:
#     if not inputString.isdigit() or len(inputString) > 12 or (int(inputString) == 0 and allowZero):
#         return ""
#
#     inputString = str(int(inputString))
#
#     if len(inputString) <= 3:
#         return "0" * (3 - len(inputString)) + inputString + "0"
#     result = inputString[0:3] + str(len(inputString) - 3)
#     return result


class SerialSender:
    RX_SIZE = 8
    client = None
    characteristic = None

    def __init__(self):
        self.ser = serial.Serial()

    def connect(self, port):
        try:
            self.ser.close()
            self.ser = serial.Serial(port, baudrate=115200, timeout=0.2)
            return port
        except serial.SerialException:
            sg.popup("No device connected", keep_on_top=True, no_titlebar=True, grab_anywhere=True)
            return None


    # parses command based on programCode, does not pad the command to be RX_SIZE in length
    def parseCommand(self, programCode: str, *args) -> bytes:

        match programCode:
            case 'system reset':
                return bytes([0x00])

            case  'stop stimulation':
                return bytes([0x01])

            case 'stimulate once':
                return bytes([0x02])

            case 'stimulate continuously':
                return bytes([0x02, 0xff])

            case 'intensity':
                value = args[0][0]
                return bytes([0x13, int(value)])

            case 'add channel':
                index = args[0][0]
                channelData = args[0][1] # 0 - channel ID, 1 - number of bursts, 2 - intensity
                intensityValue = int(int(channelData[2]) * 0x0fff / 127.0)
                print(bytes([0x0e, index, (intensityValue & 0xffff) >> 8, intensityValue & 0xff, (int(channelData[0], 16) >> 8) & 0xff, int(channelData[0], 16) & 0xff, int(channelData[1])]))
                return bytes([0x0e, index, (intensityValue & 0xffff) >> 8, intensityValue & 0xff, (int(channelData[0], 16) >> 8) & 0xff, int(channelData[0], 16) & 0xff, int(channelData[1])])

            case 'valid channels':

                return bytes([0x0f, args[0][0]])

            case 'command line instruction':

                data = args[0][0].split(' ')


                for index, i in enumerate(data):
                    if 'x' in i and i[0] == '0':
                        data[index] = int(data[index], 16)
                    elif i.isdigit():
                        data[index] = int(data)
                    else:
                        raise ValueError('invalid data')

                    if data[index] > 255 or data[index] < 0:
                        raise ValueError('invalid data')

                return bytes(data)

            case 'AWIDTH': #some of these are meant to be 16 bit values
                value = int(args[0][0])
                value = round(80 * value / 132) #adjust from miliseconds to clock cycles

                index = int(args[0][1])
                return bytes([0x05, (value & 0xffff) >> 8, value & 0xff, index])

            case 'BWIDTH':
                value = int(args[0][0])
                index = int(args[0][1])
                return bytes([0x06, (value & 0xffff) >> 8, value & 0xff, index])

            case 'CWIDTH':
                value = int(args[0][0])
                value = round(80 * value / 132)

                index = int(args[0][1])

                return bytes([0x07, (value & 0xffff) >> 8, value & 0xff, index])

            case 'DWIDTH':
                value = int(args[0][0])
                value = round(value / 2) # divide by two because control bits also take time
                index = int(args[0][1])
                return bytes([0x08, (value & 0xffff) >> 8, value & 0xff, index])

            case 'NBURST':
                value = int(args[0][0])
                print(value)
                return bytes([0x09, (value & 0xffff) >> 8, value & 0xff])

            case 'PAUSETIME':

                value = round(int(args[0][0]) / int(args[0][1]))

                return bytes([0x0b, (value & 0xffff) >> 8, value & 0xff])

            case "PWM":
                value = int(args[0][0])
                if value >= 100 or value < 0:
                    raise ValueError('Value must be between 0 and 100')

                return bytes([0x0c, value & 0xff])

            case "valid timing steps":
                value = int(args[0][0])

                return bytes([0x14, (value & 0xffff) >> 8, value & 0xff])

            case _:
                    raise NameError('not implemented')




    def send(self, command, *data) -> None:

        try:
            command = self.parseCommand(command, data)
        except ValueError:
            sg.popup("could not send: invalid data", keep_on_top=True, no_titlebar=True, grab_anywhere=True)
            return
        except NameError:
            sg.popup("could not send: not implemented", keep_on_top=True, no_titlebar=True, grab_anywhere=True)
            return

        #pad command with zeros until it is RX_SIZE - 1
        command = bytes(list(command) + [0x0] * (self.RX_SIZE - len(command) - 1))

        if len(command) > self.RX_SIZE - 1:
            raise Exception('command length exceeds max length')

        try:
            #if command[0] == 6:
            #     self.ser.write(self.appendCRC(command))
            # self.ser.write(self.appendCRC(command))

                # commandArray = [0x69]
            # commandArray += list(command)
            # commandArray = bytes(commandArray)
            asyncio.run(sendBLE(self.client, self.appendCRC(command), self.characteristic))
            print(self.appendCRC(command))

            print('command length: ', len(self.appendCRC(command)))
        except serial.SerialException:
            sg.popup("could not send: serial error", keep_on_top=True, no_titlebar=True, grab_anywhere=True)

        print("done")



    def appendCRC(self, data: bytes) -> bytes:

        data = list(data)
        crc = sum(data) % 256
        data.append(crc)
        return bytes(data)


    def readAll(self):
        try:
            result = self.ser.readall()
        except serial.SerialException:
            sg.popup("could not read")
            return 'could not read'
        return result

