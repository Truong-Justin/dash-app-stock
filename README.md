# Python Stock Dashboard


## Project Description
This web application was made using Python and the Dash framework. OHLC (Open/High/Low/Close) values are obtained using the yfinance API that interfaces with the Yahoo Finance! website. This project was intended to display relevant stock information to a user, without requiring the user to go through a complicated setup process. When the web application is accessed by the user, they have access to: common standard-moving-averages, MACD and RSI indicators, volume, and resistance/support levels that are derived using a fractal-based algorithm or a fibonacci-based algorithm depending on the selected timeframe.


## How to run the web application
1. The first option is to visit the [deployed web application](stockdash.justintruong.studio).
    - This is the easiest option.

2. The second option involves installing the application onto a local machine.
    - First, download the repository into a folder onto your device.
    - Then, navigate to folder using the terminal/console where the repository was saved to and install the dependencies within the requirements.txt file.
      - To install dependencies, enter $ pip install -r requirements.txt using the terminal/command prompt.

    - Run the program either via the terminal/command prompt by typing **python3 app.py** or by running the program within your preferred IDE that supports Python. 
    - The program will run within the local machine's web browser via http://127.0.0.1:8080/


## How to  use the project
1. Open the application in your chosen web browser; scroll-to-zoom doesn't work for Safari web browser. 
2. Enter the Ticker symbol into the text input box in the lower left hand corner. 
3. Press enter to load the new stock graph.
4. To display/hide moving averages and resistance/support values, click on the corresponding value within the interactive legend in the right hand corner.



## Planned additions
1. I plan to revise the UI and include Dash component that will let the user select a start and end date for the stock data.

2. Currently, the user needs to know what the abbreviated Ticker symbol. I want to convert the current input textbox into a drop-down list with autocomplete that will help the user choose the right company that they intend to view. 

3. To make the application more like an actual dashboard, I plan to add more relevant data to show the user such as the stock's P/E ratio and EPS so that the user can make better decisions.


