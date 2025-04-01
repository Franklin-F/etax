from rest_framework import serializers
from agent.models import *


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = ['id', 'name', 'credit_id', 'user_id', 'password', 'status', 'addtime']
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class LoginDetailSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = Login
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'status', 'result', 'addtime', 'errcode', 'errmsg',
            'auth_state'
        ]


class GetInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GetInvoice
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'mode',
            'begin_date', 'end_date', 'status', 'addtime',
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class GetInvoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GetInvoice
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'mode', 'begin_date', 'end_date',
            'status', 'result', 'addtime', 'errcode', 'errmsg',
        ]


class DownloadInvoiceSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = DownloadInvoice
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'mode',
            'begin_date', 'end_date', 'status', 'addtime','auth_state'
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class DownloadInvoiceDetailSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = DownloadInvoice
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'mode', 'begin_date', 'end_date',
            'status', 'result', 'addtime', 'errcode', 'errmsg', 'auth_state'
        ]


class GetInvoiceFileSerializer(serializers.ModelSerializer):
    begin_date = serializers.DateField(format='%Y-%m-%d')
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = GetInvoiceFile
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'mode',
            'begin_date', 'end_date', 'status', 'addtime', 'auth_state'
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class GetInvoiceFileDetailSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = GetInvoiceFile
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'mode', 'begin_date', 'end_date',
            'status', 'result', 'addtime', 'errcode', 'errmsg','auth_state'
        ]


class GetDeductionSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = GetDeduction
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'period', 'status', 'addtime', 'auth_state',
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class GetDeductionDetailSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = GetDeduction
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'period', 'status', 'result', 'addtime', 'errcode', 'errmsg','auth_state'
        ]


class GetCurrentDeductionSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = GetCurrentDeduction
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'status', 'addtime','auth_state'
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class GetCurrentDeductionDetailSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = GetCurrentDeduction
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'status', 'result', 'addtime', 'errcode', 'errmsg',
            'auth_state'
        ]


class FileVatSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = FileVat
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'status', 'addtime', 'auth_state',
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class FileVatDetailSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = FileVat
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'status', 'result', 'addtime', 'screenshot_url', 'errcode', 'errmsg',
            'vat_screenshots','auth_state'
        ]


class FileBsisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileBsis
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'status', 'addtime', 'sheet_data',
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class FileBsisDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileBsis
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'status', 'result', 'addtime', 'screenshot_url', 'errcode', 'errmsg',
        ]


class FileCitSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileCit
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'status', 'addtime', 'begin_staff', 'end_staff',
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class FileCitDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileCit
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'status', 'result', 'addtime', 'screenshot_url', 'errcode', 'errmsg',
        ]


class RevokeTaxSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = RevokeTax
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'status', 'addtime','auth_state'
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class RevokeTaxDetailSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = RevokeTax
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'status', 'result', 'addtime', 'screenshot_url', 'errcode', 'errmsg',
            'auth_state'
        ]


class InvoicingSerializer(serializers.ModelSerializer):
    auth_state = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = Invoicing
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'status', 'addtime', 'client_name', 'client_code', 'invoice_type', 'business_specific', 'diff_tax', 'reduced_tax', 'remark', 'invoice_data', 'wait_screenshots', 'invoicing_file', 'auth_state'
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class InvoicingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoicing
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'status', 'addtime', 'client_name', 'client_code', 'invoice_type', 'business_specific', 'diff_tax', 'reduced_tax', 'remark', 'invoice_data', 'wait_screenshots', 'invoicing_file'
        ]


class InvoiceQuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceQuota
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'status', 'addtime', 'begin_date', 'end_date'
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class InvoiceQuotaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceQuota
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'status', 'result', 'addtime', 'screenshot_url',
        ]


class StampDutySerializer(serializers.ModelSerializer):
    class Meta:
        model = StampDuty
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'password', 'status', 'addtime', 'begin_date', 'end_date', 'declaration_type', 'from_data', 'stamp_duty_file','is_zero_declaration'
        ]
        read_only_fields = ('status', 'addtime')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class StampDutyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StampDuty
        fields = [
            'id', 'name', 'credit_id', 'user_id', 'status', 'result', 'addtime', 'screenshot_url', 'declaration_type', 'from_data', 'stamp_duty_file','is_zero_declaration'
        ]
