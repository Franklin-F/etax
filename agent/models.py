import base64
import datetime
import itertools
import json
import os.path
import random
import time
import traceback
import stringcase
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from encrypted_model_fields.fields import EncryptedCharField
from lib.logger import logger
from lib.property import attrs, flags
from lib.base import BaseModel
from lib.days import *
from agent.inner import crm
from .fields import MediumTextField

class BaseLogin(BaseModel):
    name = models.CharField(max_length=256)
    credit_id = models.CharField(max_length=20)
    user_id = models.CharField(max_length=20)
    password = EncryptedCharField(max_length=512)
    result = models.JSONField(blank=True, null=True)
    errcode = models.PositiveIntegerField(default=0)
    errmsg = models.CharField(max_length=512, default='')
    auth_state = MediumTextField(blank=True, null=True)

    process_times = attrs()
    priority = attrs()
    screenshots = attrs()


    PROCESS_NOTICE_LIMIT = 3

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['credit_id']),
            models.Index(fields=['user_id']),
        ]

    def __str__(self):
        return f'{self.classname} {self.id} {self.name}'

    @property
    def classname(self):
        return self.__class__.__name__

    @property
    def queuename(self):
        return self.classname.lower()

    @property
    def typename(self):
        return stringcase.snakecase(self.classname).replace('_', '-')

    def reprocess(self):
        self.status = self.STATUS_NEW
        self.process_times = 0
        self.save()
        self.enqueue()

    def get_priority(self):
        from lib.queue import PRIORITY_NORMAL
        return PRIORITY_NORMAL

    def trash(self):
        self.status = self.STATUS_DELETE
        self.save()

    def enqueue(self):
        from lib.queue import queues
        data = {'id': self.id}
        queue = getattr(queues, self.queuename)
        priority = self.get_priority()
        self.priority = priority
        self.save()
        queue.send(data, priority=priority)

    @property
    def screenshot_dir(self):
        from django.conf import settings
        return os.path.join(settings.PLAYWRIGHT_SCREENSHOT_DIR, self.typename, str(self.id))

    @property
    def download_dir(self):
        from django.conf import settings
        return os.path.join(settings.AGENT_DIR, self.typename, str(self.id))

    @property
    def screenshot_urls(self):
        from django.conf import settings
        arr = []
        if not self.screenshots:
            return arr
        for screenshot in self.screenshots:
            if settings.DEBUG:
                url = f'{settings.TEST_HOST}screenshot/{self.typename}/{self.id}/{screenshot}'
            else:
                url = f'{settings.PROD_HOST}screenshot/{self.typename}/{self.id}/{screenshot}'
            arr.append(url)
        return arr

    @property
    def screenshot_url(self):
        if not self.screenshot_urls:
            return None
        return self.screenshot_urls[-1]

    def save_screenshots(self, save=True):
        if os.path.isdir(self.screenshot_dir):
            screenshots = list(sorted(os.listdir(self.screenshot_dir)))
        else:
            screenshots = []
        self.screenshots = screenshots
        save and self.save()

    def process(self, force=False):
        if not force and self.status >= self.STATUS_DONE:
            return

        clss = [GetInvoiceFile, GetDeduction, GetCurrentDeduction, Login, FileVat, RevokeTax,Invoicing,InvoiceQuota]
        for cls in clss:
            if cls.objects.filter(user_id=self.user_id, status=cls.STATUS_DOING, id__ne=self.id).exists():
                time.sleep(random.random() * 3)
                self.reprocess()
                return
        self.status = self.STATUS_DOING
        process_times = self.process_times or 0
        self.process_times = process_times + 1
        self.save()

        if not force and self.process_times > self.PROCESS_NOTICE_LIMIT:
            from lib.notice import wecom
            msg = f'{self.id} {self.typename} {self.process_times} {self.name}'
            logger.warn(msg)
            # wecom.send_text(msg)
            if not force:
                self.trash()
                return

        from lib.agent.bureau import StopError
        try:
            result = self.process_agent()
            self.status = self.STATUS_DONE
            self.result = result
            self.save_screenshots(save=False)
            self.save()
        except StopError as err:
            logger.error(err)
            self.status = self.STATUS_FAIL
            self.result = err.payload
            self.errcode = err.errcode
            self.errmsg = err.errmsg
            self.save_screenshots(save=False)
            self.save()
        except Exception as err:
            logger.error(err)
            logger.error(traceback.format_exc())
            raise err
        self.callback()

    def process_agent(self):
        pass

    def get_data(self):
        return {}

    def wait_status(self,**kwargs):
        self.status = self.STATUS_WAIT

    def callback(self):
        headers = {
            'Tenant-Id': 1,
        }
        if self.status == self.STATUS_DONE:
            data = {
                'code': 200,
                'msg': '成功',
                'type': self.typename,
                'typeid': self.id,
                'data': self.get_data(),
            }
            crm.post('/api/smartaccount/taxApiCallBack', headers=headers, json=data)
        elif self.status == self.STATUS_FAIL:
            data = {
                'code': 500,
                'msg': '失败',
                'type': self.typename,
                'typeid': self.id,
                'data': self.get_data(),
            }
            crm.post('/api/smartaccount/taxApiCallBack', headers=headers, json=data)
        elif self.status == self.STATUS_WAIT:
            data = {
                'code': 400,
                'msg': '等待用户操作',
                'type': self.typename,
                'typeid': self.id,
                'data': self.get_data(),
            }
            crm.post('/api/smartaccount/taxApiCallBack', headers=headers, json=data)


