from catti.IO.general import dataSaver
from pandas import DataFrame


def signalConditions(security, indicators, index):
    conditions = {
        # There are moving averages or indicators that generate signals the same way.
        # Unfortunately, I have to repeat code with this design. Can't think anything better right now.
    
        'DEMA': {
            # Crossover - Price Ascends above Indicator
            'buy': crossoverAaboveB(index, security['Adj Close'], indicators['DEMA']),
            # Crossover - Price Descends below Indicator
            'sell': crossoverAbelowB(index, security['Adj Close'], indicators['DEMA'])
            }
        ,
        'EMA': {
            # Crossover - Price Ascends above Indicator
            'buy': crossoverAaboveB(index, security['Adj Close'], indicators['EMA']),
            # Crossover - Price Descends below Indicator
            'sell': crossoverAbelowB(index, security['Adj Close'], indicators['EMA'])
            }
        ,
        'SMA': {
            # Crossover - Price Ascends above Indicator
            'buy': crossoverAaboveB(index, security['Adj Close'], indicators['SMA']),
            # Crossover - Price Descends below Indicator
            'sell': crossoverAbelowB(index, security['Adj Close'], indicators['SMA'])
            }
        ,
        'T3': {
            # Crossover - Price Ascends above Indicator
            'buy': crossoverAaboveB(index, security['Adj Close'], indicators['T3']),
            # Crossover - Price Descends below Indicator
            'sell': crossoverAbelowB(index, security['Adj Close'], indicators['T3'])
            }
        ,
        'TEMA': {
            # Crossover - Price Ascends above Indicator
            'buy': crossoverAaboveB(index, security['Adj Close'], indicators['TEMA']),
            # Crossover - Price Descends below Indicator
            'sell': crossoverAbelowB(index, security['Adj Close'], indicators['TEMA'])
            }
        ,
        'TRIMA': {
            # Crossover - Price Ascends above Indicator
            'buy': crossoverAaboveB(index, security['Adj Close'], indicators['TRIMA']),
            # Crossover - Price Descends below Indicator
            'sell': crossoverAbelowB(index, security['Adj Close'], indicators['TRIMA'])
            }
        ,
        'WMA': {
            # Crossover - Price Ascends above Indicator
            'buy': crossoverAaboveB(index, security['Adj Close'], indicators['WMA']),
            # Crossover - Price Descends below Indicator
            'sell': crossoverAbelowB(index, security['Adj Close'], indicators['WMA'])
            }
        ,
        'SAR': {
            # Crossover - Price Ascends above Indicator
            'buy': crossoverAaboveB(index, security['Adj Close'], indicators['SAR']),
            # Crossover - Price Descends below Indicator
            'sell': crossoverAbelowB(index, security['Adj Close'], indicators['SAR'])
            }
        ,
        'BBANDS': {
            # Crossover on the lowerband - Oversold, reversal is imminent
            'buy': crossoverAbelowB(index, security['Adj Close'], indicators['BBANDS-lowerband']),
            # Crossover on the upperband - Overbought, reversal is imminent 
            'sell': crossoverAaboveB(index, security['Adj Close'], indicators['BBANDS-upperband'])
        },
        # 'MAMA': {
        #     # Crossover - MAMA crosses above the FAMA
        #     'buy': crossoverAaboveB(index, indicators['MAMA-mama'], indicators['MAMA-fama']),
        #     # Crossover - MAMA crosses below the FAMA
        #     'sell': crossoverAbelowB(index, indicators['MAMA-mama'], indicators['MAMA-fama'])
        # },
        'ADX': {
            # Crossover - +DI crosses above the -DI and the trend is strong (ADX is at least 25%)
            'buy': crossoverAaboveB(index, indicators['PLUS_DI'], indicators['MINUS_DI']) \
                and (indicators['ADX'].iloc[index] >= 25.0),
            # Crossover - +DI crosses below the -DI and the trend is strong (ADX is at least 25%)
            'sell': crossoverAbelowB(index, indicators['PLUS_DI'], indicators['MINUS_DI']) \
                and (indicators['ADX'].iloc[index] >= 25.0),
        },
        'ADXR': {
            # Crossover - ADX crosses above the ADXR and the trend is strong (ADX is at least 25%)
            'buy': crossoverAaboveB(index, indicators['ADX'], indicators['ADXR']) \
                and indicators['ADX'].iloc[index] >= 25.0,
            # Crossover - ADX crosses below the ADXR and the trend is strong (ADX is at least 25%)
            'sell': crossoverAbelowB(index, indicators['ADX'], indicators['ADXR']) \
                and indicators['ADX'].iloc[index] >= 25.0
        },
        'APO': {
            # buy signal when the Price Oscillator rises above zero
            'buy': crossoverAaboveValue(index, indicators['APO'], 0),
            # sell signal when the Price Oscillator falls below zero
            'sell': crossoverAbelowValue(index, indicators['APO'], 0)
        },
        'AROON': {
            # buy signal when the Aroon Up crosses above Aroon Down
            'buy': crossoverAaboveB(index, indicators['AROON-aroonup'], indicators['AROON-aroondown']),
            # sell signal when the Aroon Up crosses below Aroon Down
            'sell': crossoverAbelowB(index, indicators['AROON-aroonup'], indicators['AROON-aroondown'])
        },
        'AROONOSC': {
            # buy signal when the Aroon Oscillator rises above zero
            'buy': crossoverAaboveValue(index, indicators['AROONOSC'], 0),
            # sell signal when the Aroon Oscillator falls below zero
            'sell': crossoverAbelowValue(index, indicators['AROONOSC'], 0)
        },
        'BOP': {
            # buy signal when the Power of Balance rises above zero
            'buy': crossoverAaboveValue(index, indicators['BOP'], 0),
            # sell signal when the Power of Balance falls below zero
            'sell': crossoverAbelowValue(index, indicators['BOP'], 0)
        },
        'CMO': {
            # buy signal when the CMO crosses above the 10-day SMA of itself
            'buy': crossoverAaboveB(index, indicators['CMO'], indicators['CMO-SMA10']),
            # sell signal when the CMO crosses below the 10-day SMA of itself
            'sell': crossoverAbelowB(index, indicators['CMO'], indicators['CMO-SMA10'])
        },
        'MACD': {
            # buy signal when the MACD crosses above the MACD signal (trigger) line
            'buy': crossoverAaboveB(index, indicators['MACD-macd'], indicators['MACD-macdsignal']),
            # sell signal when the MACD crosses below the MACD signal (trigger) line
            'sell': crossoverAbelowB(index, indicators['MACD-macd'], indicators['MACD-macdsignal'])
        },
        # The time periods for the MACD are often given as 26 and 12.
        # However the function actually uses exponential constants of 0.075 and 0.15,
        # which are closer to 25.6667 and 12.3333 periods.
        # This indicator has fixed periods to 25 and 12 respectively.
        'MACDFIX': {
            # buy signal when the MACD crosses above the MACD signal (trigger) line
            'buy': crossoverAaboveB(index, indicators['MACDFIX-macd'], indicators['MACDFIX-macdsignal']),
            # sell signal when the MACD crosses below the MACD signal (trigger) line
            'sell': crossoverAbelowB(index, indicators['MACDFIX-macd'], indicators['MACDFIX-macdsignal'])
        },
        'MFI': {
            # buy signal when the MFI falls below 20, oversold condition
            'buy': crossoverAaboveValue(index, indicators['MFI'], 20),
            # sell signal when the MFI rises above 80, overbought condition
            'sell': crossoverAbelowValue(index, indicators['MFI'], 80)
        },
        'PPO': {
            # buy signal when the Percentage Price Oscillator crosses above the 9-day EMA of itself
            # or goes above the 0 centerline
            'buy': crossoverAaboveB(index, indicators['PPO'], indicators['PPO-EMA9']) \
                or crossoverAaboveValue(index, indicators['PPO'], 0),
            # sell signal when the Percentage Price Oscillator crosses below the 9-day EMA of itself
            # or goes below the 0 centerline
            'sell': crossoverAbelowB(index, indicators['PPO'], indicators['PPO-EMA9']) \
                or crossoverAbelowValue(index, indicators['PPO'], 0)
        },
        'ROC': {
            # buy signal when the ROC rises above the 0 centerline
            'buy': crossoverAaboveValue(index, indicators['ROC'], 0),
            # sell signal when the ROC falls below the 0 centerline
            'sell': crossoverAbelowValue(index, indicators['ROC'], 0)
        },
        'RSI': {
            # buy signal while the RSI stays below 30
            'buy': isBelowValue(index, indicators['RSI'], 30),
            # sell signal while the RSI stays above 70
            'sell': isAboveValue(index, indicators['RSI'], 70)
        },
        'STOCHRSI': {
            # buy signal while the STOCHRSI stays below 20
            'buy': isBelowValue(index, indicators['STOCHRSI-fastk'], 20),
            # sell signal while the STOCHRSI stays above 80
            'sell': isAboveValue(index, indicators['STOCHRSI-fastk'], 80)
        },
        'TRIX': {
            # buy signal when the TRIX crosses above the 9-day MA of itself or the 0 centerline
            'buy': crossoverAaboveB(index, indicators['TRIX'], indicators['TRIX-SMA9']) \
                or crossoverAaboveValue(index, indicators['TRIX'], 0),
            # sell signal when the TRIX crosses below the 9-day MA of itself or the 0 centerline
            'sell': crossoverAbelowB(index, indicators['TRIX'], indicators['TRIX-SMA9']) \
                or crossoverAbelowValue(index, indicators['TRIX'], 0)
        },
        'ULTOSC': {
            # buy signal when the Ultimate Oscillator crosses above 30, oversold condition
            'buy': crossoverAaboveValue(index, indicators['ULTOSC'], 30),
            # sell signal when the Ultimate Oscillator crosses below 70, overbought condition
            'sell': crossoverAbelowValue(index, indicators['ULTOSC'], 70)
        },
        'WILLR': {
            # buy signal when the Williams %R just rises above -80, moves out oversold territory
            'buy': crossoverAaboveValue(index, indicators['WILLR'], -80),
            # sell signal when the Williams %R just falls below -20, moves out overbought territory
            'sell': crossoverAbelowValue(index, indicators['WILLR'], -20)
        },
        'AD': {
            # buy signal when the Chaikin A/D Line has positive momentum
            'buy': indicators['AD-MOM5'].iloc[index] > 0,
            # sell signal when the Chaikin A/D Line has negative momentum
            'sell': indicators['AD-MOM5'].iloc[index] < 0,
        },
        'OBV': {
            # buy signal when the On Balance Volume has positive momentum
            'buy': indicators['OBV-MOM5'].iloc[index] > 0,
            # sell signal when the On Balance Volume has positive momentum
            'sell': indicators['OBV-MOM5'].iloc[index] < 0
        },
        'ADOSC': {
            # buy signal when the Chaikin A/D Oscillator crosses above the 8-day SMA of itself
            'buy': crossoverAaboveB(index, indicators['ADOSC'], indicators['ADOSC-SMA8']),
            # sell signal when the Chaikin A/D Oscillator crosses below the 8-day SMA of itself
            'sell': crossoverAbelowB(index, indicators['ADOSC'], indicators['ADOSC-SMA8'])
        },
        'STOCH': {
            # buy signal when the Fast %K crosses above the Slow %D, it is a buy signal
            'buy': crossoverAaboveB(index, indicators['STOCHF-fastk'], indicators['STOCH-slowd']),
            # sell signal when the Fast %K crosses below the Slow %D, it is a sell signal
            'sell': crossoverAbelowB(index, indicators['STOCHF-fastk'], indicators['STOCH-slowd'])
        }
    }

    return conditions

