from django.urls import path

from dish import views


urlpatterns = [
    path('', views.CreateDishView.as_view()),
    path('names/', views.DishesNamesView.as_view()),
    path('dish_related_data/', views.DishesRelatedDataView.as_view()),
    path('menu/', views.CateringEstablishmentMenuView.as_view()),
    path('populate_order/', views.OrderPopulationView.as_view()),
    path('update_order/', views.OrderUpdateView.as_view()),
]