class Login(BaseLogin):
    def process_agent(self):
        from lib.agent.bureau import Bureau as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir,
            download_dir=self.download_dir,
        )
        return agent.login_with_auth_state(auth_state=self.auth_state)

    def get_data(self):
        from .serializers import LoginDetailSerializer
        return LoginDetailSerializer(self).data

    def save_err(self):
        if self.status != self.STATUS_FAIL:
            return
        from lib.agent.bureau import LoginFailError
        err = LoginFailError(self.result)
        self.errcode = err.errcode
        self.errmsg = err.errmsg
        self.save()


class GetInvoice(BaseLogin):
    MODE_ALL = 'all'
    MODE_IN = 'in'
    MODE_OUT = 'out'

    MODES = {
        MODE_ALL: MODE_ALL,
        MODE_OUT: MODE_OUT,
        MODE_IN: MODE_IN,
    }

    mode = models.CharField(max_length=64, default=MODE_ALL, choices=MODES)
    begin_date = models.DateField()
    end_date = models.DateField()

    def get_priority(self):
        from lib.queue import PRIORITY_NORMAL, PRIORITY_LOW, PRIORITY_TRIVIAL
        the_date = self.end_date
        if isinstance(the_date, datetime.datetime):
            the_date = the_date.date()
        if the_date < get_delta_day(days=-180).date():
            return PRIORITY_TRIVIAL
        if the_date < get_delta_day(days=-60).date():
            return PRIORITY_LOW
        return PRIORITY_NORMAL

    def process_agent(self):
        from lib.agent.get_invoice import GetInvoice as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir,
            download_dir=self.download_dir,
        )
        return agent.get_invoice(self.mode, self.begin_date, self.end_date, auth_state=self.auth_state)

    def get_data(self):
        from .serializers import GetInvoiceDetailSerializer
        return GetInvoiceDetailSerializer(self).data


class DownloadInvoice(BaseLogin):
    MODE_ALL = 'all'
    MODE_IN = 'in'
    MODE_OUT = 'out'

    MODES = {
        MODE_ALL: MODE_ALL,
        MODE_OUT: MODE_OUT,
        MODE_IN: MODE_IN,
    }

    mode = models.CharField(max_length=64, default=MODE_ALL, choices=MODES)
    begin_date = models.DateField()
    end_date = models.DateField()

    def get_priority(self):
        from lib.queue import PRIORITY_NORMAL, PRIORITY_LOW, PRIORITY_TRIVIAL
        the_date = self.end_date
        if isinstance(the_date, datetime.datetime):
            the_date = the_date.date()
        if the_date < get_delta_day(days=-180).date():
            return PRIORITY_TRIVIAL
        if the_date < get_delta_day(days=-60).date():
            return PRIORITY_LOW
        return PRIORITY_NORMAL

    def process_agent(self):
        from lib.agent.get_invoice import GetInvoice as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir,
            download_dir=self.download_dir,
        )
        result = agent.download_invoice(self.mode, self.begin_date, self.end_date, auth_state=self.auth_state)
        for item in itertools.chain(result['in'], result['out']):
            if item["invoice_pdf"]:
                filepath = os.path.join(self.download_dir, item["invoice_pdf"])
                relpath = os.path.relpath(filepath, settings.OSS_DIR)
                relpath = relpath.replace('\\', '/')
                if settings.DEBUG:
                    url = f'{settings.TEST_HOST}oss/{relpath}'
                else:
                    url = f'{settings.PROD_HOST}oss/{relpath}'
                item['invoice_url'] = url
            else:
                item['invoice_url'] = None
        return result

    def get_data(self):
        from .serializers import DownloadInvoiceDetailSerializer
        return DownloadInvoiceDetailSerializer(self).data


