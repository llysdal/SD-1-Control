midi = __import__('midi')
from time import time


def delay(delayTime = 0.1):
    t = time()
    while time() < t+delayTime:
        pass

def chooseDevices(devices, config):
    #Input
    valid = False
    #Check if config tells us the device
    configInput = config.get('defaultMidiInput', None)
    if configInput is not None:
        for device in list(devices[0].keys()):
            if device.find(configInput) is not -1:
                i = devices[0][device]
                print('Default input device \'' + device + '\' found')
                valid = True
                break
        else:
            print('Default input device \'' + configInput + '\' not found')

    #Obtain manually
    while not valid:
        for acc in range(len(devices[0])):
            print(str(list(devices[0].values())[acc]) + ' - ' + list(devices[0].keys())[acc])
        try:
            i = int(input('Input> '))
        except:
            print('Invalid ID\n')
            continue

        if midi.getDeviceInfo(i)[2]:
            valid = True
            print()
            break
        print('Invalid ID\n')

    #Output
    valid = False
    #Check if config tells us the device
    configOutput = config.get('defaultMidiOutput', None)
    if configOutput is not None:
        for device in list(devices[1].keys()):
            if device.find(configOutput) is not -1:
                o = devices[1][device]
                print('Default output device \'' + device + '\' found')
                valid = True
                break
        else:
            print('Default output device \'' + configOutput + '\' not found')

    while not valid:
        print()
        for acc in range(len(devices[1])):
            print(str(list(devices[1].values())[acc]) + ' - ' + list(devices[1].keys())[acc])
        try:
            o = int(input('Output> '))
        except:
            print('Invalid ID')
            continue

        if midi.getDeviceInfo(o)[3]:
            valid = True
            print()
            break
        print('Invalid ID')
        
    print()

    return i, o
