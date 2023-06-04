from django.urls import path

from location import views


urlpatterns = [
    path('data/', views.LocationsDataView.as_view()),
]
