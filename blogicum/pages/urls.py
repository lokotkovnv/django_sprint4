from django.urls import path

from pages.views import About, Rules

app_name = 'pages'

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.internal_server_error'


urlpatterns = [
    path('about/', About.as_view(), name='about'),
    path('rules/', Rules.as_view(), name='rules'),
]
