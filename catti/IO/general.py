from pandas import read_csv
from multiprocessing import Pool, cpu_count
from itertools import repeat
import tqdm
import os
import datetime


# Initializing core folders.
currentWorkingDirectory = os.getcwd()
folders = {
    'historical': os.path.join(currentWorkingDirectory, 'historical_data'),
    'indicators': os.path.join(currentWorkingDirectory, 'indicator_data'),
    'signals': os.path.join(currentWorkingDirectory, 'indicator_signals'),
    'validated signals': os.path.join(currentWorkingDirectory, 'validated_signals'),
    'signals report': os.path.join(currentWorkingDirectory, 'signals_report'),
    'validated signals report': os.path.join(currentWorkingDirectory, 'validated_signals_report'),
}

# reportFolders = {
#     'signals report': os.path.join(folders['signals report'], 'indicators'),
#     'validated signals report': os.path.join(folders['validated signals report'], 'indicators'),
# }

def makeFilePath(folder, file, suffix='csv'):
    # Windows file system limitation workaround.
    # PRN is reserved.
    # https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file

    if file == 'PRN':
        print("[!] WARNING: PRN is an invalid name for NTFS. Handling as PRN_." + suffix)
        return os.path.join(folders[folder], file + '_.' + suffix)
    else:
        return os.path.join(folders[folder], file + '.' + suffix)

def portfolioExists(portfolio='portfolio.json'):
    return os.path.isfile(portfolio)

def fileExists(folder, file):
    return os.path.isfile(makeFilePath(folder, file))

def folderExist(folder, subfolder=''):
    if subfolder != '':
        path = os.path.join(folders[folder], subfolder)
    else:
        path = folders[folder]
    return os.path.isdir(path)

def hasData(folder, subfolder=''):
    # Check if target folder exists and has data inside,
    # in other words if it's not empty.

    if subfolder != '':
        path = os.path.join(folders[folder], subfolder)
    else:
        path = folders[folder]

    if folderExist(folder, subfolder):
        if os.listdir(path) != None:
            return True
    print('[X] ERROR: No {} data found!'.format(folder))
    return False

def checkCreateFolder(folder, subfolder=''):
    
    path = folders[folder]
    if subfolder != '':
        path = os.path.join(folders[folder], subfolder)
    
    # Path must be valid first.
    if not folderExist(folder, subfolder):
        print('[!] The {} data folder did not exist. Creating at...'.format(folder))
        os.mkdir(path)
        print(path)

def checkCreateSubFolder(parentFolder, folder):
    # Path must be valid first.
    subFolder = os.path.join(folders[parentFolder], folder)
    if not folderExist(subFolder):
        print('[!] The {} data subfolder did not exist. Creating at...'.format(subFolder))
        os.mkdir(subFolder)
        print(subFolder)

def emptyTheFolder(folder):
    if hasData(folder):

        for security in os.listdir(folders[folder]):

            f = os.path.join(folders[folder], security)
            if os.path.isfile(f):
                os.remove(f)
        
        os.rmdir(folders[folder])
        os.mkdir(folders[folder])

def dataSaver(target, security, name, verbose=False):
    if verbose:
        print("[+] Saving {} for {}".format(target, name))

    checkCreateFolder(target)
    security.to_csv(makeFilePath(target, name))

def dataLoader(target, security, minDays=2, startDate='2010', verbose=False):
    try:
        securityPath = makeFilePath(target, security)
        
        # Sets as index the dates and tries to parse them as datetime format,
        # but using infer_datetime_format is faster.
        data = read_csv(securityPath, index_col='Date', parse_dates=True, infer_datetime_format=True)
        data = data[startDate:]

        # We exclude data that don't meet the minimum requirements.
        if data.shape[0] >= minDays and data.index[0].year == int(startDate):
            return security, data
        else:
            if verbose:
                print("[-] Skipping {}, because days < {}".format(security, minDays))
            return '', '' # dirty hack, explained below
    except:
        if verbose:
            print('[X] Failed to load: ' + security)
            if fileExists(target, security):
                print('[i] File exists at {}'.format(securityPath))
            else:
                print('[!] File DOES NOT exist at {}'.format(securityPath))

        # Dirty hack for invalid data. We return "" for both key and data.
        # He handle that later on the loader that called this.
        # We simply have to pop that one if such data exist.
        # Multiple occurrences of invalid data are irrelevant,
        # because we use the same key (given that we update a dictionary). 
        return '', ''
    # finally:
    #     print('[+] {}'.format(security))

def saveChunkParallel(target, data, chunk, verbose=False):
    # The zip object is a generator, we want to have
    # the target and the data as a constant and the chunk as an iterator.
    iterable = zip(repeat(target), repeat(data), chunk)
    if verbose:
        iterable = tqdm.tqdm(iterable, desc='[i] Saving {} data'.format(target), unit='files')

    with Pool(processes=cpu_count()) as pool:
        pool.starmap(dataSaver, iterable, chunksize=1)

def loadChunkParallel(target, chunk, verbose=False):
    # The zip object is a generator, we want to have
    # the target as a constant and the chunk as an iterator.
    iterable = zip(repeat(target), chunk)
    if verbose:
        iterable = tqdm.tqdm(iterable, desc='[i] Loading {} data'.format(target), unit='files', total=len(chunk))

    # This has to be instancieted before assigning keys to add data.
    data = {}

    checkCreateFolder(target)

    if hasData(target):
        with Pool(processes=cpu_count()) as pool:
            data.update(pool.starmap(dataLoader, iterable, chunksize=1))

    # Invalid data is returned as "" for both key and data,
    # thus we pop that one if such data exist.
    try:
        data.pop("")
    except:
        pass

    return data

def skip(target, securities, verbose=False):
    # The data to be skipped must have the target folder specified.
    if not target in folders:
        print('[!] Target not specified. Skipping nothing!')
        return securities

    # Initializing a set of securities that we will skip.
    toBeRemoved = set()
    print('[i] Skipping already calculated {}...'.format(target))

    for security in securities:
        if fileExists(target, security):
            if verbose:
                print('[-] Skipping ' + security)
            toBeRemoved.add(security)
    
    # We return a list without the existent securities.
    return list(set(securities).difference(toBeRemoved))

def splitter(aList, chunkSize):
    # Initialize the current chunk and it's position.
    currentChunk = 0
    chunk = aList[:chunkSize]

    # While the are not on the end of the list...
    while chunk:
        # Yield a chunk
        yield chunk

        # Increment the position.
        currentChunk += chunkSize
        # Designate the next chunk.
        chunk = aList[currentChunk : currentChunk + chunkSize]

def printLineInsideBox(text):
    print('┌' + '─' * len(text) + '┐')
    print('│' + text + '│')
    print('└' + '─' * len(text) + '┘')