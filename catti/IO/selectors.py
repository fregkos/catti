from math import floor


def selectTickers(portfolio):
    print('Choose some tickers or leave blank to select all.')
    print('Available tickers:')

    for i, ticker in enumerate(portfolio['securities'], start=1):
        print('{}) {}'.format(i, ticker), end='\t')
    print()
    print('Give the ticker index(es), separted by comma.')
    print('For example: 2,3,6')
    print("If omitted, all portfolio tickers will be selected. Hit [ENTER] to skip.")
    tickerIndexes = input('Select a ticker(s): ').split(',')


    if not '' in tickerIndexes:
        tickerIndexes = list(map(int, tickerIndexes))
        tickers = [portfolio['securities'][ticker - 1] for ticker in tickerIndexes]
    else:
        tickers = portfolio['securities']

    return tickers

def selectPeriods():
    print('Give the window periods in days, separted by comma.')
    print('For example: 5,10,20,50,100,200\n')
    print('Of course, you can add only one period if you wish.')
    print('For example, if you want a rolling window of 30 days, just type: 30')
    print("If omitted, the example periods will be used. Hit [ENTER] to skip.")
    periods = input('Periods: ').split(',')
    
    if '' in periods:
        periods=[5, 10, 20, 50, 100, 200]
    
    periods = list(map(int, periods))

    return periods

def genericSelection(items):
    print('[i] Make a selection.')
    print('[.] Available:')
    for i, item in enumerate(items, start=1):
        print('{}) {}'.format(i, item), end='\t')
    selection = input('\n[>] Your choice: ')

    return items[int(selection)-1]

def requestNumber(context, warnInt=False):
    print('[i] Give the number of {}.'.format(context))
    number = input('[>] Number: ')

    # In case we are demanding for an integer.
    if warnInt:
        print('[!] WARNING: An integer must be given. Proceeding with ' + str(int(number)))
        return int(number)

    # For example if the number given is 1,
    # then 1.0 == float(1) or 1.0 == 1.0,
    # so we return the integer 1
    # Otherwise, if 1.5 is given,
    # then 1.5 == float(1) or 1.5 == 1.0,
    # which is false, so we return the float 1.5
    if float(number) == float(floor(float(number))):
        return int(number)

    return float(number)

def requestYesNo(question):
    # Print the question
    print('[?] {}'.format(question))
    
    # Validity check
    answer = ''
    while answer != 'y' and answer != 'n':
        answer = str(input('[>] Yes/No: '))
        print()

        # If user just presses enter, do nothing about it.
        if not answer:
            continue

        # We care about the first letter y/n
        answer = answer.lower()[0]
    
    return answer == 'y'