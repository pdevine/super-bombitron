import os.path

def dataName(fileName):
    if os.path.exists(os.path.join('data', fileName)):
        return os.path.join('data', fileName)
    elif os.path.exists(os.path.join('../data', fileName)):
        return os.path.join('../data', fileName)
    else:
        return fileName

