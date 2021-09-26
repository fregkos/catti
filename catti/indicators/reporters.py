import json
from catti.IO.general import checkCreateFolder, makeFilePath, printLineInsideBox


def signalsReport(securityName, signals, verbose):
    if verbose:
        print('[i] Generating signals report for '+ securityName)
    
    # Initialize reports dictionary.
    reports = {}

    for indicator in signals:
        # Find the percentage of buy and sell signals.
        values = signals[indicator].value_counts()
        # Count the number of signals.
        totalSignals = int(values.sum())
    
        # Try to grab the correct & false signals % if there are any
        # There is no chance for division by zero, since finding a signal,
        # means that totalSignals is > 0.
        try:
            buySignals = values.loc['buy'] / totalSignals
        except KeyError:
            buySignals = 0.0
        
        try:
            sellSignals = values.loc['sell'] / totalSignals
        except KeyError:
            sellSignals = 0.0
        
        # Find the ratio of the generated signals over the total days.
        signalToDaysRatio = totalSignals/len(signals)
            
        if verbose:
            print('[i] Indicator '+ signals[indicator].name)
            print('[.] Total Signals: {:.2f} %'.format(totalSignals * 100))
            print('[.] Buy Signals: {:.2f} %'.format(buySignals * 100))
            print('[.] Sell Signals: {:.2f} %'.format(sellSignals * 100))
            print('[.] Signals to Days Ratio: {:.2f}'.format(signalToDaysRatio))
        
        report = {
            'totalSignals': totalSignals,
            'buySignals': buySignals,
            'sellSignals': sellSignals,
            'SDR': signalToDaysRatio
        }

        # Add each individual indicator's report to the dictionary.
        reports[signals[indicator].name] = report

    # Finally, include the total days we have in for our security.
    reports['totalDays'] = len(signals)

    # Save the results to a JSON file...
    checkCreateFolder('signals report')

    with open(makeFilePath('signals report', securityName, 'json'), 'w') as f:
        if verbose:
            print('[+] Saving report for ' + securityName)
        json.dump(reports, f, indent=1)

    # Remove the total days before you return the reports.
    # They are used to aggregate results per chunk, we don't need that data.
    reports.pop('totalDays')
    return reports

def validatedSignalsReport(securityName, validatedSignals, verbose=False):
    if verbose:
        print('[i] Generating validated signals report for '+ securityName)
    
    # Initialize reports dictionary.
    reports = {}

    for indicator in validatedSignals:
        # Find the percentage of True and False signals.
        values = validatedSignals[indicator].value_counts()
        # Count the number of signals.
        totalSignals = int(values.sum())
    
        # Try to grab the correct & false signals % if there are any
        # There is no chance for division by zero, since finding a signal,
        # means that totalSignals is > 0.
        try:
            correctSignals = values.loc[True] / totalSignals
        except KeyError:
            correctSignals = 0.0
        
        try:
            wrongSignals = values.loc[False] / totalSignals
        except KeyError:
            wrongSignals = 0.0
        
        # Find the ratio of the generated signals over the total days.
        signalToDaysRatio = totalSignals/len(validatedSignals)
            
        if verbose:
            print('[i] Indicator '+ validatedSignals[indicator].name)
            print('[.] Total Signals: {:.2f} %'.format(totalSignals * 100))
            print('[.] Correct Signals: {:.2f} %'.format(correctSignals * 100))
            print('[.] Wrong Signals: {:.2f} %'.format(wrongSignals * 100))
            print('[.] Signals to Days Ratio: {:.2f}'.format(signalToDaysRatio))
        
        report = {
            'totalSignals': totalSignals,
            'correctSignals': correctSignals,
            'wrongSignals': wrongSignals,
            'SDR': signalToDaysRatio
        }

        # Add each individual indicator's report to the dictionary.
        reports[validatedSignals[indicator].name] = report

    # Finally, include the total days we have in for our security.    
    reports['totalDays'] = len(validatedSignals)

    # Save the results to a JSON file...
    checkCreateFolder('validated signals report')

    with open(makeFilePath('validated signals report', securityName, 'json'), 'w') as f:
        if verbose:
            print('[+] Saving report for ' + securityName)
        json.dump(reports, f, indent=1)

    # Remove the total days before you return the reports.
    # They are used to aggregate results per chunk, we don't need that data.
    reports.pop('totalDays')
    return reports