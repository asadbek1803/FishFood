# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('shop/', views.shop_view, name='shop'),
    path('api/order/create/', views.create_order, name='create_order'),
    path('api/product/<int:product_id>/price/', views.get_product_price, name='get_product_price'),
    path("bot/webhook/", views.telegram_webhook, name="telegram_webhook"),
    path('admin/couriers/', views.courier_list, name='courier_list'),
    path('admin/couriers/create-token/', views.courier_create_token, name='courier_create_token'),
    path('admin/couriers/<int:courier_id>/', views.courier_detail, name='courier_detail'),
    path('admin/couriers/<int:courier_id>/update-status/', views.courier_update_status, name='courier_update_status'),
    path('admin/couriers/<int:courier_id>/delete/', views.courier_delete, name='courier_delete'),
    # ... boshqa url'lar
]