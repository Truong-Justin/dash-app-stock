import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ta.trend import MACD
from ta.momentum import RSIIndicator
from dash import html, dcc, Dash
from dash.dependencies import Input, Output, State





def makeCandlestick(fig, stockDF):
    #sets parameters for subplots
    fig = make_subplots(rows = 4, cols = 1, shared_xaxes = True,
                    vertical_spacing = 0.01,
                    row_heights = [0.6, 0.1, 0.15, 0.15])


    #plots candlestick values using stockDF
    fig.add_trace(go.Candlestick(x = stockDF.index,
                                 open = stockDF['Open'],
                                 high = stockDF['High'],
                                 low = stockDF['Low'],
                                 close = stockDF['Close'],
                                 name = 'Open/Close'))
    
    return fig


def makeMA(fig, stockDF):
    #create moving average values
    stockDF["MA5"] = stockDF["Close"].rolling(window = 5).mean()
    stockDF["MA15"] = stockDF["Close"].rolling(window = 15).mean()
    stockDF["MA50"] = stockDF["Close"].rolling(window = 50).mean()
    stockDF["MA200"] = stockDF["Close"].rolling(window = 200).mean()


    #plots moving average values; the 50-day and 200-day averages
    #are visible by default, and the 5-day and 15-day are accessed via legend
    fig.add_trace(go.Scatter(x = stockDF.index, y = stockDF['MA5'], opacity = 0.4, visible="legendonly",
                        line = dict(color = 'blue', width = 2), name = 'MA 5'))
            
    fig.add_trace(go.Scatter(x = stockDF.index, y = stockDF['MA15'], opacity = 0.7, visible = "legendonly",
                        line = dict(color = 'orangered', width = 2), name = 'MA 15'))

    fig.add_trace(go.Scatter(x = stockDF.index, y = stockDF['MA50'], opacity = 0.7,
                        line = dict(color = 'purple', width = 2), name = 'MA 50'))

    fig.add_trace(go.Scatter(x = stockDF.index, y = stockDF['MA200'], opacity = 0.7,
                        line = dict(color = 'black', width = 2), name = 'MA 200'))

    return fig


def makeVolume(fig, stockDF):
    #sets colors of volume bars
    colors = ['green' if row['Open'] - row['Close'] >= 0
          else 'red' for index, row in stockDF.iterrows()]


    #Plot volume trace
    fig.add_trace(go.Bar(x = stockDF.index,
                         y = stockDF['Volume'],
                         marker_color = colors,
                         showlegend = False,
                         name = "Volume"
                         ), row = 2, col = 1)

    return fig


def makeMACD(fig, stockDF):
    #Create MACD values
    macd = MACD(close = stockDF["Close"],
                window_slow = 26,
                window_fast = 12,
                window_sign = 9)

            
    #Sets color for MACD
    colors = ['green' if val >= 0 
                      else 'red' for val in macd.macd_diff()]


    #Plots MACD values
    fig.add_trace(go.Bar(x = stockDF.index,
                         y = macd.macd_diff(),
                         marker_color = colors,
                         showlegend = False,
                         name = "Histogram"
                         ), row = 4, col = 1)


    fig.add_trace(go.Scatter(x = stockDF.index,
                             y = macd.macd(),
                             line = dict(color = 'red', width = 1),
                             showlegend = False,
                             name = "MACD"
                             ), row = 4, col = 1)


    fig.add_trace(go.Scatter(x = stockDF.index,
                             y = macd.macd_signal(),
                             line = dict(color = 'blue', width = 2),
                             showlegend = False,
                             name = "Signal"
                             ), row = 4, col = 1)


    return fig


