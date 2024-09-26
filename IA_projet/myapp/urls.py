from django.urls import path
from .views import data_view, translate_summary, articles_view, home_view, index_view, run_python_function

urlpatterns = [
    path('api/data/', data_view, name='data_view'),
    path('api/translate_summary/<int:article_id>/', translate_summary, name='translate_summary'),
    path('articles/', articles_view, name='articles_view'),
    path('', home_view, name='home'),
    path('index/', index_view, name='index'),
    path('run_function/', run_python_function, name='run_function'),
]
