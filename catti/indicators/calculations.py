from catti.IO.general import dataSaver
from pandas import DataFrame
from talib import abstract
import talib


def indicatorsCalculator(securityName, security, verbose=False):
    if verbose:
        print('Calculating indicators for ' + securityName)
    indicatorsDataframe = DataFrame(index=security.index)
    indicatorFunctionGroups = talib.get_function_groups()
    indicatorGroupsNames = [
        'Overlap Studies',
        'Momentum Indicators',
        'Volume Indicators',
        'Volatility Indicators'
        ]
    # We ignore these, for input reasons...
    ignored = ['MAVP', 'MA', 'HT_TRENDLINE', 'SAREXT', 'MACDEXT',\
        'PLUS_DM', 'MINUS_DM', 'ROCP', 'ROCR', 'CCI', 'ATR', 'NATR',\
        'KAMA', 'MAMA', 'MIDPOINT', 'MIDPRICE', 'ROCR100', 'DX']

    # Special cases that return more than 1 values

    ## Overlap Studies
    # BBANDS - upperband, middleband, lowerband
    # MAMA - mama, fama
    ## Momentum Indicator
    # AROON - aroondown, aroonup
    # MACD, MACDEXT, MACDFIX - macd, macdsignal, macdhist
    # STOCH - slowk, slowd
    # STOCHF, STOCHRSI - fastk, fastd

    #twoValues = ['MAMA', 'AROON', 'STOCH', 'STOCHF', 'STOCHRSI']
    #threeValues = ['BBANDS', 'MACD', 'MACDEXT', 'MACDFIX']

    twoValues = {
                'MAMA': ['mama', 'fama'],
                'AROON': ['aroondown', 'aroonup'],
                'STOCH': ['slowk', 'slowd'],
                'STOCHF': ['fastk', 'fastd'],
                'STOCHRSI': ['fastk', 'fastd']
        }
    threeValues = {
                'BBANDS': ['upperband', 'middleband', 'lowerband'],
                'MACD': ['macd', 'macdsignal', 'macdhist'],
                'MACDEXT': ['macd', 'macdsignal', 'macdhist'],
                'MACDFIX': ['macd', 'macdsignal', 'macdhist']
        }
    
    inputs = {
        'open': security['Open'],
        'high': security['High'],
        'low': security['Low'],
        'close': security['Adj Close'],
        'volume': security['Volume']
    }

    for group in indicatorGroupsNames:
        targetGroup = indicatorFunctionGroups[group]
        if verbose:
            print("[i] Target group:" + str(targetGroup))
        for indicator in targetGroup:
            if indicator in ignored:
                continue
            
            if verbose:
                print("[.] [.] Indicator:" + indicator)
            
            indicatorFunction = abstract.Function(indicator)
            
            # Handling different cases
            if indicator in twoValues.keys():
               value1, value2 = indicatorFunction(inputs)
               indicatorsDataframe[indicator + '-' + twoValues[indicator][0]] = value1
               indicatorsDataframe[indicator + '-' + twoValues[indicator][1]] = value2
            elif indicator in threeValues.keys():
               value1, value2, value3 = indicatorFunction(inputs)
               indicatorsDataframe[indicator + '-' + threeValues[indicator][0]] = value1
               indicatorsDataframe[indicator + '-' + threeValues[indicator][1]] = value2
               indicatorsDataframe[indicator + '-' + threeValues[indicator][2]] = value3
            else:
                indicatorsDataframe[indicator] = indicatorFunction(inputs)
    
    auxiliaryCalculator(indicatorsDataframe, verbose)
    
    dataSaver('indicators', indicatorsDataframe, securityName)

def auxiliaryCalculator(indicatorsDataframe, verbose=False):
    if verbose:
        print("[i] Extra auxiliary indicators:")
    
    auxiliary = {
        'CMO': {
            'function': 'SMA',
            'period': 10
        },
        'TRIX': {
            'function': 'SMA',
            'period': 9
        },
        'ADOSC': {
            'function': 'SMA',
            'period': 8
        },
        'PPO': {
            'function': 'EMA',
            'period': 9
        },
        'AD': {
            'function': 'MOM',
            'period': 5
        },
        'OBV': {
            'function': 'MOM',
            'period': 5
        }
    }

    for indicator in auxiliary:
        # Construct the name of the auxiliary indicator
        extraName = indicator + '-' + auxiliary[indicator]['function'] + str(auxiliary[indicator]['period'])
        if verbose:
            print("[.] Indicator:" + extraName)
        indicatorFunction = abstract.Function(auxiliary[indicator]['function'])
        indicatorsDataframe[extraName] = indicatorFunction(indicatorsDataframe[indicator].fillna(0), timeperiod=auxiliary[indicator]['period'])

    #     indicator = 'CMO-SMA10'
    # if verbose:
    #     print("[.] Indicator:" + indicator)
    # indicatorFunction = abstract.Function("SMA")
    # indicatorsDataframe[indicator] = indicatorFunction(indicatorsDataframe['CMO'].fillna(0), timeperiod=10)
    
    # indicator = 'TRIX-SMA9'
    # if verbose:
    #     print("[.] Indicator:" + indicator)
    # indicatorFunction = abstract.Function("SMA")
    # indicatorsDataframe[indicator] = indicatorFunction(indicatorsDataframe['TRIX'].fillna(0), timeperiod=9)
    
    # indicator = 'ADOSC-SMA8'
    # if verbose:
    #     print("[.] Indicator:" + indicator)
    # indicatorFunction = abstract.Function("SMA")
    # indicatorsDataframe[indicator] = indicatorFunction(indicatorsDataframe['ADOSC'].fillna(0), timeperiod=8)
    
    # indicator = 'PPO-SMA9'
    # if verbose:
    #     print("[.] Indicator:" + indicator)
    # indicatorFunction = abstract.Function("SMA")
    # indicatorsDataframe[indicator] = indicatorFunction(indicatorsDataframe['PPO'].fillna(0), timeperiod=9)
    
    # indicator = 'AD-MOM'
    # if verbose:
    #     print("[.] Indicator:" + indicator)
    # indicatorFunction = abstract.Function("MOM")
    # # We need at least 5 days momentum for the 14-day A/D
    # indicatorsDataframe[indicator] = indicatorFunction(indicatorsDataframe['AD'].fillna(0), timeperiod=5)
    
    # indicator = 'OBV-MOM'
    # if verbose:
    #     print("[.] Indicator:" + indicator)
    # indicatorFunction = abstract.Function("MOM")
    # # We need at least 5 days momentum for the 14-day OBV
    # indicatorsDataframe[indicator] = indicatorFunction(indicatorsDataframe['OBV'].fillna(0), timeperiod=5)