def isMomentumPositive(index, data):
    # index : the index of the date will be compared with the (n-1)th index
    #         (first value of the list in not handled here)
    # data  : the data we seek momentum for
    return data.iloc[index] - data.iloc[index - 1] > 0

def crossoverAaboveB(index, A, B):
    # index : the index of the date will be compared with the (n-1)th index
    #         (first value of the list in not handled here)
    # A     : the points that we want to cross, from below, above B
    # B     : the points that we want to cross, from above, below A
    return A.iloc[index - 1] <= B.iloc[index - 1] and A.iloc[index] >= B.iloc[index]

def crossoverAbelowB(index, A, B):
    # index : the index of the date will be compared with the (n-1)th index
    #         (first value of the list in not handled here)
    # A     : the points that we want to cross, from above, below B
    # B     : the points that we want to cross, from below, above A
    return A.iloc[index - 1] >= B.iloc[index - 1] and A.iloc[index] <= B.iloc[index]

def crossoverAaboveValue(index, A, value):
    # index : the index of the date will be compared with the (n-1)th index
    #         (first value of the list in not handled here)
    # A     : the points that we want to cross, from below, above a value
    # value : the value we want to cross below A
    return A.iloc[index - 1] <= value and A.iloc[index] >= value

def crossoverAbelowValue(index, A, value):
    # index : the index of the date will be compared with the (n-1)th index
    #         (first value of the list in not handled here)
    # A     : the points that we want to cross, from above, below a value
    # value : the value we want to cross above A
    return A.iloc[index - 1] >= value and A.iloc[index] <= value

def isAboveValue(index, point, value):
    # index : the index of the date will be compared with a value
    # point : the point that we want to compare
    # value : the value we want it to be above
    return point.iloc[index] > value

def isBelowValue(index, point, value):
    # index : the index of the date will be compared with a value
    # point : the point that we want to compare
    # value : the value we want it to be below
    return point.iloc[index] < value

def signalsCalculator(securityName, security, indicators):
    signalsDataframe = DataFrame(index=security.index)
    
    # We skip the first date because we compare each one
    # with the previous date for a crossover.
    for index in range(1, len(security.index)):
        # Check all buy/sell conditions for each indicator for a specific date (index)
        conditions = signalConditions(security, indicators, index)
    
        # Iterate through all the indicators for that date (index) and store signals
        for indicator in conditions.keys():
            if conditions[indicator]['buy']:
                signalsDataframe.at[indicators.index[index], indicator] = 'buy'
            elif conditions[indicator]['sell']:
                signalsDataframe.at[indicators.index[index], indicator] = 'sell'
            # else:
                # signalsDataframe.at[indicators.index[index], indicator] = 'neutral'
    
    dataSaver('signals', signalsDataframe, securityName)