def makeRSI(fig, stockDF):
    #Create RSI values
    rsi = RSIIndicator(close = stockDF["Close"],
                       window = 14)


    #Plots RSI values
    fig.add_trace(go.Scatter(x = stockDF.index,
                             y = rsi.rsi(),
                             line = dict(color = 'black', width = 2),
                             showlegend = False,
                             name = "RSI"
                             ), row = 3, col = 1)


    fig.add_trace(go.Scatter(x = stockDF.index,
                             y = [30 for val in range(len(stockDF))],
                             line = dict(color = 'red', width = 1),
                             showlegend = False,
                             name = "Oversold"
                             ), row = 3, col = 1)


    fig.add_trace(go.Scatter(x = stockDF.index,
                             y = [70 for val in range(len(stockDF))],
                             line = dict(color = 'green', width = 1),
                             showlegend = False,
                             name = "Overbought"
                             ), row = 3, col = 1)


    return fig


def makeCurrentPrice(fig, stockDF):
    #Plots the last closing price of stock 
    fig.add_trace(go.Scatter(x = stockDF.index,
              y = [stockDF['Close'].iat[-1] for price in range(len(stockDF))],
              opacity = 0.7, line = dict(color = 'red', width = 2, dash = 'dot'),
              name = "Current Price: " + str(round(stockDF['Close'].iat[-1], 2))))
    

    return fig


def supportLevel(stockDF, index):
    #Finds and returns support levels using fractals;
    #if there are two higher lows on each side of the current stockDF['Low'] value, 
    #return this value
    support = stockDF['Low'][index] < stockDF['Low'][index - 1] and \
              stockDF['Low'][index] < stockDF['Low'][index + 1] and \
              stockDF['Low'][index + 1] < stockDF['Low'][index + 2] and \
              stockDF['Low'][index - 1] < stockDF['Low'][index - 2]

    return support


def resistanceLevel(stockDF, index):
    #Finds and returns resistance levels using fractals;
    #If there are two lower highs on each side of the current stock['High'] value,
    #return this value
    resistance = stockDF['High'][index] > stockDF['High'][index - 1] and \
              stockDF['High'][index] > stockDF['High'][index + 1] and \
              stockDF['High'][index + 1] > stockDF['High'][index + 2] and \
              stockDF['High'][index - 1] > stockDF['High'][index - 2]

    return resistance


def isFarFromLevel(stockDF, level, levels):
    #If a level is found near another level, it returns false;

    ##.88 for longer term .97 for short term
    s = np.mean(stockDF['High'] - (stockDF['Low'] * .89))

    return np.sum([abs(level - x) < s for x in levels]) == 0


def makeLevels(fig, stockDF):
    #Traverses through stockDF and finds key support/resistance levels
    levels = []
    for index in range(2, stockDF.shape[0] - 2):
        if supportLevel(stockDF, index):
            support = stockDF['Low'][index]
            if isFarFromLevel(stockDF, support, levels):
                levels.append((support))
            
        elif resistanceLevel(stockDF, index):
            resistance = stockDF['High'][index]
            if isFarFromLevel(stockDF, resistance, levels):
                levels.append((resistance))

    levels.sort()
    

    #Plots the key levels within levels 
    for i in range(len(levels)):
        fig.add_trace(go.Scatter(x = stockDF.index,
                             y = [levels[i] for val in range(len(stockDF))],
                             line = dict(color = "black"),
                             name = "Sup/Res: " + str(round(levels[i], 2)),
                             hoverinfo = "skip",
                             opacity = 0.3))

    return fig


def findMax(stockDF):
    max = 0
    for i in range(len(stockDF)):
        if stockDF["Close"][i] > max:
            max = stockDF["Close"][i]
        
    return max


def findLow(stockDF):
    low = 50
    for i in range(len(stockDF)):
        if stockDF["Close"][i] < low:
            low = stockDF["Close"][i]

    return low


