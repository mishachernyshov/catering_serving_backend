from django.urls import path
from rest_framework.routers import DefaultRouter

from catering_establishment import views


root_router = DefaultRouter()
root_router.register(r'', views.CateringEstablishmentViewSet, basename='catering_establishment')

non_root_router = DefaultRouter()
non_root_router.register(r'booking', views.BookingViewSet, basename='booking')


urlpatterns = (
    [
        path('owned_by_user/', views.UserCateringEstablishmentsView.as_view()),
        path('catalog/', views.CateringEstablishmentCatalogView.as_view()),
        path('user_rating/', views.CateringEstablishmentUserRatingView.as_view()),
        path('feedbacks/', views.CateringEstablishmentFeedbacksView.as_view()),
        path('tables_list/', views.CateringEstablishmentTablesListView.as_view()),
        path('tables/', views.CateringEstablishmentsTablesView.as_view()),
        path('work_hours/', views.CateringEstablishmentWorkHoursView.as_view()),
        path('representation/', views.CateringEstablishmentsRepresentationView.as_view()),
        path('pay_for_booking/', views.BookingPaymentCreateView.as_view()),
    ]
    + non_root_router.urls
    + root_router.urls
)
