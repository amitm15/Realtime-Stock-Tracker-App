from celery import shared_task
from yahoo_fin.stock_info import tickers_nifty50, get_data, get_quote_table
from io import StringIO 
from collections import OrderedDict
from threading import Thread
import queue
from channels.layers import get_channel_layer
import asyncio
import simplejson as js
from asgiref.sync import async_to_sync

# Fetch stock data (not a Celery task since it's used in threads)
def fetch_stock_data(q, stock):
    print(f"Fetching data for stock: {stock}")
    stock_data = get_data(stock).iloc[-1]
    stock_info = {
        'open': str(round(stock_data.open, 4)),
        'high': str(round(stock_data.high, 4)),
        'low': str(round(stock_data.low, 4)),
        'close': str(round(stock_data.close, 4)),
        'adjclose': str(round(stock_data.adjclose, 4)),
        'volume': str(int(stock_data.volume))
    }
    q.put({stock: stock_info})

# Celery task to update stock data
@shared_task
def update_stock(stockpicker):
    print(f"Updating stocks: {stockpicker}")
    data = {}
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

    #send data to group
    channel_layer = get_channel_layer()
    print(f"Sending stock updates: {data}")

    async_to_sync(channel_layer.group_send)(
        "track",  # Replace with your group name
        {
            "type": "send_stock_update",
            "message": data,
        }
    )

    return "Done"