def makeFibLevels(max, low, fig, stockDF):
    fibRatios = [.236, .382, .5, .618, .786, 1]
    fibLevels = []
    dif = max - low

    for i in range(len(fibRatios)):
        fibLevels.append(dif * fibRatios[i])


    #for prices that are above the last resistance/support line within fibLevels,
    #look to see if there can be any levels drawn using fractals that are also not 
    #too close to the current last support/resistance;
    #We really are just looking for the last resistance level;
    fractal = fibLevels[-1] + (fibLevels[-1] * .17)
    if (fibLevels[-1] < fractal) and (fractal < max):
         fibLevels.append(fractal)  
    

    for i in range(len(fibLevels)):
        fig.add_trace(go.Scatter(x = stockDF.index,
                             y = [fibLevels[i] for val in range(len(stockDF))],
                             line = dict(color = "black"),
                             name = "Sup/Res: " + str(round(fibLevels[i], 2)),
                             hoverinfo = "skip",
                             opacity = 0.3))
    
    return fig


def graphLayout(fig, choice):
    #Sets the layout of the graph and legend
    fig.update_layout(title_text = choice + ' Price Action', 
                  title_x = 0.5, 
                  legend_title_text = "Legend Items",
                  dragmode = "pan", 
                  xaxis_rangeslider_visible = False, 
                  hovermode = "x", 
                  legend = dict(bgcolor="#E2E2E2",
                           bordercolor="Black",
                           borderwidth=2)
                               
                 )

    subplotLabels(fig)

    return fig


def subplotLabels(fig):
    #Sets subplot labels
    fig.update_yaxes(title_text = "Price", row = 1, col = 1)
    fig.update_yaxes(title_text = "Volume", row = 2, col = 1)
    fig.update_yaxes(title_text = "RSI", row = 3, col = 1)
    fig.update_yaxes(title_text = "MACD", showgrid = False, row = 4, col = 1)

    return fig


def xAxes(fig):
    #Remove none trading days from dataset and sets behavior for x-axis mouse-hovering
    fig.update_xaxes(rangebreaks = [dict(bounds = ["sat", "mon"])], 
                 autorange = True, 
                 showspikes = True, 
                 spikedash = "dot",
                 spikethickness = 1, 
                 spikemode = "across", 
                 spikecolor = "black")
    
    return fig



fig = go.Figure()
config = dict({'scrollZoom': True})



stockApp = Dash(__name__, meta_tags=[{'name': 'viewport', 
                       'content':'width=device-width, initial-scale=1.0'}])

application = stockApp.server

stockApp.layout = html.Div([
    dcc.Graph(figure = fig, config = config,

              style = {'width': '99vw', 'height': '93vh'},
              id = "stockGraph"
             ),

             html.Div([
                dcc.Input(
                    id = "userInput",
                    type = "text",
                    placeholder = "Ticker Symbol"
                         ),
            
            html.Button("Submit", id = "btnSubmit")]),
                      ],
            )
                

             


@stockApp.callback(
    Output("stockGraph", "figure"),
    Input("btnSubmit", "n_clicks"),
    State("userInput", "value"))

def update_figure(n, tickerChoice):
    #set choice to something if !isPostBack
    if tickerChoice == None:
        tickerChoice = 'AAPL'


    #make stockDF    
    today = date.today()
    stockDF = yf.download(tickerChoice, start = '2019-12-01', end = today )

    #make go Figure object as fig
    fig = go.Figure()

    #make and plot candlestick chart
    fig = makeCandlestick(fig, stockDF)

    #update layout properties
    fig = graphLayout(fig, tickerChoice.upper())

    #updates x-axis parameters
    fig = xAxes(fig)

    #make and plot subplots charts and moving averages
    fig = makeMA(fig, stockDF)
    fig = makeVolume(fig, stockDF)
    fig = makeMACD(fig, stockDF)
    fig = makeRSI(fig, stockDF)

    #make and plot stock's last closing price
    fig = makeCurrentPrice(fig, stockDF)

    #make and plot stock's resistance/support values using fibonacci retracement
    fig = makeFibLevels(max, low, fig, stockDF)

    
    return fig


if __name__ == '__main__':
    application.run(debug = False, port = 8080)
