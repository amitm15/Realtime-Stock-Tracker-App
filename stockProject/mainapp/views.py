from django.http import HttpResponse
from django.shortcuts import render
from yahoo_fin.stock_info import tickers_nifty50, get_data, get_quote_table
from io import StringIO 
from collections import OrderedDict
from threading import Thread
import queue
from asgiref.sync import sync_to_async

@sync_to_async
def checkAuthenticated(request):
    if not request.user.is_authenticated:
        return False
    else:
        return True

def stockRetriver(request):
    listOfstocks = tickers_nifty50(True)
    stocks = {}
    for stock in listOfstocks.index:
        stocks[StringIO(listOfstocks["Symbol"][stock]).read()]= (StringIO(listOfstocks["Company Name"][stock]).read())

    return render(request, 'mainapp/stockpicker.html', context={'stocks': OrderedDict(sorted(stocks.items()))})

# Function to be executed by each thread
def fetch_stock_data(q, stock):
    stock_data = get_data(stock).iloc[-1]
    if not stock_data.empty:
        context = {
            'open': str(round(stock_data.open, 4)),
            'high': str(round(stock_data.high, 4)),
            'low': str(round(stock_data.low, 4)),
            'close': str(round(stock_data.close, 4)),
            'adjclose': str(round(stock_data.adjclose, 4)),
            'volume': str(int(stock_data.volume))
        }
        q.put({stock: context})

async def stockTracker(request):
    is_login = await checkAuthenticated(request)
    if not is_login:
        return HttpResponse("You are not logged in!")
    stockpicker = request.GET.getlist('stockpicker')
    data = {}

    try:
        nthreads = len(stockpicker)
        threadList = []
        queueData = queue.Queue()
        for i in range(nthreads):
            thread = Thread(target=fetch_stock_data, args=(queueData, stockpicker[i]))
            threadList.append(thread)
            threadList[i].start()
        
        # Wait for all threads to complete
        for thread in threadList:
            thread.join()
        
        while not queueData.empty():
            data.update(queueData.get())

        # print(data)

    except:
        return "Something went wrong"
    
    return render(request, 'mainapp/stocktracker.html', context={"data": data, 'room_name': 'track'})