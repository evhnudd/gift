from django.conf import settings
from django.contrib import admin
from django.urls import include, path


admin.site.site_header = "Система учета подарков"
admin.site.site_title = "Учёт подарков"
admin.site.index_title = "Администрирование"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("gift_web.urls")),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
