######################################

# Name: Yilin Wang
# Andrew Id: yilinwan
# CMU 15112 TP: Trading Simulation

######################################

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk 
from tkinter import ttk
import threading

import random
from PIL import Image, ImageTk
import urllib.request
from urllib.request import Request, urlopen
# pip install requests_html (run in terminal before run the app)
import yfinance as yf 
from yahoo_fin import stock_info as si
import matplotlib.pyplot as plt

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import lxml
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import webbrowser  
import os
import datetime

############# 

### adapted from https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter
def rgbval(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb   


## Adapted from https://stackoverflow.com/questions/8742644/python-2-7-tkinter-open-webbrowser-click
def openURL(url):
    webbrowser.open(url)
    #############################################################


## loosely adapted from https://stackoverflow.com/questions/8286352/how-to-save-an-image-locally-using-python-whose-url-address-i-already-know
def saveImage(url,filename):
    if not os.path.exists("temp"):
        os.makedirs("temp")
    prePath = "temp/imageSet"
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    urllib.request.urlretrieve(url, filename)
####################################################################

def searchHist(stock):
    path = "temp/" + parameters.user + "/Hist"
    file = open(path,"a")
    file.close()
    content = open(path,"r").read().splitlines()
    result = dict()
    for line in content:
        elems = line.split(" ")
        result[elems[0]] = elems[1]
    result[stock.upper()] = int(result.get(stock.upper(),0)) + 1
    file = open(path,"w")
    for key in result:
        file.write(key + " " + str(result[key]))
        file.write("\n")
    file.close()
     
    

def MovAvg(df,startY,minPrice,priceRange,effectiveY,x0,barWidth):
    coordinates = []
    ###### remove -1  ???? A: no need. 
    for i in range(len(df)-1):
        Ycoor = startY - (df.iloc[i]-minPrice)/priceRange*(effectiveY)
        Ycoor2 = startY - (df.iloc[i+1]-minPrice)/priceRange*(effectiveY)
        Xcoor = x0+i*barWidth
        Xcoor2 = x0+(i+1)*barWidth
        coordinates.extend([Xcoor,Ycoor,Xcoor2,Ycoor2])
    return coordinates


def removeElem(L, n):
    result = []
    for elem in L:
        if elem != n:
            result.append(elem)
    return result


def existElem(D,n):
    for key in D:
        if D[key] == n:
            return True
    return False

#####################   Fonts used   ##########################

titleFont = "Arial 25"
bigTitle = "Arial 37 bold"
smallTitle = "Arial 15"
medianTitle = "Arial 20"

###############################################################


## Standard Tkinter setting closely adapted from
## https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/
############################################################

class myapp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        container.pack(side = "top", fill="both",expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        self.login = {}
        for F in [financials,portfolio,initial,graph,sentimentStat,startPage,actions]:
            frame = F(container,self)
            self.frames[F] = frame 
            frame.grid(row=0,column=0,sticky="nsew")
        self.show_frame(initial)


    def show_frame(self, cont):
        frame=self.frames[cont]
        frame.tkraise()

##############################################################

    def quit(self):
        self.destroy()
    

    @staticmethod
    def openURL(url):
        webbrowser.open_new(url)

    
##############################################################

class initial(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.imageURL = "https://www.ft.com/__origami/service/image/v2/images/raw/http://prod-upp-image-read.ft.com/d5fd785c-e077-11e9-b8e0-026e07cbe5b4?source=next&fit=scale-down&quality=highest&width=1440"
        self.userInfo = dict()
        if not os.path.exists("temp"):
            os.makedirs("temp")
        if not os.path.exists("temp/username"):
            os.makedirs("temp/username")
        file = open("temp/username/userInfo","a")
        content = open("temp/username/userInfo", "r").read().splitlines()
        i = 0
        #####
        while i < (len(content)-1):
            self.userInfo[content[i]] = content[i+1]
            i+=2
        self.controller = controller
        self.drawWelcome()
        

    def drawWelcome(self):
        imagePath="temp/imageSet/image1.jpg"
        if not os.path.exists(imagePath):
            saveImage(self.imageURL,imagePath)
        content = Image.open(imagePath)
        ######## This line is inspired by https://www.daniweb.com/programming/software-development/threads/369823/resizing-image
        content = content.resize((1000, 450), Image.ANTIALIAS)
        #######################################################################
        image = ImageTk.PhotoImage(content)
        imgLabel=tk.Label(self,image=image)
        imgLabel.image = image
        imgLabel.place(relx=0.5,rely=0.3,anchor=tk.CENTER)
        #####################################################################
        label1=tk.Label(self,text="Welcome to Trading Simulation!",font=titleFont)
        label1.place(relx=0.5,rely=0.65,anchor=tk.CENTER)
        button1=tk.Button(self,text="Login",command=self.login,bg="red",width=25,height=2,cursor="plus",relief=tk.RAISED)#.grid(row=3)
        button1.place(relx=0.5,rely=0.75,anchor=tk.CENTER)
        button2=tk.Button(self,text="Join Now",command=self.register,width=25,height=2)#.grid(row=5)
        button2.place(relx=0.5,rely=0.85,anchor=tk.CENTER)
        button3=tk.Button(self,text="Quit",command=lambda:self.controller.quit(),width=25,height=2)#.grid(row=7)
        button3.place(relx=0.5,rely=0.95,anchor=tk.CENTER)


    ###### mechanism inspired by https://yq.aliyun.com/articles/396114
    def askLoginInfo(self):
        popUp = loginPopup()
        self.wait_window(popUp)
        return popUp.info
    ###################################################################
    
    def registerInfo(self):
        popUp = registerPopup()
        self.wait_window(popUp)
        return popUp.info
    

    def wrongPassword(self):
        popUp = wrongPassword()
        self.wait_window(popUp)
        return popUp.answer


    def noUser(self):
        popUp = noUserName()
        self.wait_window(popUp)
        return popUp.answer
    

    def sameUsername(self):
        popUp = sameUserName()
        self.wait_window(popUp)
        return popUp.answer


    def success(self):
        popUp = errorPopup(message="Registration Successful. Login?")
        self.wait_window(popUp)
        return popUp.answer

    def register(self):
        info = self.registerInfo()
        if info == None: return 
        if info[0] in self.userInfo:
            reEnter = self.sameUsername()
            if reEnter:
                self.register()
        else:
            self.userInfo[info[0]] = info[1]
            ################### inspired by https://www.simplifiedpython.net/python-gui-login/
            file = open("temp/username/userInfo", "a")
            file.write(info[0] + "\n")
            file.write(info[1]+"\n")
            file.close()
            #####################################################################
            login = self.success()
            if login:
                self.login()
            return 



    def login(self):
        info = self.askLoginInfo()
        if info == None: return
        elif self.userInfo.get(info[0],None) == None:
            self.controller.show_frame(initial)
            answer = self.noUser()
            if answer:
                self.register()
            return 
        elif self.userInfo[info[0]] == info[1]:
            if not os.path.exists("temp/" + info[0]):
                os.makedirs("temp/" + info[0])
            self.controller.show_frame(startPage)
            parameters.user = info[0]
            return 
        elif self.userInfo[info[0]] != info[1]:
            reEnter = self.wrongPassword()
            if reEnter:
                self.login()
    

####### ideology inspired by https://yq.aliyun.com/articles/396114    #########         
class registerPopup(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.drawDialog()
    

    def drawDialog(self):
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        tk.Label(self,text="Reigister here",font=medianTitle).grid(row=0)
        tk.Label(self).grid(row=1)
        tk.Label(self,text="Username: ",font=smallTitle).grid(row=2,column=0,sticky="w")
        tk.Entry(self,textvariable=self.username).grid(row=2,column=1,sticky="e")
        tk.Label(self,text="Password: ").grid(row=3,column=0,sticky="w")
        tk.Entry(self,textvariable=self.password).grid(row=3,column=1,sticky="e")
        tk.Label(self).grid(row=4)
        tk.Button(self,text="OK",font=smallTitle,width=10,command=self.OK).grid(row=5,column=0,sticky="w")
        tk.Button(self,text="Cancel",font=smallTitle, width=10,command=self.quit).grid(row=5,column=1,sticky="e")


    def OK(self):
        self.info = [self.username.get(),self.password.get()]
        self.destroy()
    

    def quit(self):
        self.info = None
        self.destroy()    
    ############################################################################



class wrongPassword(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.drawDialog()
        self.answer = False
    

    def drawDialog(self):
        tk.Label(self,text="Wrong password! Re-enter?",font=medianTitle).grid(row=0)
        tk.Label(self).grid(row=1)
        tk.Button(self,text="YES",font=smallTitle,width=10,command=self.revert).grid(row=2,sticky="w")
        tk.Button(self,text="No",font=smallTitle,width=10,command=self.no).grid(row=2,sticky="e")
    

    def no(self):
        self.destroy()


    def revert(self):
        self.answer = True
        self.destroy()



class noUserName(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.answer = False
        self.drawDialog()
    

    def drawDialog(self):
        tk.Label(self,text="No user found! Register?",font=medianTitle).grid(row=0)
        tk.Label(self).grid(row=1)
        tk.Button(self,text="Yes",width=10,font=smallTitle,command=self.revert).grid(row=2,sticky="w")
        tk.Button(self,text="NO",width=10,command=self.no,font=smallTitle).grid(row=2,sticky="e")
    

    def no(self):
        self.destroy()


    def revert(self):
        self.answer = True
        self.destroy()



class sameUserName(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.answer= False
        self.drawDialog()
    

    def drawDialog(self):
        tk.Label(self,text="Username already taken! Choose another one?",font=smallTitle).grid(row=0)
        tk.Label(self).grid(row=1)
        tk.Button(self,text="YES",font=smallTitle,width=10,command=self.revert).grid(row=2,sticky="w")
        tk.Button(self,text="NO",width=10,font=smallTitle,command=self.quit).grid(row=2,sticky="e")
    

    def quit(self):
        self.destroy()
    

    def revert(self):
        self.answer=True
        self.destroy()



class loginPopup(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.drawDialog()
    
    def drawDialog(self):
        tk.Label(self,text="Login here",font=medianTitle).grid(row=0,sticky="nsew")
        tk.Label(self).grid(row=1)
        tk.Label(self,text="Username: ",font=smallTitle).grid(row=2,column=0,sticky="w")
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        tk.Entry(self,textvariable=self.username).grid(row=2,column=1,sticky="e")
        tk.Label(self,text="Password: ", font=smallTitle).grid(row=3,column=0,sticky="w")
        tk.Entry(self,textvariable=self.password,show="*").grid(row=3,column=1,sticky="e")
        tk.Label(self).grid(row=4)
        tk.Button(self,text="OK",width=10,font=smallTitle,command=self.OK).grid(row=5,column=0,sticky="w")
        tk.Button(self,text="Cancel",width=10,font=smallTitle,command=self.quit).grid(row=5,column=1,sticky="e")

    def OK(self):
        self.info = [self.username.get(),self.password.get()]
        self.destroy()
    
    def quit(self):
        self.info = None
        self.destroy()



class startPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.imageURL = "https://www.nyse.com/publicdocs/images/NYSE_BusyFloor_Vertical_media.jpg"
        self.drawGraph()
        label = tk.Label(self,text="Start Page",font=bigTitle)
        label.place(relx = 0.5,rely = 0.03,anchor = tk.CENTER)
        label2 = tk.Button(self,text="Menu", width=10,height=2,font=titleFont,fg="dark red")
        label2.place(relx = 0.77, rely = 0.15, anchor = tk.CENTER)
        button1 = tk.Button(self, text = "Price Quotes",font=smallTitle,width=30,height=3,cursor="plus",relief=tk.RAISED,command=lambda: controller.show_frame(graph))
        button1.place(relx = 0.77,rely = 0.27, anchor =tk.CENTER)
        button2 = tk.Button(self,text="Sentiment Analysis",font=smallTitle,width=30,height=3,cursor="plus",relief=tk.RAISED,command=lambda: controller.show_frame(sentimentStat))
        button2.place(relx = 0.77,rely = 0.39,anchor=tk.CENTER)
        button3 = tk.Button(self,text="Actions",font=smallTitle,width=30,height=3,cursor="plus",relief=tk.RAISED,command=lambda:controller.show_frame(actions))
        button3.place(relx = 0.77, rely = 0.63,anchor=tk.CENTER)
        ## modify following #######
        button4 = tk.Button(self,text="Financials",font=smallTitle,width=30,height=3,cursor="plus",relief=tk.RAISED,command=lambda:controller.show_frame(financials))
        button4.place(relx = 0.77, rely = 0.51, anchor = tk.CENTER)
        button5 = tk.Button(self,text="View Portifolio",font=smallTitle,width=30,height=3,cursor="plus",relief=tk.RAISED,command=lambda:controller.show_frame(portfolio))
        button5.place(relx = 0.77, rely = 0.75, anchor = tk.CENTER)
        ##################
        button6 = tk.Button(self,text="Log out",font=smallTitle,width=30,height=3,cursor="plus",relief=tk.RAISED,command=lambda: controller.show_frame(initial))
        button6.place(relx = 0.77, rely = 0.87,anchor = tk.CENTER)

    def drawGraph(self):
        imagePath="temp/imageSet/image2.jpg"
        if not os.path.exists(imagePath):
            saveImage(self.imageURL,imagePath)
        content = Image.open(imagePath)
        ######## This line is inspired by https://www.daniweb.com/programming/software-development/threads/369823/resizing-image
        content = content.resize((680, 648), Image.ANTIALIAS)
        #######################################################################
        image = ImageTk.PhotoImage(content)
        imgLabel=tk.Label(self,image=image)
        imgLabel.image = image
        imgLabel.place(relx=-0.03,rely=0.1)



class errorPopup(tk.Toplevel):
    def __init__(self,message="404 Not Found. Re-enter?"):
        super().__init__()
        self.answer=False
        self.message = message
        self.drawDialog()
    

    def drawDialog(self):
        tk.Label(self,text=self.message,font=medianTitle).grid(row=0,sticky="w")
        tk.Label(self).grid(row=1)
        tk.Button(self,text="Yes",command=self.yes,font=smallTitle,width=10).grid(row=2,sticky="w")
        tk.Button(self,text="No",command=self.no,font=smallTitle,width=10).grid(row=2,sticky="e")


    def yes(self):
        self.answer=True
        self.destroy()
    

    def no(self):
        self.destroy()



    
class sentimentStat(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent) 
        tk.Label(self,text="Sentiment Analysis",font=titleFont).place(relx=0.5,rely=0.02,anchor=tk.CENTER)
        tk.Button(self,text="set stock",font=smallTitle,width=20,height=2,relief=tk.SUNKEN,command=self.setUp).place(relx=1,rely=0.025,anchor="e")
        tk.Button(self,text = "back",font=smallTitle,width=20,height=2,relief=tk.SUNKEN,command=lambda:controller.show_frame(startPage)).place(relx=0,rely=0.025,anchor="w")
        self.bar = bar(self,0.5,0.06)
        self.bar.clear()


    def getInfo(self):

        def askInfo(self):
            popUp = getSentimentStock()
            self.wait_window(popUp)
            return popUp.info

        def error(self):
            popUp = errorPopup()
            self.wait_window(popUp)
            return popUp.answer

        info = askInfo(self)
        self.bar.start()
        if info == None: 
            self.bar.clear()
            return
        self.stock = info
        try:
            self.news = getHeadline(self.stock)
            if len(self.news) == 0 or self.stock=="": 1/0
        except:
            answer = error(self)
            if answer:
                self.getInfo()
            else:
                self.bar.clear()
                return
        else:
            self.distribution,self.rate = getStastics(self.news)
            self.coloredNews = RGB(self.news)
            self.linkedNews = newsURL(self.stock)
            self.urls = getURL(self.stock)
            self.distributions()
            self.drawPie()
            tk.Label(self,text=f'{self.stock} Headlines', font=medianTitle).place(relx=0.72,rely=0.1,anchor=tk.CENTER)
            canvas = self.drawSentiment()
            canvas.place(relx=0.48,rely=0.15)
            searchHist(self.stock)
            self.bar.complete()
            return


    def setUp(self):
        self.thread = threading.Thread(target=self.getInfo,args=(),daemon=True)
        self.thread.start()


    def distributions(self):
        count = 0
        for key in self.distribution:
            count += 1
            button = tk.Button(self,anchor="w",width = 20,height=2,text=f'  {key}: {self.distribution[key]}')#.grid(row=count)
            button.place(relx=0.23,rely=0.67+0.05*count,anchor=tk.CENTER)


    def drawPie(self):
        tk.Label(self,text=" ").grid(row=10)
        f = Figure(figsize=(5.5,4), dpi=100)
        a = f.add_subplot(111)
        f.suptitle("News Distribution")
        labels = []
        values = []
        explode = [0.1,0.1,0.1,0.1,0.2]
        for elem in self.distribution:
            labels.append(elem)
            values.append(self.distribution[elem])
        pieChart = a.pie(values, labels=labels, explode = explode,shadow=True)
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().place(relx = 0.025, rely = 0.129)
        #canvas.redraw()


    def drawSentiment(self):
        count = 0
        canvas = tk.Canvas(self,width=600,height=558)
        horizontalScroll = tk.Scrollbar(canvas)
        verticalScroll = tk.Scrollbar(canvas, orient="horizontal")
        news = tk.Listbox(canvas,width=67, height=33,yscrollcommand=verticalScroll.set,xscrollcommand= verticalScroll.set)
        for elem in self.news:
            count += 1
            url = self.linkedNews[elem]
            news.insert(tk.END,str(count) + ".  " + elem)
            news.insert(tk.END,"Link: " + url)
            news.insert(tk.END,"")
            color = rgbval(self.coloredNews[elem])
            news.itemconfig((count-1)*3,fg=color)
            #,command=lambda arg=url: self.openURL(arg)
            news.itemconfig((count-1)*3+1,fg=color)
        news.bind('<<ListboxSelect>>', self.openURL)
        news.place(relx=0,rely=0)
        return canvas


    #### Loosely adapted from https://stackoverflow.com/questions/6554805/getting-a-callback-when-a-tkinter-listbox-selection-is-changed
    def openURL(self,evt):
        w = evt.widget
        index = int(w.curselection()[0])
        new = w.get(index)
        if len(new) > 5:
            url = self.urls[index//3]
            webbrowser.open_new(url)

    
    


class getSentimentStock(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.drawDialog()


    def drawDialog(self):
        tk.Label(self,text="Choose your stock!",font=smallTitle).grid(row=0)
        tk.Label(self,text="Stock code",font=smallTitle).grid(row=1,sticky="w")
        self.stock = tk.StringVar()
        tk.Entry(self,textvariable=self.stock).grid(row=1,sticky="e")
        tk.Button(self,text="OK",font=smallTitle,width=10,command=self.OK).grid(row=2,sticky="w")
        tk.Button(self,text="Cancel",font=smallTitle,width=10,command=self.quit).grid(row=2,sticky="e")


    def OK(self):
        self.info = self.stock.get()
        self.destroy()
    

    def quit(self):
        self.info = None
        self.destroy()





class stockPopup(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.drawDialog()
    

    def drawDialog(self):
        tk.Label(self,text="Choose your stock!").grid(row=0)
        self.stock = tk.StringVar()
        self.stock.set("e.g. AAPL")
        self.start = tk.StringVar()
        self.start.set("YYYY-MM-DD")
        self.end = tk.StringVar()
        self.end.set("YYYY-MM-DD")
        self.volume = tk.BooleanVar()
        self.volume.set(False)
        self.movAvg5 = tk.BooleanVar()
        self.movAvg10 = tk.BooleanVar()
        self.movAvg25 = tk.BooleanVar()
        self.movAvg50 = tk.BooleanVar()

        tk.Label(self,text="Enter stock code").grid(row = 1,column = 0)
        tk.Entry(self,textvariable = self.stock).grid(row=1,column=1)
        tk.Label(self,text="Enter start date").grid(row = 2,column = 0)
        tk.Entry(self,textvariable = self.start).grid(row=2,column=1)
        tk.Label(self,text="Enter end date").grid(row = 3,column = 0)
        tk.Entry(self,textvariable = self.end).grid(row=3,column=1)

        tk.Label(self,text="Volume",anchor="w").grid(row=4,column=0,sticky="w")
        tk.Checkbutton(self,variable=self.volume,offvalue=False).grid(row=4,column=1,sticky="e")

        tk.Label(self,text="5 day moving average",anchor="w").grid(row=5,column=0,sticky="w")
        tk.Checkbutton(self,variable=self.movAvg5,offvalue=False).grid(row=5,column=1,sticky="e")
        tk.Label(self,text="10 day moving average",anchor="w").grid(row=6,column=0,sticky="w")
        tk.Checkbutton(self,variable=self.movAvg10,offvalue=False).grid(row=6,column=1,sticky="e")
        tk.Label(self,text="25 day moving average",anchor="w").grid(row=7,column=0,sticky="w")
        tk.Checkbutton(self,variable=self.movAvg25,offvalue=False).grid(row=7,column=1,sticky="e")
        tk.Label(self,text="50 day moving average",anchor="w").grid(row=8,column=0,sticky="w")
        tk.Checkbutton(self,variable=self.movAvg50,offvalue=False).grid(row=8,column=1,sticky="e")
        
        tk.Label(self).grid(row=9)
        tk.Button(self,text="OK",font=smallTitle,width=10,command=self.OK).grid(row=10,column=0)
        tk.Button(self,text="Cancel",font=smallTitle,width=10,command=self.quit).grid(row=10,column=1)


    def OK(self):
        self.info = [self.stock.get(),self.start.get(),self.end.get(),self.volume.get(),
                    [self.movAvg5.get(),self.movAvg10.get(),self.movAvg25.get(),self.movAvg50.get()]]
        self.destroy()
    

    def quit(self):
        self.info = None
        self.destroy()

        

class graph(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        tk.Label(self,text="Price Quotes",font=titleFont).place(relx=0.5,rely=0.03,anchor=tk.CENTER)
        back = tk.Button(self,text="Back",width=20,height=2,relief=tk.SUNKEN,command=lambda:controller.show_frame(startPage)) #.grid(row=1,sticky="w")
        setup = tk.Button(self,text="Set up",width=20,height=2,relief=tk.SUNKEN,command=self.enter)
        back.place(relx = 0, rely=0.025, anchor = "w")
        setup.place(relx=1,rely=0.025,anchor="e")
        self.stop = False
        self.bar = bar(self,0.5,0.06)
        self.bar.clear()


    def getInfo(self):

        def getQuotes(self):
            popUp = stockPopup()
            self.wait_window(popUp)
            return popUp.info

        def error(self):
            popUp = errorPopup()
            self.wait_window(popUp)
            return popUp.answer

        info = getQuotes(self)
        self.bar.start()
        self.stock = info[0]
        self.start = info[1]
        self.end = info[2]
        self.volume = info[3]
        self.movAvg = {5:info[4][0],10:info[4][1],25:info[4][2],50:info[4][3]}
        try:
            stock = yf.Ticker(self.stock)
            self.df = stock.history(start=self.start, end=self.end)
            if len(self.df) == 0: 1/0
            if existElem(self.movAvg,True):
                self.previousYr = str(int(self.start[0:4])-1) + self.start[4:]
                self.df1 = stock.history(start = self.previousYr, end = self.end)
                if len(self.df1) == 0: 1/0
            searchHist(self.stock)
            canvasBG = tk.Canvas(self,width=1000,height=700)
            canvasBG.create_rectangle(0,0,1100,700)
            canvasBG.place(relx=0.07,rely=0.1)
            canvas = self.canvasDraw()
            canvas.place(relx=0.07,rely=0.1)
            legend = self.legend()
            legend.place(relx=0.17,rely=0.95)
            self.bar.complete()
            
        except:
            answer = error(self)
            if answer:
                self.getInfo()
            else:
                self.stop = True
                self.bar.clear()

    
    def raiseError(self,df):
        if len(df)==0:
            answer = self.errorPopup()
            if answer:
                self.getInfo()
        return


    def enter(self):

        self.thread = threading.Thread(target=self.getInfo,args=(),daemon=True)
        self.thread.start()
    
    ## draw using matplotlib. Replaced with tk canvas. Kept as a interesting alternative
    def matDraw(self):
            f = Figure(figsize=(4,4), dpi=100)
            a = f.add_subplot(111)
            df=yf.download(self.stock,self.start,self.end)
            df.Close.plot(ax=a)
            canvas = FigureCanvasTkAgg(f, self)
            canvas.draw()
            ######## Adapted from https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/?completed=/styling-gui-bit-using-ttk/
            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            toolbar = NavigationToolbar2Tk(canvas, self)
            toolbar.update()
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            tk.Button(self,text="back",command=lambda:controller.show_frame(startPage)).pack()
            ##################################################################

    def canvasDraw(self):

        ############  Moving Average Setup ####################################
        MA_max = []
        MA_min = []
        for elem in self.movAvg:
            if self.movAvg[elem]:
                result = []
                for i in range(len(self.df1)):
                    if i < elem:
                        result.append(0)
                    else:
                        result.append(self.df1.Close.iloc[i-elem:i].mean())
                result = result[len(self.df1)-len(self.df):]
                self.df[f'Mov{elem}'] = pd.Series(result,index = self.df.index)
                MA_max.append(max(result))
                MA_min.append(min(result))

        ############# Parameter SetUp #######################################
        (width,height) = (1100,630)
        canvas = tk.Canvas(self,width=width,height=height)
        plotTitle = f'{self.stock.upper()}  Price  Chart  from  {self.start}  to  {self.end}'
        canvas.create_text(550,15, fill="purple",text=plotTitle, font=medianTitle, anchor=tk.CENTER)
        (x1,y1,x0,y0) = (width-60,50,60,height-60)
        unitWidth,unitHeight = ((x1-x0)/4, (y0-y1)/4)
        dates = [str(elem)[:10] for elem in self.df.index]
        (minPrice,maxPrice) = (self.df.Low.min(),self.df.High.max())
        if len(MA_min)>0:
            minPrice = min(self.df.Low.min(),min(MA_min))
            maxPrice = max(self.df.High.max(),max(MA_max))
        (minVol,maxVol) = (self.df.Volume.min(),self.df.Volume.max())
        priceRange = maxPrice-minPrice
        volRange = maxVol - minVol
        barWidth = (x1-x0)/len(dates)
        effectiveY = (y0-y1)*0.75
        startY = y0-(y0-y1)*0.25

        ##################  Draw Axes  #####################################
        canvas.create_line(x0,y1,x0,y0)
        canvas.create_line(x0,y0,x1,y0)
        for i in range(0,4):
            canvas.create_line(x0+unitWidth*i,y0,x0+unitWidth*i-10,y0+10)
            label = dates[i*len(dates)//5]
            canvas.create_text(x0+unitWidth*i-5,y0+25,text=label,anchor="w")
        for i in range(0,4):
            canvas.create_line(x0-5,y1+unitHeight*i,x0,y1+unitHeight *i)
            canvas.create_text(x0-10,y1+unitHeight *i,text=str((maxPrice-priceRange/3*i)//0.1/10),
            anchor="e")

        ############### Draw price chart ########################################
        for i in range(len(dates)):
            lowY = (self.df.Low.iloc[i]-minPrice)/priceRange*(effectiveY)
            highY = (self.df.High.iloc[i]-minPrice)/priceRange*(effectiveY)
            closeY = (self.df.Close.iloc[i]-minPrice)/priceRange*(effectiveY)
            OpenY = (self.df.Open.iloc[i]-minPrice)/priceRange*(effectiveY)
            color = "green" if closeY>OpenY else "red"
            if self.volume:
                volY = (self.df.Volume.iloc[i]-minVol)/volRange*((y0-y1)*0.25)
                canvas.create_rectangle(x0+i*barWidth,y0-volY,x0+(i+1)*barWidth,y0,fill=color,outline="")
            Y0 = max(closeY, OpenY)
            Y1 = min(closeY, OpenY)
            canvas.create_line(x0+(i+0.5)*barWidth,startY-highY,x0+(i+0.5)*barWidth,startY-lowY,fill=color)
            canvas.create_rectangle(x0+i*barWidth,startY-Y0,x0+(i+1)*barWidth,startY-Y1,fill=color,outline="")

        ##################### Draw Moving Average ###############################
        for elem in self.movAvg:
            if self.movAvg[elem]:
                startIndex = len(self.df1) - len(self.df)
                if elem == 5:
                    coordinates = MovAvg(self.df.Mov5,startY,minPrice,priceRange,effectiveY,x0,barWidth)
                    color = "purple"
                elif elem == 10:
                    coordinates = MovAvg(self.df.Mov10,startY,minPrice,priceRange,effectiveY,x0,barWidth)
                    color = "orange"
                elif elem == 25:
                    coordinates = MovAvg(self.df.Mov25,startY,minPrice,priceRange,effectiveY,x0,barWidth)
                    color = "blue"
                elif elem == 50:
                    coordinates = MovAvg(self.df.Mov50,startY,minPrice,priceRange,effectiveY,x0,barWidth)
                    color ="dark blue"
                canvas.create_line(coordinates,smooth=True,fill=color)

        canvas.update_idletasks()
        return canvas
    #canvasDraw(self)
    #matDraw(self)

    def legend(self):
        canvas = tk.Canvas(self,width=800,height=30)
        i = 0
        interval = 200
        reference = {"purple":5,"orange":10,"blue":25,"dark blue":50}
        for elem in reference:
            canvas.create_rectangle(20+i*interval,5,40+i*interval,25,fill=elem)
            canvas.create_text(100+i*interval,15,text=f'{reference[elem]} day MA')
            i += 1
        return canvas



class actions(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.drawBasics()
        self.controller = self.controller
    

    def drawBasics(self):
        tk.Label(self,text="Construct your portfolio",font=titleFont).place(relx=0.5,rely=0.03,anchor=tk.CENTER)
        tk.Button(self,text="Back",font=smallTitle,width=20,height=2,relief=tk.SUNKEN,command=lambda:self.controller.show_frame(startPage)).place(relx=0,rely=0.025,anchor="w")
        tk.Button(self,text="Action",font=smallTitle,width=20,height=2,relief=tk.SUNKEN,command = self.action).place(relx=1,rely=0.025,anchor="e")


    def actPopUp(self):
        popup = actionPopup()
        self.wait_window(popup)
        return popup.info


    def action(self):
        info = self.actPopUp()
        self.username = parameters.user
        if info == None: return
        self.address = "temp/" + self.username
        if not os.path.exists(self.address):
            os.makedirs(self.address)
        file = open(self.address+"/actions", "a")
        result = self.modifyPortfolio(info[0],info[1].upper(),info[2])
        if result == "NegativeError":
            answer = self.negativeError()
            if answer:
                self.action()
        time = datetime.datetime.now()
        try:
            ##### This one line is closely adapted from http://theautomatic.net/2018/07/31/how-to-get-live-stock-prices-with-python/
            price = si.get_live_price(info[1]) // 0.01 /100
        except:
            answer = self.stockError()
            if answer:
                self.action()
        action = info[0] + " " + info[1] + " " + str(info[2])+ " " + str(time) + " " + str(price)
        file.write(action + "\n")
        file.close()
        #self.modifyPortfolio(info[0],info[1],info[2])
        self.drawUpdate()
    

    def negativeError(self):
        popUp = errorPopup(message="You cannot sell shares that you do not own!")
        self.wait_window(popUp)
        return popUp.answer
    

    def stockError(self):
        popUp = errorPopup(message="Cannot find such share!")
        self.wait_window(popUp)
        return popUp.answer


    def modifyPortfolio(self,action,stock,quantity):
        try: 
            unitPrice = float(si.get_live_price(stock))
            try: 
                price = round(unitPrice,2)
            except:
                price = unitPrice // 0.01 /100
            #price = float(si.get_live_price(stock) // 0.01 /100)
            if str(price) == "nan": 1/0
        except: return 
        path = self.address + "/portfolio"
        file = open(path, "a")
        file.close()
        content = open(path, "r").read().splitlines()
        portfolio = dict()
        for elem in content:
            info = elem.split(" ")
            portfolio[info[0]] = int(info[1])
        #print(int(portfolio.get(info[0],0)),int(quantity))
        if action == "Buy":
            portfolio[stock.upper()] = portfolio.get(stock,0) + quantity
        else:
            if int(portfolio.get(stock,0)) < int(quantity):
                return "NegativeError"
            elif int(portfolio.get(stock,0)) == int(quantity):
                del portfolio[stock] 
            else:
                portfolio[stock] = portfolio.get(stock,0) - quantity
        self.profitMeasure(action,price,quantity)
        #portfolio[stock] = int(portfolio.get(stock,0)) + quantity
        file = open(path, "w")
        for key in portfolio:
            file.write(key + " " + str(portfolio[key]))
            file.write("\n")
        file.close()
        searchHist(stock)
            
        
    def drawUpdate(self):
        self.actions = open(self.address+"/actions", "r").read().splitlines()
        actioncanvas = self.drawAction()
        tk.Label(self,text="Trading Histroy",font=titleFont).place(relx=0.23,rely=0.12)
        tk.Label(self,text="Recent Searches",font=titleFont).place(relx=0.735,rely=0.15,anchor=tk.CENTER)
        actioncanvas.place(relx = 0.05,rely = 0.2)
        preferCanvas = self.drawPreference()
        preferCanvas.place(relx = 0.6,rely = 0.2)


    def drawBG(self):
        canvas = tk.Canvas(self,width=800,height=400)
        canvas.create_rectangle(0,0,800,400,fill="white")
        return canvas


    def drawAction(self):
        canvas = tk.Canvas(self,width=500,height=600)
        canvas.configure(scrollregion=canvas.bbox("all"))
        horizontalScroll = tk.Scrollbar(canvas)
        verticalScroll = tk.Scrollbar(canvas)
        actions = tk.Listbox(canvas,width=70, height=30,yscrollcommand=verticalScroll.set,xscrollcommand= horizontalScroll.set)
        for elem in self.actions:
            line = self.sentence(elem)
            actions.insert(0,line)
            actions.insert(0,"")
        actions.pack(fill=tk.BOTH,expand=True)
        return canvas
    

    def profitMeasure(self,action,price,amount):
        path = self.address + "/account"
        if not os.path.exists(path):
            file = open(path,"w")
            file.write("0\n0")
            file.close()
        content = open(path,"r").read().splitlines()
        value = round(amount*price,2)
        if len(content) == 2:
            if action == "Sell":
                content[1] = str(float(content[1]) + value)
            elif action == "Buy":
                content[0] = str(float(content[0]) + value)
        else:
            if action == "Sell":
                content = [0,value]
            elif action == "Buy":
                content = [value,0]
        file = open(path,"w")
        file.write(str(content[0]) + "\n" + str(content[1]))
        file.close()




    def drawPreference(self):
        path = "temp/" + self.username + "/Hist"
        content = open(path,"r").read().splitlines()
        result = []
        for line in content:
            elems = line.split(" ")
            result.append([int(elems[1]),elems[0]])
        result = sorted(result)[::-1]
        for i in range(len(result)):
            result[i][0] = str(result[i][0]) 
        canvas = tk.Canvas(self)
        horizontalScroll = tk.Scrollbar(canvas)
        verticalScroll = tk.Scrollbar(canvas)
        listBox = tk.Listbox(canvas,width=40, height=30,yscrollcommand=verticalScroll.set,xscrollcommand= horizontalScroll.set)
        order = 1
        maxLen = 50
        for stock in result:
            spaceNeeded = maxLen - len(str(order)) - 2 - len(stock[1]) - len(stock[0])
            sentence = "  " + str(order) + ". " + stock[1] + " "*spaceNeeded + stock[0] + "  search(es)"
            listBox.insert(tk.END, " ")
            listBox.insert(tk.END, sentence)
            order += 1
        listBox.pack(fill=tk.BOTH,expand=True)
        return canvas




    def sentence(self,line):
        result = "  User " + self.username + " "
        param = line.split(" ")
        result += " " + param[0].lower() + "s" + " "
        result += param[2] + " " + param[1].upper() + " shares " + "at " + param[3] + " "
        result += param[4][:param[4].find(".")]
        result += ". " + "Price: $" + param[-1] + " per share"
        return result



class portfolio(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        tk.Button(self,text="Back", font=smallTitle,width=20,height=2,relief=tk.SUNKEN,command = lambda: self.controller.show_frame(startPage)).place(relx=0,rely=0.025,anchor="w")
        tk.Button(self,text="Refresh", font=smallTitle,width=20,height=2,command=self.reload).place(relx=1,rely=0.025,anchor="e")
        tk.Label(self,text="View your portfolio",font=titleFont).place(relx=0.5,rely=0.03,anchor=tk.CENTER)
        self.bar = bar(self,0.75,0.03)
        self.bar.clear()
        self.drawBasics()
    

    def reload(self):
        self.thread = threading.Thread(target=self.drawBasics,args=(),daemon=True)
        self.thread.start()


    def drawBasics(self):

        def randomColor():
            red = random.randint(1,255)
            green = random.randint(1,255)
            blue = random.randint(1,255)
            color = rgbval((red,green,blue))
            return color


        def getStock(self):
            self.username = parameters.user
            if not os.path.exists("temp/" + self.username):
                os.makedirs("temp/" + self.username)
            path = "temp/" + self.username + "/portfolio"
            file = open(path,"a")
            file.close()
            result = []
            content = open(path,"r").read().splitlines()
            for line in content:
                info = line.split(" ")
                result.append((info[0],info[1]))
            result.sort()
            return result


        def reFresh(self):
            self.stocks = getStock(self)
    

        def getPortfolioValue(portfolio):
            result = 0
            for stock in portfolio:
                name = stock[0]
                amount = stock[1]
                value = si.get_live_price(name)*int(amount)
                result += round(value,2)
            return result
        

        def getDistribution(portfolio,value):
            result = dict()
            for stock in portfolio:
                name = stock[0]
                amount = stock[1]
                totalVal = si.get_live_price(name)*int(amount)/value
                result[name] = round(totalVal,4)

            return result


        def drawPortfolio(self):
            canvas = tk.Canvas(self)
            listBox = tk.Listbox(canvas)
            canvas.configure(scrollregion=canvas.bbox("all"))
            verticalScroll = tk.Scrollbar(canvas)
            horizontalScroll = tk.Scrollbar(canvas)
            maxLength = 50
            stocks = tk.Listbox(canvas,width=30, height=30,yscrollcommand=verticalScroll.set,xscrollcommand= horizontalScroll.set)
            for elem in self.stocks:
                spaceNeeded = maxLength - len(elem[0]) - len(elem[1])
                line = elem[0] + " "*spaceNeeded + elem[1]
                stocks.insert(tk.END, line)
                stocks.insert(tk.END," ")
            stocks.pack()
            return canvas

        def drawPie(self):
            canvas = tk.Canvas(self, width=600, height=400)
            prevAngle = 0
            self.colors = []
            unitLen = min(200/(len(self.distribution)+1),20)
            i = 0
            for key in self.distribution:
                angle = self.distribution[key]*360
                color = randomColor()
                while color in self.colors:
                    color = randomColor()
                self.colors.append(color)
                if len(self.distribution) == 1:
                    canvas.create_oval(20,20,380,380,fill=color)
                else:
                    canvas.create_arc(20,20,380,380,start=prevAngle,extent=angle,fill=color)
                canvas.create_rectangle(400,(i)*unitLen,400+unitLen,(1+i)*unitLen,fill=color)
                percentage = round(self.distribution[key]*100,2)
                canvas.create_text(450+unitLen,(2*i+1)/2*unitLen,text=f'{key}: {percentage}%')
                prevAngle = prevAngle + angle
                i += 2
            return canvas

        def drawStat(self):
            profitPath = "temp/" + self.username + "/account"
            if not os.path.exists(profitPath):
                file = open(profitPath,"w")
                file.write("0\n0")
                file.close()
            (self.liability,self.asset) = open(profitPath,"r").read().splitlines()
            if self.liability != "0":
                self.returnRatio = ((self.portfolioVal + float(self.asset))/float(self.liability) - 1)*100
                self.returnRatio = format(self.returnRatio,"2f")
                self.profit = self.portfolioVal + float(self.asset) - float(self.liability)
                self.profit = format(self.profit,"2f")
            else:
                self.returnRatio = 0
                self.profit = 0
            canvas = tk.Canvas(self, width=700, height = 250)
            canvas.create_text(350,30,text="Portfolio Statistics",font=medianTitle,anchor="center")
            canvas.create_text(20,90,text="Profit: ", font=smallTitle,anchor="w")
            canvas.create_text(700,90,text=f'$ {self.profit}',font=smallTitle,anchor="e")
            canvas.create_text(20,140,text="Returns Ratio: ", font=smallTitle,anchor="w")
            canvas.create_text(700,140,text=f'{self.returnRatio} %',font=smallTitle,anchor="e")
            canvas.create_text(20,190,text="Portfolio Value: ", font=smallTitle,anchor="w")
            canvas.create_text(700,190,text=f'$ {format(self.portfolioVal,"2f")}',font=smallTitle,anchor="e")
            return canvas

        self.bar.start()
        reFresh(self)
        self.portfolioVal = getPortfolioValue(self.stocks)
        self.distribution = getDistribution(self.stocks,self.portfolioVal)
        tk.Label(self,text="Portfolio",font=medianTitle).place(relx=0.17,rely=0.15,anchor=tk.CENTER)
        tk.Label(self,text="Portfolio Composition",font=medianTitle).place(relx=0.65,rely=0.42,anchor=tk.CENTER)
        canvas = drawPortfolio(self)
        canvas.place(relx=0.17,rely=0.55,anchor=tk.CENTER)
        pieChart = drawPie(self)
        pieChart.place(relx = 0.72, rely=0.72, anchor = tk.CENTER)
        statCanvas = drawStat(self)
        statCanvas.place(relx=0.38,rely=0.05)
        self.bar.complete()






class actionPopup(tk.Toplevel):
    def __init__(self):
        super().__init__()
        #self.geometry("700x200")
        self.drawDialog()
    
    def drawDialog(self):
        tk.Label(self,text=" "*50+"Buy or Sell Stocks!",font=titleFont).grid(row=0,sticky="w")
        #tk.Label(self,text="Action: ").grid(row=1,sticky="w")
        self.choice = ttk.Combobox(self,values=["Buy","Sell"])
        tk.Label(self,text="Action: ").grid(row=1,column=0)
        self.choice.grid(row=1,column=1)
        self.stock = tk.StringVar()
        self.quantity = tk.IntVar()
        tk.Label(self,text="stock: ",anchor="w").grid(row=2,column=0)
        tk.Entry(self,textvariable=self.stock).grid(row=2,column=1)
        tk.Label(self,text="Quantity: ").grid(row=3,column = 0)
        tk.Entry(self,textvariable=self.quantity).grid(row=3,column=1)
        tk.Button(self,text="OK",font=smallTitle,width=10,command=self.OK).grid(row=4,column=0)
        tk.Button(self,text="Quit",font=smallTitle,width=10,command=self.quit).grid(row=4,column=1)

    def OK(self):
        self.info = [self.choice.get(),self.stock.get(),self.quantity.get()]
        self.destroy()
    
    def quit(self):
        self.info = None
        self.destroy()



class financials(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.maximum = 100
        self.interval = 10
        tk.Button(self,text="Back", font=smallTitle,width=20,height=2,relief=tk.SUNKEN,command = lambda: self.controller.show_frame(startPage)).place(relx=0,rely=0.025,anchor="w")
        tk.Button(self,text="Select", font=smallTitle,width=20,height=2,command=self.drawBasics).place(relx=1,rely=0.025,anchor="e")
        tk.Label(self,text="View Corporate Financials",font=titleFont).place(relx=0.5,rely=0.03,anchor=tk.CENTER)
        self.bar = bar(self, 0.5, 0.06)
        self.bar.clear()


    def getInfo(self):

        def askStock(self):
            popUp = getSentimentStock()
            self.wait_window(popUp)
            return popUp.info
    
        def askTime(self):
            popUp = timePopup(self.times)
            self.wait_window(popUp)
            return popUp.info

        def error(self):
            popUp = errorPopup()
            self.wait_window(popUp)
            return popUp.answer

        def drawStatement(self,df,name):
            canvas = tk.Canvas(self,width=380,height=670)
            canvas.create_text(175,20,text=f'{self.stock} {name}',font=medianTitle,anchor="center")
            canvas.create_text(20,50,text="Item",anchor="w",font=smallTitle)
            canvas.create_text(360,50,text="Value / Million",anchor="e",font=smallTitle)
            canvas.create_line(20,63,360,63)
            start = 80
            for i in range(len(df)):
                name = df.index[i]
                try:
                    value = float(df.iloc[i])/1000000
                except:
                    value = str(df.iloc[i])
                #value = format(value)
                canvas.create_text(20,80+23*i,text=str(name).strip(),anchor="w",font=smallTitle)
                canvas.create_text(360,80+23*i,text=str(value),font=smallTitle,anchor="e")
            return canvas
            
        ########### get stock info ##########################
        self.stock = askStock(self)
        self.bar.start()
        if self.stock == None: 
            self.bar.clear()
            return None
        self.stockInfo = yf.Ticker(self.stock)
        try:
            self.balance_sheet = self.stockInfo.balance_sheet
            self.cash_flow = self.stockInfo.cashflow
            self.income = self.stockInfo.financials
            self.times = list(self.balance_sheet.columns.values) 
        except:
            answer = error(self)
            if answer:
                self.getInfo()
            else:
                self.bar.clear()
                return 

        ############# get time info #####################################
        self.time = askTime(self)
        if self.time == None:
            return None
        time = np.datetime64(self.time)
        try: 
            self.balance = self.balance_sheet[time]
            self.cash = self.cash_flow[time]
            self.revenue = self.income[time]
            self.balanceCanvas = drawStatement(self,self.balance,"Balance Sheet")
            self.cashCanvas = drawStatement(self,self.cash,"Cashflow Statement")
            self.incomeCanvas = drawStatement(self,self.revenue,"Income Statement")
            self.balanceCanvas.place(relx=0.05,rely=0.07)
            self.cashCanvas.place(relx=0.375,rely=0.07)
            self.incomeCanvas.place(relx=0.7,rely=0.07)
            searchHist(self.stock)
            self.bar.complete()
        except:
            answer = error(self)
            if answer:
                self.getInfo()
            else:
                self.bar.clear()

    def drawBasics(self):
        self.thread = threading.Thread(target=self.getInfo,args=(),daemon=True)
        self.thread.start()
         

## Loosely adpated from https://gist.github.com/MattWoodhead/c7c51cd2beaea33e1b8f5057f7a7d78a
# doesn't really work as a threading mechanics (I built my own) but kept as the main thread.           
class bar():
    def __init__(self, parent, x,y):
        self.maximum = 100
        self.interval = 20
        self.progressbar = ttk.Progressbar(parent, orient=tk.HORIZONTAL,
                                           mode="indeterminate",
                                           maximum=self.maximum,
                                           length = 200)
        self.progressbar.place(relx=x, rely=y,anchor=tk.CENTER)
        self.thread = threading.Thread(target=self.progressbar.start(self.interval),
                             args=(),daemon=True)
        self.thread.start()
    
    def stop(self):
        if not self.thread.isAlive():
            VALUE = self.progressbar["value"]
            self.progressbar.stop()
            self.progressbar["value"] = VALUE
    
    def start(self):
        #if not self.thread.isAlive():
        VALUE = self.progressbar["value"]
        self.progressbar.configure(mode="determinate",
                                    maximum=self.maximum,
                                    value=self.maximum/2)
        self.progressbar.start(self.interval)
        
    def clear(self):
        if not self.thread.isAlive():
            self.progressbar.stop()
            self.progressbar.configure(mode="determinate", value=0)
    
    def complete(self):
        if not self.thread.isAlive():
            self.progressbar.stop()
            self.progressbar.configure(mode="determinate",
                                       maximum=self.maximum,
                                       value=self.maximum)



class timePopup(tk.Toplevel):
    def __init__(self,times):
        super().__init__()
        self.times = times
        self.drawDialog()
    
    def drawDialog(self):
        tk.Label(self,text="Choose publification data",font=medianTitle).grid(row=0)
        tk.Label(self,text="Date: ",font=smallTitle).grid(row=1,column=0,sticky="w")
        self.choice = ttk.Combobox(self,value=self.times)
        self.choice.grid(row=1,column=1,sticky="e")
        tk.Button(self,text="OK",command=self.OK).grid(row=2,column=0)
        tk.Button(self,text="Quit",command=self.quit).grid(row=2,column=1)

    def OK(self):
        self.info = self.choice.get()
        self.destroy()
    
    def quit(self):
        self.info = None
        self.destroy()


#### store the paramter after login 
class parameters():
    user = "Tony"





################# Sentiment Analysis  ############################

def getEven(L):
    if len(L) == 2:
        return [L[1]]
    elif len(L) <= 2:
        return []
    else:
        return [L[1]] + getEven(L[2:])



def getNewResult(code):
    #https://finviz.com/quote.ashx?t=aapl
    url = "https://finviz.com/quote.ashx?t=" + code.lower() 
    page=requests.get(url)
    ### Bypasses the websites' security protection, credit: https://medium.com/@raiyanquaium/how-to-web-scrape-using-beautiful-soup-in-python-without-running-into-http-error-403-554875e5abed
    req = Request(url , headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    webText = BeautifulSoup(webpage,"html.parser")
    #########################################################################
    content = webText.findAll("tr",)
    result = []
    for c in content:
        if str(c).startswith('''<tr><td align="right"'''):
            result.append(str(c))
    newResult=[]
    for elem in result:
        for c in elem.split("</td><td "):
            newResult.append(c)
    return newResult



def getHeadline(code):
    newResult=getNewResult(code)
    finalResult = []
    for i in range(len(newResult)):
        start='''target="_blank">'''
        end = '''</a>'''
        elem = newResult[i][newResult[i].find(start)+len(start):newResult[i].find(end)]
        finalResult.append(elem)
    return getEven(finalResult)



def sentenceScore(sentence):
    result = dict()
    analyser = SentimentIntensityAnalyzer()
    for elem in sentence:
        score = analyser.polarity_scores(elem)
        result[elem] = (score["compound"])
    return result



def RGB(sentences):
    result = dict()
    scores = sentenceScore(sentences)
    for elem in sentences:
        score = int(abs(scores[elem])*255/2)
        if abs(scores[elem])<=0.05:
            result[elem] = (0,0,0)
        elif scores[elem]>0.05:
            result[elem] = (0,122+score,0)
        else:
            result[elem] = (122+score,0,0)
    return result



def getStastics(sentences):
    distribution = sentenceScore(sentences)
    result={"Positive":0,"Highly Positive":0,"Negative":0,"Highly Negative":0,
    "Neutral":0}
    rate=dict()
    for elem in distribution:
        score = distribution[elem]
        if score > 0.5:
            result["Highly Positive"] += 1
            rate[elem] = "Highly Positive"
        elif score < 0.5 and score > 0.05:
            result["Positive"] += 1
            rate[elem] = "Positive"
        elif score < -0.5:
            result["Highly Negative"] += 1
            rate[elem] = "Highly Negative"
        elif score > -0.5 and score < -0.05:
            result["Negative"] += 1
            rate[elem] = "Negative"
        else:
            result["Neutral"] += 1
            rate[elem] = "Neutral"
    return result,rate



def getURL(stock):
    newResult= getNewResult(stock)
    finalResult = []
    for elem in getEven(newResult):
        part=elem[elem.find("https"):elem.find('''" target="''')]
        finalResult.append(part)
    return finalResult



def newsURL(code):
    news = getHeadline(code)
    url = getURL(code)
    result = dict()
    for i in range(len(news)):
        result[news[i]] = url[i]
    return result 

################################################################################

top = myapp()
top.geometry("1280x720")
top.mainloop()