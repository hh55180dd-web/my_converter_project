from django.urls import path
from .views import PDFToWordView

urlpatterns = [
    path('convert/', PDFToWordView.as_view(), name='pdf-to-word'),
]