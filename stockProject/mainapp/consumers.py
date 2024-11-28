# chat/consumers.py
import json
import copy
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async, async_to_sync
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import StockDetail

class StockConsumer(AsyncWebsocketConsumer):

    @sync_to_async
    def addToCeleryBeat(self, stockpicker):
        try:
            task = PeriodicTask.objects.filter(name="every-10-seconds")
            if task.exists():
                task = task.first()
                args = json.loads(task.args)
                print(f"Existing args: {args}")
                if isinstance(args, list) and len(args) > 0:
                    current_stocks = args[0]
                    for x in stockpicker:
                        if x not in current_stocks:
                            current_stocks.append(x)
                    task.args = json.dumps([current_stocks])
                    task.save()
                    print(f"Updated args: {task.args}")
            else:
                schedule, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
                PeriodicTask.objects.create(
                    interval=schedule,
                    name="every-10-seconds",
                    task="mainapp.tasks.update_stock",
                    args=json.dumps([stockpicker]),
                )
                print(f"Created new periodic task with args: {stockpicker}")
        except Exception as e:
            print(f"Error in addToCeleryBeat: {e}")

    @sync_to_async
    def addToStockDetails(self, stockpicker):
        user = self.scope["user"]
        for i in stockpicker:
            stock, created = StockDetail.objects.get_or_create(stock = i)
            stock.user.add(user)


    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        #Parse queryString
        query_params = parse_qs(self.scope["query_string"].decode())

        print(query_params)
        stockpicker = query_params.get("stockpicker", [])
        if not stockpicker:
            print("No stockpicker parameter provided")
            return

        #Add to celery beat
        await self.addToCeleryBeat(stockpicker)

        #Store User to Model.py
        await self.addToStockDetails(stockpicker)

        await self.accept()

    @sync_to_async
    def disconnection(self):
        user = self.scope["user"]
        stocks = StockDetail.objects.filter(user__id = user.id)
        task = PeriodicTask.objects.get(name= "every-10-seconds")
        args = json.loads(task.args)
        args = args[0]
        
        for i in stocks:
            i.user.remove(user)
            if i.user.count() == 0:
                args.remove(i.stock)
                i.delete()
        
        if args == None:
            args = []

        if len(args) == 0:
            task.delete()
        else:
            task.args = json.dumps([args])
            task.save()


    async def disconnect(self, close_code):
        await self.disconnection()
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "send_update", "message": message}
        )
    
    @sync_to_async
    def selectUserStocks(self):
        user = self.scope["user"]
        user_stocks = user.stockdetail_set.values_list("stock", flat=True)
        return list(user_stocks)

    # Receive message from room group
    async def send_stock_update(self, event):
        message = event["message"]
        message = copy.copy(message)
        
        user_stocks = await self.selectUserStocks()

        keys = message.keys()
        for key in list(keys):
            if key in user_stocks:
                pass
            else:
                del message[key]


        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))