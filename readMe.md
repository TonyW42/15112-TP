Instructions 

You can find a demo video for this project on 
- https://youtu.be/DTKM3B2D4sI

Project description:

  - The project is called "Trade Simulation". It is an app that allows the user to check 
    stock info (e.g. price, news headlines and sentiment analysis, and corporate financial
    information). The app also allows users to portfolios and trade virtually to construct
    and view portfolios. 

  - For more detailed instructions, please refer to the folder "Design Document" 
    (especially "Yilin Wang_Project proposal " and "update2") and follows the instruction in 
    the pop-up.

  - Note: when you are asked to enter stock name, DO NOT enter the real company name like 
          "Apple" or "Google", but you should enter unique Ticker symbols like "AAPL" or "GOOG".

  - You may want to refer ticker symbol to this list: 
    http://eoddata.com/symbols.aspx
    Although some ticker symbols might be not available for search due to module limitation. 


Before you start:

  -  Install all required modules listed in the beginning of the code. It is recommended 
     that you install modules using Anaconda (download at "https://www.anaconda.com/products/individual")
  
  -  After you installed Anaconda, go to VSCode-Command Palette and type in "Python: Select Interpreter"
     and select the one with Anaconda in it. Very important. Won't compile if you used other interpreter. 
     (theoretically it would word if you use pip3 to install the modules, but Anaconda allows more convenient
     installation of modules)

  -  After that, open terminal and use pip install + module name to install modules. 

  -  There are some very important updates in "Update2". Please definitely check on that. 


Module list:

  -  It is recommended that you install all modules again using pip. However, some module is built-in with
     python, so you don't have to install those. Here are a list of modules that you definitely need to install:

  -  matplotlib, threading, PIL, yfinance, yahoo_fin, requests, pandas, numpy, bs4,
     lxml, vaderSentiment, webbrowser, datetime

  -  Though some modules are built-in, it is still recommended that you install all modules, as their might
     be updates and differences in version. If anything went wrong, please follow the instruction in the shell
     to install modules. Generally issues could be fixed by re-installing modules using pip. 


Special Instructions (VERY IMPORTANT):

  -  After you installed yfinance module, please go to the local source file on you computer (../yfinance).
     open the file "base.py" (../yfinance/base.py) and change line 283-284 to the following: 

  -  url = "{}/{}".format(self._scrape_url, self.ticker)
     holders = _pd.read_html(url+'\holders')

  - This is very important. If you do not do this step, you will not be able to use the "financials" page
    and you will get repeated error message. If this approach fails, you can also replace the "base.py" file
    in your local source file with the attached file "base.py". This should also work

  -  Before you run the file, type the following command in terminal: "pip install requests_html"
     If you do not do this, you will get repeated error message in the sentiment page. 


How to run the file:

   - To run the file, simply run the document "TP3 / final version.py" after you did the prior steps. 
     You do not need to do anything else beside this. 

   - Note: If it is the first time you use this app, please register first in using the "Join Now" button. 


Short-cut commands:
 
  -  There are no short-cut commands for this app. Please do not use "enter" or "esc". It won't work. 
     Everything command is executed based on mouse click. 

Notes:

  -  in case anything failed to load, you can still access the features of the frames
     by referring to the video and by accessing the folder "frames". 