import base64
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, permissions, viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from agent.serializers import *
from agent.models import *
from agent.renderers import CodeMsgRenderer


class BaseListCreateAPIView(generics.ListCreateAPIView):
    renderer_classes = [CodeMsgRenderer, BrowsableAPIRenderer]


class BaseRetrieveAPIView(generics.RetrieveAPIView):
    renderer_classes = [CodeMsgRenderer, BrowsableAPIRenderer]


class LoginViewSet(viewsets.ModelViewSet):
    name = 'login-viewset'
    queryset = Login.objects.all().order_by('id')
    serializer_class = LoginSerializer


class LoginView(BaseListCreateAPIView):
    name = 'login-view'
    queryset = Login.objects.order_by('id')
    serializer_class = LoginSerializer


class LoginDetail(BaseRetrieveAPIView):
    name = 'login-detail'
    queryset = Login.objects.order_by('id')
    serializer_class = LoginDetailSerializer


class GetInvoiceView(BaseListCreateAPIView):
    name = 'get-invoice-view'
    queryset = GetInvoice.objects.order_by('id')
    serializer_class = GetInvoiceSerializer


class GetInvoiceDetail(BaseRetrieveAPIView):
    name = 'get-invoice-detail'
    queryset = GetInvoice.objects.order_by('id')
    serializer_class = GetInvoiceDetailSerializer


class DownloadInvoiceView(BaseListCreateAPIView):
    name = 'download-invoice-view'
    queryset = DownloadInvoice.objects.order_by('id')
    serializer_class = DownloadInvoiceSerializer


class DownloadInvoiceDetail(BaseRetrieveAPIView):
    name = 'download-invoice-detail'
    queryset = DownloadInvoice.objects.order_by('id')
    serializer_class = DownloadInvoiceDetailSerializer


class GetInvoiceFileView(BaseListCreateAPIView):
    name = 'get-invoice-file-view'
    queryset = GetInvoiceFile.objects.order_by('id')
    serializer_class = GetInvoiceFileSerializer


class GetInvoiceFileDetail(BaseRetrieveAPIView):
    name = 'get-invoice-file-detail'
    queryset = GetInvoiceFile.objects.order_by('id')
    serializer_class = GetInvoiceFileDetailSerializer


class GetDeductionView(BaseListCreateAPIView):
    name = 'get-deduction-view'
    queryset = GetDeduction.objects.order_by('id')
    serializer_class = GetDeductionSerializer


class GetDeductionDetail(BaseRetrieveAPIView):
    name = 'get-deduction-detail'
    queryset = GetDeduction.objects.order_by('id')
    serializer_class = GetDeductionDetailSerializer


class GetCurrentDeductionView(BaseListCreateAPIView):
    name = 'get-current-deduction-view'
    queryset = GetCurrentDeduction.objects.order_by('id')
    serializer_class = GetCurrentDeductionSerializer


class GetCurrentDeductionDetail(BaseRetrieveAPIView):
    name = 'get-current-deduction-detail'
    queryset = GetCurrentDeduction.objects.order_by('id')
    serializer_class = GetCurrentDeductionDetailSerializer


class FileVatView(BaseListCreateAPIView):
    name = 'file-vat-view'
    queryset = FileVat.objects.order_by('id')
    serializer_class = FileVatSerializer


class FileVatDetail(BaseRetrieveAPIView):
    name = 'file-vat-detail'
    queryset = FileVat.objects.order_by('id')
    serializer_class = FileVatDetailSerializer


class FileBsisView(BaseListCreateAPIView):
    name = 'file-bsis-view'
    queryset = FileBsis.objects.order_by('id')
    serializer_class = FileBsisSerializer


class FileBsisDetail(BaseRetrieveAPIView):
    name = 'file-bsis-detail'
    queryset = FileBsis.objects.order_by('id')
    serializer_class = FileBsisDetailSerializer


class FileCitView(BaseListCreateAPIView):
    name = 'file-cit-view'
    queryset = FileCit.objects.order_by('id')
    serializer_class = FileCitSerializer


class FileCitDetail(BaseRetrieveAPIView):
    name = 'file-cit-detail'
    queryset = FileCit.objects.order_by('id')
    serializer_class = FileCitDetailSerializer


class RevokeTaxView(BaseListCreateAPIView):
    name = 'revoke-tax-view'
    queryset = RevokeTax.objects.order_by('id')
    serializer_class = RevokeTaxSerializer


class RevokeTaxDetail(BaseRetrieveAPIView):
    name = 'revoke-tax-detail'
    queryset = RevokeTax.objects.order_by('id')
    serializer_class = RevokeTaxDetailSerializer


class InvoicingView(BaseListCreateAPIView):
    name = 'invoicing-view'
    queryset = Invoicing.objects.order_by('id')
    serializer_class = InvoicingSerializer

class InvoicingDetail(BaseRetrieveAPIView):
    name = 'invoicing-detail'
    queryset = Invoicing.objects.order_by('id')
    serializer_class = InvoicingDetailSerializer


class InvoiceQuotaView(BaseListCreateAPIView):
    name = 'invoice-quota-view'
    queryset = InvoiceQuota.objects.order_by('id')
    serializer_class = InvoiceQuotaSerializer


class InvoiceQuotaDetail(BaseRetrieveAPIView):
    name = 'invoice-quota-detail'
    queryset = InvoiceQuota.objects.order_by('id')
    serializer_class = InvoiceQuotaDetailSerializer



class StampDutyView(BaseListCreateAPIView):
    name = 'stamp-duty-view'
    queryset = StampDuty.objects.order_by('id')
    serializer_class = StampDutySerializer


class StampDutyDetail(BaseRetrieveAPIView):
    name = 'stamp-duty-detail'
    queryset = StampDuty.objects.order_by('id')
    serializer_class = StampDutyDetailSerializer

@csrf_exempt
def callback(request):
    try:
        body = request.body.decode('utf8')
    except:
        body = None

    data = {
        'method': request.method,
        'headers': {key: val for key, val in request.headers.items()},
        'body': body,
        'body_base64': base64.b64encode(request.body).decode('ascii'),
    }
    return JsonResponse(data)


@csrf_exempt
def InvoiceFileDownload(request, pk):
    import io
    import zipfile
    import base64
    model = GetInvoiceFile.objects.get(pk=pk)

    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')
    filename = f'invoice-file-{model.id}'
    zip_file.mkdir(filename)
    if 'in' in model.result and model.result['in']:
        zip_file.writestr('in.xlsx', base64.b64decode(model.result['in'].encode('ascii')))
    if 'out' in model.result and model.result['out']:
        zip_file.writestr('out.xlsx', base64.b64decode(model.result['out'].encode('ascii')))
    zip_file.close()

    resp = HttpResponse(buffer.getvalue())
    resp['Content-Disposition'] = f'attachment; filename={filename}.zip'
    resp['Content-Type'] = 'application/zip'
    return resp
