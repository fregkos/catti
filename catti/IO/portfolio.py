from datetime import date
from catti.IO.general import emptyTheFolder, skip, splitter, saveChunkParallel
from catti.IO.selectors import requestYesNo
import json
import os
import getpass
import yfinance as yf


def savePortfolio(portfolio, filename='portfolio.json'):
    portfolioData = {key: portfolio[key] for key in ['owner', 'securities', 'lastDates', 'creationDate']}

    with open(filename, 'w') as f:
        json.dump(portfolioData, f)

    print('[i] Portfolio information saved.')

# CAREFUL: This list is initialized and the same memory address will be used for subsequent calls
def createPortfolio(tickers=[]):
    # In case security tickers are given as a parameter, we won't ask the user for them.
    if not tickers:
        print('[i] Data is downloaded from yahoo finance. Check your ticker names from there.')
        tickers = input('[>] Give your tickers separated with comma (,): ').upper().split(',')
        if tickers == '':
            tickers = []

    portfolio = {
        'owner': getpass.getuser(),
        'securities': tickers,
        'lastDates': ['1970-12-31', str(date.today())], # Default date values in case they are omitted.
        'creationDate': str(date.today())
    }

    savePortfolio(portfolio)

    if requestYesNo('Do you want to download historical data now?'):
        downloadHistoricalData()

def loadPortfolioInfo(filename='portfolio.json', verbose=False):
    if verbose:
        print('[i] Loading portfolio info...')
    
    if not os.path.isfile(filename):
        print('[X] ERROR: Portfolio not found. Create a portfolio first!')
        createPortfolio()

    with open(filename, 'r') as f:
        portfolio = json.load(f)
    
    return portfolio

def downloadHistoricalData(filename='portfolio.json', skipDownloaded=True):
    portfolio = loadPortfolioInfo(filename)

    print("[i] Give start and end dates separated by comma in YYYY-MM-DD format.")
    print("[.] For example: 1970-12-31," + str(date.today()))
    print("[.] If omitted, the example dates will be used. Hit [ENTER] to skip.")
    
    startDate, endDate = portfolio['lastDates']
    dates = input('[>] Dates: ').split(',')

    if not dates[0] == '':
        startDate = dates[0]
        endDate = dates[1]

    # Update portfolio date values.
    portfolio['lastDates'] = [startDate, endDate]
    savePortfolio(portfolio)

    # Don't delete all historical data if user wants to resume downloads.
    if not skipDownloaded:
        emptyTheFolder('historical')

    dataDownloader(portfolio['securities'], startDate, endDate, True, 3)

    return portfolio

def dataDownloader(tickers, startDate, endDate, skipDownloaded=True, savePercentage=1):
    print('[i] Downloading historical data...')
    print('[+] Saving to disk for every {}% of progress'.format(savePercentage))
    size = len(tickers)
    chunkSize = int(size * savePercentage/100)
    
    chunks = splitter(tickers, chunkSize)
    for chunk in chunks:
        if skipDownloaded:
            chunk = skip('historical', chunk, False)
            
            # If all items from chunk are skipped, continue.
            if not chunk:
                continue

        data = yf.download(chunk, start=startDate, end=endDate, group_by='ticker')
        saveChunkParallel('historical', data, chunk, True)

        print("[i] Total download progress: {:.2f}%".format(len(chunk)/size * 100))

