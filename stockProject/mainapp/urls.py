from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.stockRetriver, name="stockRetriver"),
    path("track/", views.stockTracker, name="stockTracker"),
]
