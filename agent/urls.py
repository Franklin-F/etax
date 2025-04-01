"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'login', views.LoginViewSet)

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('login/<int:pk>/', views.LoginDetail.as_view()),
    path('get-invoice/', views.GetInvoiceView.as_view()),
    path('get-invoice/<int:pk>/', views.GetInvoiceDetail.as_view()),
    path('download-invoice/', views.DownloadInvoiceView.as_view()),
    path('download-invoice/<int:pk>/', views.DownloadInvoiceDetail.as_view()),
    path('get-invoice-file/', views.GetInvoiceFileView.as_view()),
    path('get-invoice-file/<int:pk>/', views.GetInvoiceFileDetail.as_view()),
    path('get-invoice-file/<int:pk>/download/', views.InvoiceFileDownload),
    path('get-deduction/', views.GetDeductionView.as_view()),
    path('get-deduction/<int:pk>/', views.GetDeductionDetail.as_view()),
    path('get-current-deduction/', views.GetCurrentDeductionView.as_view()),
    path('get-current-deduction/<int:pk>/', views.GetCurrentDeductionDetail.as_view()),
    path('file-vat/', views.FileVatView.as_view()),
    path('file-vat/<int:pk>/', views.FileVatDetail.as_view()),
    path('file-bsis/', views.FileBsisView.as_view()),
    path('file-bsis/<int:pk>/', views.FileBsisDetail.as_view()),
    path('file-cit/', views.FileCitView.as_view()),
    path('file-cit/<int:pk>/', views.FileCitDetail.as_view()),
    path('revoke-tax/', views.RevokeTaxView.as_view()),
    path('revoke-tax/<int:pk>/', views.RevokeTaxDetail.as_view()),
    path('invoicing/', views.InvoicingView.as_view()),
    path('invoicing/<int:pk>/', views.InvoicingDetail.as_view()),
    path('invoice-quota/', views.InvoiceQuotaView.as_view()),
    path('invoice-quota/<int:pk>/', views.InvoiceQuotaDetail.as_view()),
    path('stamp-duty/', views.StampDutyView.as_view()),
    path('stamp-duty/<int:pk>/', views.StampDutyDetail.as_view()),
    path('callback/', views.callback),
    path('v2/', include(router.urls)),
]
