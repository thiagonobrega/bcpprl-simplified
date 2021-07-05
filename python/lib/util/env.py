import os

def getbase_dir(subpath):
    try:
        os.environ['WINDIR']
        # os.path.join('path','paths')
        # base_dir = 'D:\\Dados\\OneDrive\\Doutorado\\workspace\\bc-playground\\'+subpath+'\\'
        base_dir = 'D:\\Dados\\OneDrive\\Doutorado\\workspace\\bc-playground\\'
    except KeyError:
        # base_dir = '/home/thiagonobrega/workspace/bc-playground/'+subpath+'/'
        base_dir = '/home/thiagonobrega/workspace/bc-playground/'

    if (type(subpath) == str):
        return os.path.join(base_dir, subpath) + os.sep

    for p in subpath:
        base_dir = os.path.join(base_dir,p)

    return base_dir + os.sep