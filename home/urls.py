from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home-index'),
    path('analyze-sentiment/', views.analyze_sentiment, name='analyze-sentiment'),
]


