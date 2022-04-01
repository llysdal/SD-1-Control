import os, wave, struct
curDir = os.path.dirname(os.path.abspath(__file__))[0:-4]

def getRessourcePath(name):
    return curDir+'/Ressource/' + name

def getConfig():
    try:
        file = open(curDir+'/config.ini', 'r')
        data = file.read()
        file.close()

        dataSplit = data.split('\n')

        config = {}
        for configuration in dataSplit:
            if configuration[0] == '#': continue
            splitPoint = configuration.index('=')
            if len(configuration) == splitPoint+1:
                config[configuration[0:splitPoint]] = None
            else:
                config[configuration[0:splitPoint]] = configuration[splitPoint+1:]

        return True, config
    except:
        print('Config file not found / wrong format - using defaults')
        return False, {}