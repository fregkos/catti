from catti.IO.general import dataSaver
from pandas import DataFrame


def signalsValidator(securityName, security, signals, days=1):
    signalsValidationDataframe = DataFrame(index=security.index)
    
    # We skip the first day (see why @ indicatorSignals/calcAllSignals)
    # We skip the last n days because we check every n days after a signal,
    # Therefore, we don't care about the last n days,
    # because we have no future data for them.
    for index in range(1, len(signals.index) - days):
        for indicator in signals.columns:
            # If we have a buy signal, we expect after n days that the price will rise
            #if signals.loc[indicator].iat[index] == 'buy':
            if signals.at[security.index[index], indicator] == 'buy':
                if security['Adj Close'].iloc[index + days] >= security['Adj Close'].iloc[index]:
                    signalsValidationDataframe.at[security.index[index], indicator] = True
                else:
                    signalsValidationDataframe.at[security.index[index], indicator] = False
            # Else if we have a sell signal, we expect after n days that the price will fall
            elif signals.at[security.index[index], indicator] == 'sell':
                if security['Adj Close'].iloc[index + days] <= security['Adj Close'].iloc[index]:
                    signalsValidationDataframe.at[security.index[index], indicator] = True
                else:
                    signalsValidationDataframe.at[security.index[index], indicator] = False

    dataSaver('validated signals', signalsValidationDataframe, securityName)