class GetInvoiceFile(BaseLogin):
    MODE_ALL = 'all'
    MODE_IN = 'in'
    MODE_OUT = 'out'

    MODES = {
        MODE_ALL: MODE_ALL,
        MODE_OUT: MODE_OUT,
        MODE_IN: MODE_IN,
    }

    mode = models.CharField(max_length=64, default=MODE_ALL, choices=MODES)
    begin_date = models.DateField()
    end_date = models.DateField()

    def get_priority(self):
        from lib.queue import PRIORITY_NORMAL, PRIORITY_LOW, PRIORITY_TRIVIAL
        the_date = self.end_date
        if isinstance(the_date, datetime.datetime):
            the_date = the_date.date()
        if the_date < get_delta_day(days=-180).date():
            return PRIORITY_TRIVIAL
        if the_date < get_delta_day(days=-60).date():
            return PRIORITY_LOW
        return PRIORITY_NORMAL

    def process_agent(self):
        from lib.agent.get_invoice import GetInvoice as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir,
            download_dir=self.download_dir,
        )
        return agent.get_invoice_file(self.mode, self.begin_date, self.end_date)

    def get_file_content(self, type='in'):
        if self.status != self.STATUS_DONE:
            return None
        if not self.result:
            return None
        if type not in self.result:
            return None
        if not self.result[type]:
            return None
        return base64.b64decode(self.result[type].encode('ascii'))

    def get_data(self):
        from .serializers import GetInvoiceFileDetailSerializer
        return GetInvoiceFileDetailSerializer(self).data


class GetDeduction(BaseLogin):
    period = models.CharField(max_length=10, validators=[
        RegexValidator(
            regex='^2\d{3}-\d{2}$',
            message='Please input valid month like 2024-01',
        ),
    ])

    def get_priority(self):
        from lib.queue import PRIORITY_NORMAL, PRIORITY_LOW, PRIORITY_TRIVIAL
        the_date = get_month(self.period).date()
        if the_date < get_delta_day(days=-180).date():
            return PRIORITY_TRIVIAL
        if the_date < get_delta_day(days=-60).date():
            return PRIORITY_LOW
        return PRIORITY_NORMAL

    def process_agent(self):
        from lib.agent.get_deduction import GetDeduction as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir,
            download_dir=self.download_dir,
        )
        return agent.get_deduction(self.period, auth_state=self.auth_state)

    def get_data(self):
        from .serializers import GetDeductionDetailSerializer
        return GetDeductionDetailSerializer(self).data


class GetCurrentDeduction(BaseLogin):
    def process_agent(self):
        from lib.agent.get_deduction import GetDeduction as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir,
            download_dir=self.download_dir,
        )
        return agent.get_current_deduction(auth_state=self.auth_state)

    def get_data(self):
        from .serializers import GetCurrentDeductionDetailSerializer
        return GetCurrentDeductionDetailSerializer(self).data


class FileVat(BaseLogin):
    def process_agent(self):
        from lib.agent.file_vat import FileVAT as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir,
            download_dir=self.download_dir,
        )

        return agent.file_vat(auth_state=self.auth_state)

    @property
    def vat_screenshots(self):
        if not self.screenshot_urls:
            return []
        return [filename for filename in self.screenshot_urls if 'vat_detail' in filename]

    def get_data(self):
        from .serializers import FileVatDetailSerializer
        return FileVatDetailSerializer(self).data


class FileBsis(BaseLogin):
    sheet_data = models.JSONField(blank=True, null=True)

    def process_agent(self):
        from lib.agent.file_bsis import FileBSIS as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir,
            download_dir=self.download_dir,
        )
        return agent.file_bsis(self.sheet_data)

    def get_data(self):
        from .serializers import FileBsisDetailSerializer
        return FileBsisDetailSerializer(self).data

    def save_excel(self, download_dir=None):
        import pandas as pd

        if isinstance(self.sheet_data, str):
            data = json.loads(self.sheet_data)
        else:
            data = self.sheet_data
        download_dir = download_dir or '.'
        for name, sheet in data.items():
            pd_data = pd.DataFrame(sheet)
            xls_file = os.path.join(download_dir, f'{self.name}_{name}.xlsx')
            pd_data.to_excel(xls_file, index=False, header=False, sheet_name=name)


