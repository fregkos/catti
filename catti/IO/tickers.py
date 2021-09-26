import shutil
import urllib.request as request
from contextlib import closing

def tickerDownloader(filename):
   print("[i] Fetching tickers from ftp.nasdaqtrader.com server...")
   with closing(request.urlopen('ftp://ftp.nasdaqtrader.com/SymbolDirectory/{}'.format(filename))) as r:
      with open('filename', 'wb') as f:
         shutil.copyfileobj(r, f)

def tickerParser(file):
   lines = []
   tickers = []

   with open(file, 'r') as f:
      lines = f.readlines()
   
   header = lines[0].split('|')
   testIssuePosition = header.index('Test Issue')

   # Ignoring header and footer
   for line in lines[1:-1]:
      splittedLine = line.split('|')
      ticker = splittedLine[0]

      isTestIssue = True if splittedLine[testIssuePosition] == 'Y' else False
      
      # We will only keep a ticker that is not used for testing
      if not isTestIssue:
         ticker = ticker.replace('$','-P')
         ticker = ticker.replace('.W','-WT')
         ticker = ticker.replace('.U','-UN')
         tickers.append(ticker)

   return tickers

def tickers(exchange):
   if exchange.lower() == 'nasdaq':
      tickerDownloader('nasdaqlisted.txt')
      return tickerParser('nasdaqlisted.txt')
   elif exchange.lower() == 'nyse' or exchange.lower() == 'amex':
      tickerDownloader('otherlisted.txt')
      return tickerParser('otherlisted.txt')
   else:
      tickerDownloader('nasdaqlisted.txt')
      tickerDownloader('otherlisted.txt')
      return tickerParser('nasdaqlisted.txt') + tickerParser('otherlisted.txt')