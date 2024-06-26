import pyvisa
import pandas

rm = pyvisa.ResourceManager()
lrc = rm.open_resource('USB0::0x0957::0x0909::MY54201800::0::INSTR')
lrc.timeout = 6000
#setupCommands = ':SOUR:DCS:STAT OFF;:BIAS:STAT OFF;:COMP:BIN:COUN:CLE;:LIST:CLE:ALL;:COMP:BIN:CLE;:AMPL:ALC OFF;:APER MED,1;:BIAS:POL:AUTO OFF;:BIAS:RANG:AUTO ON;:BIAS:VOLT:LEV 0;:COMP:ABIN OFF;:COMP:BIN:COUN:STAT OFF;:COMP:MODE PTOL;:COMP:SLIM -9.9e+37,9.9e+37;:COMP:STAT OFF;:COMP:SWAP OFF;:COMP:TOL:NOM 0;:DISP:ENAB ON;:DISP:LINE "";:DISP:WIND:TEXT1:DATA:FMSD:DATA 1e-09;:DISP:WIND:TEXT2:DATA:FMSD:DATA 1e-09;:FORM:ASC:LONG OFF;:FORM:BORD NORM;:FORM:DATA ASC,64;:FREQ:CW 1000;:FUNC:DCR:RANG:VAL 100;:FUNC:DEV1:MODE OFF;:FUNC:DEV1:REF:VAL 0;:FUNC:DEV2:MODE OFF;:FUNC:DEV2:REF:VAL 0;:FUNC:IMP:RANG:VAL 100000;:FUNC:IMP:TYPE ZTD;:FUNC:SMON:IDC:STAT OFF;:FUNC:SMON:VDC:STAT OFF;:INIT:CONT OFF;:LIST:MODE SEQ;:LIST:STIM:TYPE FREQ,NONE;:OUTP:DC:ISOL:LEV:VAL 2e-05;:OUTP:DC:ISOL:STAT OFF;:SOUR:DCS:VOLT:LEV 0;:TRIG:DEL 0;:TRIG:SOUR INT;:TRIG:TDEL 0;:VOLT:LEV 1;:DISP:WIND:TEXT1:DATA:FMSD:STAT OFF;:DISP:WIND:TEXT2:DATA:FMSD:STAT OFF;:FUNC:DCR:RANG:AUTO ON;:FUNC:IMP:RANG:AUTO ON;:OUTP:DC:ISOL:LEV:AUTO ON;:LIST:STIM:DATA 20,100,200,500,1000,2000,5000,10000,20000,50000;:DISP:PAGE LSETup;'
#lrc.write(setupCommands)
freqs = [20, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
setupCommands = f':SOUR:DCS:STAT OFF;:BIAS:STAT OFF;:COMP:BIN:COUN:CLE;:LIST:CLE:ALL;:COMP:BIN:CLE;:AMPL:ALC OFF;:APER MED,1;:BIAS:POL:AUTO OFF;:BIAS:RANG:AUTO ON;:BIAS:VOLT:LEV 0;:COMP:ABIN OFF;:COMP:BIN:COUN:STAT OFF;:COMP:MODE PTOL;:COMP:SLIM -9.9e+37,9.9e+37;:COMP:STAT OFF;:COMP:SWAP OFF;:COMP:TOL:NOM 0;:DISP:ENAB ON;:DISP:LINE "";:DISP:WIND:TEXT1:DATA:FMSD:DATA 1e-09;:DISP:WIND:TEXT2:DATA:FMSD:DATA 1e-09;:FORM:ASC:LONG OFF;:FORM:BORD NORM;:FORM:DATA ASC,64;:FREQ:CW 20;:FUNC:DCR:RANG:VAL 100;:FUNC:DEV1:MODE OFF;:FUNC:DEV1:REF:VAL 0;:FUNC:DEV2:MODE OFF;:FUNC:DEV2:REF:VAL 0;:FUNC:IMP:RANG:VAL 300;:FUNC:IMP:TYPE ZTD;:FUNC:SMON:IDC:STAT OFF;:FUNC:SMON:VDC:STAT OFF;:INIT:CONT ON;:LIST:MODE SEQ;:LIST:STIM:TYPE FREQ,NONE;:OUTP:DC:ISOL:LEV:VAL 0.02;:OUTP:DC:ISOL:STAT OFF;:SOUR:DCS:VOLT:LEV 0;:TRIG:DEL 0;:TRIG:SOUR INT;:TRIG:TDEL 0;:VOLT:LEV 1;:DISP:WIND:TEXT1:DATA:FMSD:STAT OFF;:DISP:WIND:TEXT2:DATA:FMSD:STAT OFF;:FUNC:DCR:RANG:AUTO ON;:FUNC:IMP:RANG:AUTO ON;:OUTP:DC:ISOL:LEV:AUTO ON;:LIST:STIM:DATA {str(freqs)[1:-1].replace(' ', '')};:DISP:PAGE LIST;\n'
lrc.write(setupCommands)

df = pandas.DataFrame()

results = []

freqsDict = {}

for index, f in enumerate(freqs):
    freqsDict[2*index] = f'Z@{f}'
    freqsDict[2*index + 1] = f'θ@{f}'

saveFilename = input('Enter the saveFilename: ')

titles = {}


for j in range(0, 100):
    try:
        message = input('Enter measurement title: ')
        if message == 'stop':
            break

        titles[j] = message
        data = lrc.query(":FETCH?")
        print(data)

        data = data.split(",")
        tmpData = []
        for index, i in enumerate(data):
            #for some reason the data returned has two zeros after every measurement, so we need to skip those
            if index % 4 >= 2:
                continue
            tmpData.append(i)

        # tmp = ['-' for i in tmpData]
        # tmp.append(message)
        # results.append(tmp)
        results.append(tmpData)

    except pyvisa.errors.VisaIOError as e:
        lrc.timeout += 500
        print('Error, increasing timeout...')


df = pandas.DataFrame(results)
df = df.rename(columns=freqsDict)
df = df.rename(index=titles)
df.to_excel(f'measurements/{saveFilename}.xlsx')