class FileCit(BaseLogin):
    begin_staff = models.PositiveIntegerField(default=0)
    end_staff = models.PositiveIntegerField(default=0)

    def process_agent(self):
        from lib.agent.file_cit import FileCIT as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir,
            download_dir=self.download_dir,
        )
        return agent.file_cit(self.begin_staff, self.end_staff)

    def get_data(self):
        from .serializers import FileCitDetailSerializer
        return FileCitDetailSerializer(self).data


class RevokeTax(BaseLogin):
    def process_agent(self):
        from lib.agent.revoke_tax import RevokeTax as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir
        )

        return agent.revoke_tax()

    def get_data(self):
        from .serializers import RevokeTaxDetailSerializer
        return RevokeTaxDetailSerializer(self).data


class Invoicing(BaseLogin):
    client_name = models.CharField(max_length=512, default='')
    client_code = models.CharField(max_length=512, default='')
    invoice_type = models.CharField(max_length=512, default='ordinary_invoice')
    business_specific = models.CharField(max_length=512, default='')
    diff_tax = models.CharField(max_length=512, default='')
    reduced_tax = models.CharField(max_length=512, default='')
    remark = models.CharField(max_length=512, default='')
    invoice_data = models.JSONField(blank=True, null=True)

    def process_agent(self):
        from lib.agent.invoicing import invoicing_wait_signal
        invoicing_wait_signal.connect(self.wait_status, weak=False)

        from lib.agent.invoicing import Invoicing as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir,
        )
        return agent.invoicing(client_name=self.client_name,
                               client_code=self.client_code,
                               invoice_type=self.invoice_type,
                               business_specific=self.business_specific,
                               diff_tax=self.diff_tax,
                               reduced_tax=self.reduced_tax,
                               invoice_data=self.invoice_data,
                               remark=self.remark,
                               submit=True,
                               auth_state=self.auth_state,
                               )

    def get_data(self):
        from .serializers import InvoicingSerializer
        return InvoicingSerializer(self).data

    @property
    def wait_screenshots(self):
        # 人脸识别二维码和预览开票
        result = {}
        for filename in self.screenshot_urls:
            if 'scan_code' in filename:
                result['scan_code'] = filename
            if 'invoice_preview' in filename:
                result['invoice_preview'] = filename
        return result

    @property
    def invoicing_file(self):
        # 发票二维码和发票pdf
        result = self.result
        for filename in self.screenshot_urls:
            if 'invoice_qr_code' in filename:
                result['qr_code'] = filename
        return result

    from django.dispatch import receiver

    def wait_status(self, **kwargs):
        """
        进入等待, 改变状态,保存截图,回调给erp
        """
        super().wait_status()
        self.save_screenshots()
        self.callback()


class InvoiceQuota(BaseLogin):
    begin_date = models.DateField()
    end_date = models.DateField()

    def process_agent(self):
        from lib.agent.invoice_quota import InvoiceQuota as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir
        )
        return agent.invoice_quota(begin_date=self.begin_date, end_date=self.end_date)

    def get_data(self):
        from .serializers import InvoiceQuotaSerializer
        return InvoiceQuotaSerializer(self).data


class StampDuty(BaseLogin):
    # 税款所属期起
    begin_date = models.DateField()
    # 税款所属期止
    end_date = models.DateField()
    # 申报类型
    declaration_type = models.CharField(max_length=512, default='11|正常申报')
    # 填报信息
    from_data = models.JSONField(blank=True, null=True)
    # 是否0申报
    is_zero_declaration = models.PositiveSmallIntegerField(default=0)
    def process_agent(self):
        from lib.agent.stamp_duty import StampDuty as Agent
        agent = Agent(
            name=self.name,
            credit_id=self.credit_id,
            user_id=self.user_id,
            password=self.password,
            screenshot_dir=self.screenshot_dir
        )
        return agent.stamp_duty(begin_date=self.begin_date,
                                end_date=self.end_date,
                                declaration_type=self.declaration_type,
                                stamp_duty_data=self.from_data,
                                is_zero_declaration=self.is_zero_declaration
                                )

    def get_data(self):
        from .serializers import StampDutySerializer
        return StampDutySerializer(self).data

    @property
    def stamp_duty_file(self):
        for filename in self.screenshot_urls:
            if 'stamp_duty_end' in filename:
                return filename
