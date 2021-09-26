from catti.IO.selectors import requestNumber, requestYesNo
from catti.indicators.parallelCalculator import calculate
from catti.IO.portfolio import createPortfolio, downloadHistoricalData, loadPortfolioInfo
from catti.IO.tickers import tickers


def printMenu(title, status, owner):
    print("""

        ┌{}┐
        ├─────────────────────────────────────────────────────────────────────────┤
        ├{}┤
        ├─────────────────────────────────────────────────────────────────────────┤
        │        0) Exit                                                          │
        │                                                                         │
        │ ─ Make a NEW or OPEN a saved portfolio                                  │
        │        1) Create a Portfolio                                            │
        │        2) Load a Portfolio                                              │
        │                                                                         │
        │ ─ Tickers                                                               │
        │        3) Create a NASDAQ Portfolio                                     │
        │        4) Create a NYSE American (formerly AMEX) Portfolio              │
        │        5) Combine the above                                             │
        │                                                                         │
        │ ─ Download CSV data for your portfolio securities                       │
        │        6) Download historical data                                      │
        │                                                                         │
        │ ─ Indicators                                                            │
        │        7) Calculate all indicators for all securities                   │
        │                                                                         │
        │ ─ Find buy/sell signals                                                 │
        │        8) Calculate all signals for all securities                      │
        │                                                                         │
        │ ─ Validate signals' prediction                                          │
        │        9) Validate all signals for all securities                       │
        │            for the n-th day in the future                               │
        │                                                                         │        
        │ ─ Generate reports all securities' signals                              │
        │       10) Generate reports for buy & signals percentages                │
        │       11) Generate reports for correct & wrong signals percentages      │
        │                                                                         │
        │ ─ Pipeline for the credibility process                                  │
        │       12) Calculate all indicators, their signals,                      │
        │            validate them and generate their reports                     │
        │                                                                         │
        ├─────────────────────────────────────────────────────────────────────────┤
        └{}┘
    """.format(title.center(73,'─'), status.center(73,'─'), owner.center(73,'─'))
    )

#        │                                                                         │
#        │ ─ Lorem ipsum                                                           │
#        │        X) Lorem ipsum                                                   │

def menu(settings):
    title = 'Credibility Analysis Toolkit for Technical Indicators'
    #title = "Prediction & Validation of Technical Indicators' Signals"
    portfolio = {}
    owner = ''

    # Checking and loading settings...
    if settings['autoLoad']:
        portfolio = loadPortfolioInfo()
        owner = '┤ ' + portfolio['owner'] + ' ├'
    
    # Updating status...
    if 'securities' in portfolio:
        numOfSecurities = len(portfolio['securities'])
        if numOfSecurities == 0:
            status = 'Portfolio has no securities yet. Recreate it!'
        else:
            status = 'Got {} securities, ranged from  {}  to  {}'.format(numOfSecurities,
                                                                            portfolio['lastDates'][0],
                                                                            portfolio['lastDates'][1])
    else:
        status = 'Portfolio not loaded yet. Maybe you should create it!'

    status = '┤ ' + status + ' ├'

    # Printing the actual menu
    printMenu(title, status, owner)

    # Handling given options
    totalOptions = 12
    while True:
        option = int(input('[>] Select an option: '))
        if (option > totalOptions or option < 0):
            print('[X] ERROR: Invalid option!')
            continue

        if option == 0:
            break
        elif option == 1:
            createPortfolio()
        elif option == 2:
            portfolio = loadPortfolioInfo()
        elif option == 3:
            createPortfolio(tickers('nasdaq'))
        elif option == 4:
            createPortfolio(tickers('nyse'))
        elif option == 5:
            createPortfolio(tickers())
        elif option == 6:
            # Portfolio is reloaded after update.
            portfolio = downloadHistoricalData()
        elif option == 7:
            percentage = requestNumber('securities to include per chunk (on a 0%-100% scale)')
            calculate('indicators', percentage)
        elif option == 8:
            percentage = requestNumber('securities to include per chunk (on a 0%-100% scale)')
            calculate('signals', percentage)
        elif option == 9:
            days = requestNumber('days after a signal', warnInt=True)
            percentage = requestNumber('securities to include per chunk (on a 0%-100% scale)')
            calculate('validated signals', percentage, extraArgs=days)
        elif option == 10:
            percentage = requestNumber('securities to include per chunk (on a 0%-100% scale)')
            calculate('signals report', percentage)
        elif option == 11:
            percentage = requestNumber('securities to include per chunk (on a 0%-100% scale)')
            calculate('validated signals report', percentage)
        elif option == 12:
            pipeline = ['indicators', 'signals', 'validated signals', 'signals report', 'validated signals report']
            pipelineCopy = pipeline.copy()

            if requestYesNo('Do you want to skip any step?'):
                for task in pipelineCopy:
                    if requestYesNo('Skip calculating {}?'.format(task)):
                        pipeline.remove(task)

            days = 1
            # if any('validated' in task for task in pipeline):
                # days = requestNumber('days after a signal', warnInt=True)
            
            print('[!] The final pipeline looks like this:')
            print('[i] [' + '] -> ['.join(pipeline) + ']\n')
            
            if requestYesNo('Continue?'):
                percentage = requestNumber('securities to include per chunk (on a 0%-100% scale)')
                for task in pipeline:
                    calculate(task, percentage, extraArgs=days)

        # Printing the actual menu
        printMenu(title, status, owner)
