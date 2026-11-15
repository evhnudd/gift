from django.urls import path

from . import views


app_name = "gift_web"

urlpatterns = [
    path("", views.index, name="index"),
    path("users/", views.user_list, name="user_list"),
    path("users/<int:user_id>/", views.user_detail, name="user_detail"),
    path("recipients/", views.recipient_list, name="recipient_list"),
    path(
        "recipients/<slug:slug>/",
        views.recipient_detail,
        name="recipient_detail",
    ),
    path("gifts/", views.gift_list, name="gift_list"),
    path("gifts/new/", views.gift_create, name="gift_create"),
    path("gifts/search/", views.gift_search, name="gift_search"),
    path("gifts/<int:gift_id>/", views.gift_detail, name="gift_detail"),
    path("gifts/<int:gift_id>/edit/", views.gift_edit, name="gift_edit"),
    path(
        "gifts/<int:gift_id>/cancel/",
        views.gift_cancel,
        name="gift_cancel",
    ),
    path("events/", views.event_list, name="event_list"),
    path(
        "events/need-gift/",
        views.events_need_gift,
        name="events_need_gift",
    ),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("statistics/", views.statistics, name="statistics"),
]
