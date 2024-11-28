# StockScope

StockScope is a dynamic stock tracking web application that uses Django and WebSocket technologies to provide real-time stock updates. The application leverages Yahoo Finance APIs for stock data retrieval and presents the information in an intuitive tabular format using Bootstrap. The stock data is updated every 10 seconds using Celery and Redis for efficient task scheduling and background processing.


## Features
1. **Stock Picker**: Select stocks from the NIFTY 50 list and monitor their data.
2. **Real-Time Updates**: Get updated stock data every 10 seconds via WebSocket integration.
3. **Multi-Threaded Data Retrieval**: Uses threading to fetch data concurrently for faster updates.
4. **User Authentication**: Only authenticated users can access stock tracking functionalities.
5. **Celery & Redis Integration**: Background tasks to periodically fetch and update stock data.
6. **Intuitive UI**: Data presented in tabular format with Bootstrap for responsive design.

## Technologies Used
### Backend
1. **Django**: Web framework for building the backend logic.
2. **Yahoo Finance API**: For retrieving stock data.
3. **Celery**: Task scheduling for periodic updates.
4. **Redis**: Message broker for Celery.
### Frontend
1. **Bootstrap**: For responsive and visually appealing table layouts.
2. **WebSockets**: Real-time stock data updates using Django Channels.



## Installation
## Prerequisites
1. Python 3.8 or higher
2. Redis server

## Steps
1. Clone the repository:
```python
git clone https://github.com/amitm15/Realtime-Stock-Tracker-App.git
cd stockProject
```
2. Create a virtual environment and install dependencies:
```python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
3. Install Redis and start the server:
```python
sudo apt install redis
redis-server
```
4. Migrate the database:
```python
python manage.py makemigrations
python manage.py migrate
```
5. Run the Celery worker:
```python
celery -A stockProject.celery worker --pool=solo -l info
```
6. Run the Celery beat:
```python
celery -A stockProject beat -l INFO
```
7. Start the Django development server:
```python
python manage.py runserver
```


## Usage
1. Stock Picker
2. Log in to the application.(via django-admin)
3. Navigate to the Stock Picker page to select stocks from the NIFTY 50 list.
4. Submit your selection to start tracking.
5. Real-Time Updates
## Updates will appear on the Stock Tracker page, showing the latest stock information, including:
1. Open price
2. High price
3. Low price
4. Close price
5. Adjusted close price
6. Volume
