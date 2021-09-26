import json
from multiprocessing import Pool, cpu_count
from catti.IO.portfolio import loadPortfolioInfo
from catti.IO.general import *
from catti.indicators.calculations import indicatorsCalculator
from catti.indicators.signals import signalsCalculator
from catti.indicators.signalsValidation import signalsValidator
from catti.indicators.reporters import signalsReport, validatedSignalsReport
import tqdm


def calculate(target, chunkPercentage=2, skipCalculated=True, extraArgs=1, verbose=False):
    # Each target has its own way of processing the data.
    functionSelection = {
        'indicators': indicatorsCalculator,
        'signals': signalsCalculator,
        'validated signals': signalsValidator,
        'signals report': signalsReport,
        'validated signals report': validatedSignalsReport
    }
    selectedFunction = functionSelection[target]

    # We load portfolio info, to grab the securities' ticker names.
    portfolio = loadPortfolioInfo()
    securitiesToCalculate = portfolio['securities']

    # We skip already calculated target data if requested.
    if skipCalculated:
        securitiesToCalculate = skip(target, portfolio['securities'], True)
    
    # The new size of all the tickers after skipping calculated.
    size = len(securitiesToCalculate)
    # A percentage of the total data to be calculated per chunk.
    chunkSize = int(size * chunkPercentage/100)

    # If the chunkPercentage is relatively too small, the chunkSize becomes zero.
    # In that case, the user basically wants to calculate 1 security at a time,
    # which is actually futile. Nevertheless, we need to avoid 0.
    if chunkSize == 0:
        chunkSize = 1

    print('Calculating at most {} securites per chunk, which is ~{}% of the total ({})'.format(chunkSize, chunkPercentage, size))

    # We create a list of lists that consists of the chunks.
    chunks = splitter(securitiesToCalculate, chunkSize)
    # We need the number of splits to track the progress.
    splits = size // chunkSize

    # Initialize the results of all the chunks, to generate reports later.
    chunkResults = []

    for chunk in tqdm.tqdm(chunks, desc='Chunk completion', total=splits):

        # For each chunk, we load whatever is required and
        # we pass the arguments to the corresponding function.
        args = parameters(target, chunk, extraArgs)

        # The chunksize=1 parameter, basically gives 1 security to work on per thread.
        # This is intented because the calculations are already intensive. Feel free to tweak.
        with Pool(processes=cpu_count()) as pool:
            if 'report' in target:
                results = pool.starmap(selectedFunction, tqdm.tqdm(args, desc='Calculating {}'.format(target)), chunksize=1)
                chunkResults.extend(results)
            else:
                pool.starmap(selectedFunction, tqdm.tqdm(args, desc='Calculating {}'.format(target)), chunksize=1)

        
    # Aggregate results of indicators' data for whole portfolio.
    if 'report' in target:
        manageReports(target, chunkResults, verbose)
            


def parameters(target, chunk, extraArgs, verbose=False):
    # Each target we calculate depends on other data to be calculated.
    targetRequirement = {
        'indicators': 'historical',
        'signals': 'indicators',
        'validated signals': 'signals',
        'signals report': 'signals',
        'validated signals report': 'validated signals'
    }
    requiredTarget = targetRequirement[target]
    
    # NOTE: Cyclomatic complexity: HIGH.

    # We either want to generate reports...
    if 'report' in target:
        # We always need to load the data required for the target's function if we proceed below.
        targetData = loadChunkParallel(requiredTarget, chunk)

        if target == 'signals report':
            # The function header is "signalsReport(securityName, signals, verbose)"
            return [(security, targetData[security], verbose) for security in targetData]

        elif target == 'validated signals report':
            # The function header is "signalsReport(securityName, validatedSignals, verbose)"
            return [(security, targetData[security], verbose) for security in targetData]

    # ...or we want to either calculate indicator signals or to validate them.
    else:
        # We always need to load historical data for comparisons.
        historicalData = loadChunkParallel('historical', chunk)

        # If we calculate indicators, our target data is only historical.
        if target == 'indicators':
            # The function header is "indicatorsCalculator(securityName, security, verbose)"
            return [(security, historicalData[security], verbose) for security in historicalData]
        
        # We always need to load the data required for the target's function if we proceed below.
        targetData = loadChunkParallel(requiredTarget, chunk)
        
        if target == 'signals':
            # The function header is "signalsCalculator(securityName, security, indicators)"
            return [(security, historicalData[security], targetData[security]) for security in historicalData]

        elif target == 'validated signals':
            # The function header is "signalsValidator(securityName, security, signals, days)"
            return [(security, historicalData[security], targetData[security], extraArgs) for security in historicalData]

def manageReports(target, chunkResults, verbose=False):
    aggregatedResults = {}
    checkCreateFolder(target, 'indicators')

    # Initialize the percentages for each indicator
    for security in chunkResults:
        for indicator in security:
            aggregatedResults[indicator] = {}
            for key in security[indicator]:
                aggregatedResults[indicator][key] = 0.0
    
    # Aggregate them...
    for security in chunkResults:
        for indicator in security:
            for key in security[indicator]:
                # We divide with the number of total loaded securities, because they might be less than those
                # included in portfolio. Those with insufficient data are ignored.
                aggregatedResults[indicator][key] += security[indicator][key] / len(chunkResults) # might carry errors
    
    # Save them individually...
    for indicator in aggregatedResults:
        subFolder = os.path.join(folders[target], 'indicators')
        fileName = os.path.join(subFolder, indicator + '.json')
        with open(fileName, 'w') as f:
            if verbose:
                print('[+] Saving aggregated report for {}'.format(indicator))
            json.dump(aggregatedResults[indicator], f, indent=1)
    
    # ...and all together
    allTogetherFilename = os.path.join(subFolder, 'combined.json')
    with open(allTogetherFilename, 'w') as f:
        if verbose:
            print('[+] Saving aggregated report for all indicators')
        json.dump(aggregatedResults, f, indent=1)