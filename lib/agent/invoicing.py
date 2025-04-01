import os
import re
import time
import json
import traceback
import django.dispatch
from lib.logger import logger
from lib.attrdict import AttrDict
from lib.agent.bureau import Bureau, login_etax_decorator, StopError


invoicing_wait_signal = django.dispatch.Signal()


class InvoicingParamError(StopError):
    errcode = 150201
    errmsg = '缺少开票关键参数，请检查接口'


class InvoicingBackError(StopError):
    errcode = 150202
    errmsg = '当前账号没有银行信息,请手动配置'


class BusinessSpecificParamError(StopError):
    errcode = 150203
    errmsg = '特定业务参数错误'


class DiffTaxParamError(StopError):
    errcode = 150204
    errmsg = '差额征税参数错误'


class ReducedTaxParamError(StopError):
    errcode = 150205
    errmsg = '减按征税参数错误'


class InvoicingStatusError(StopError):
    errcode = 150206
    errmsg = '非数电票试点纳税人，未核定数电票票种，不允许开票'


class InvoicingProductCodeError(StopError):
    errcode = 150207
    errmsg = '明细导入错误'


class InvoicingUserError(StopError):
    errcode = 150208
    errmsg = '用户扫码超时'


class InvoicingError(StopError):
    errcode = 150209
    errmsg = '税局报错信息'


class Invoicing(Bureau):

    def down_invicing_file(self):
        data = {}
        from django.conf import settings
        self.page.wait_for_selector('.qrcode-btn')
        with self.page.expect_download() as download_info:
            self.page.locator('.electronic-file > button:nth-child(1)').click()
            download = download_info.value
            file_path = f"{settings.OSS_DIR}/{self.credit_id}/invoicing/"
            download.save_as(file_path + download.suggested_filename)
            data['annex'] = file_path + download.suggested_filename
        self.page.locator('.qrcode-btn').click()
        self.page.wait_for_selector('.qrcode-box__codeImg')
        self.wait(500)
        self.screenshot(name="invoice qr code")
        return data

    @login_etax_decorator
    def invoicing(self, client_name,
                  client_code,
                  invoice_data,
                  invoice_type='ordinary_invoice',
                  business_specific='',
                  diff_tax='',
                  reduced_tax='', remark='', submit=True):
        if not client_code or not client_name or not invoice_data:
            raise InvoicingParamError()

        # 是否有蓝色发票报税资格
        self.page.goto('https://dppt.tianjin.chinatax.gov.cn:8443/invoice-business')
        self.page.wait_for_selector('.page_app_list')
        if not self.page.locator('.page_app_item').filter(has_text="蓝字发票开具").count():
            raise InvoicingStatusError()

        # 选择普票和专票
        self.page.goto('https://dppt.tianjin.chinatax.gov.cn:8443/blue-invoice-makeout/invoice-makeout')
        self.page.wait_for_load_state()

        # 是否有银行账号
        url = 'https://dppt.tianjin.chinatax.gov.cn:8443/kpfw/hqnsrjcxx/v1/hqnsrjcxx'
        with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_info:
            tax_list_response = response_info.value.json()
            if not tax_list_response['Response']['Data']['YhxxList']:
                self.page.wait_for_selector('.t-button__text')
                self.page.locator('.t-button__text').filter(has_text="我知道了").click()
                self.page.locator("div").filter(has_text=re.compile(r"^销方开户银行是否展示$")).get_by_placeholder("请输入").fill('888888')
                seller_table = self.page.locator('.accordin-wrap').filter(has_text="销售方信息")
                seller_bank = seller_table.locator('.form-list-wrap__item').filter(has_text="银行账号")
                seller_bank.get_by_placeholder("请输入").fill('66666')

        self.page.wait_for_selector('.t-drawer__content-wrapper--top')
        self.page.locator('.t-form-item__fppzDm > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').click()
        if invoice_type == 'ordinary_invoice':
            self.page.locator('li.t-select-option:nth-child(2)').click()
        else:
            self.page.locator('li.t-select-option:nth-child(1)').click()

        # # 特定业务
        # if business_specific:
        #     self.page.locator('.t-form-item__tdyslxDm > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').click()
        #     business_specific_button = self.page.locator('body > div:nth-child(14) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > ul:nth-child(1) li').filter(has_text=business_specific)
        #     if business_specific_button.count():
        #         business_specific_button.click()
        #     else:
        #         raise BusinessSpecificParamError()
        #
        # # 差额
        # if diff_tax:
        #     self.page.locator('div.t-form-item__:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').click()
        #     diff_tax_button = self.page.locator('body > div:nth-child(15) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > ul:nth-child(1) li').filter(has_text=diff_tax)
        #     if diff_tax_button.count():
        #         diff_tax_button.click()
        #     else:
        #         raise DiffTaxParamError()
        #
        # # 减按征税
        # if reduced_tax:
        #     self.page.locator('div.t-form-item__:nth-child(5) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').click()
        #     reduced_tax_button = self.page.locator('body > div:nth-child(16) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > ul:nth-child(1) li').filter(has_text=reduced_tax)
        #     if reduced_tax_button.count():
        #         reduced_tax_button.click()
        #     else:
        #         raise ReducedTaxParamError()

        self.page.locator('div.t-drawer__footer:nth-child(3) > button:nth-child(1)').click()

        # 填写购买方信息
        purchaser_table = self.page.locator('.accordin-wrap').filter(has_text="购买方信息")
        purchaser_name = purchaser_table.locator('.form-list-wrap__item').filter(has_text="名称")
        purchaser_name.get_by_placeholder("请输入").fill(client_name)
        purchaser_code = purchaser_table.locator('.form-list-wrap__item').filter(has_text="统一社会信用代码/纳税人识别号")
        purchaser_code.get_by_placeholder("请输入").fill(client_code)

        # self.page.locator('.auto-complete__item').click()
        # 上传文件，开票明细
        self.page.locator('.operate-button-group__container > div:nth-child(1) > button:nth-child(3)').click()

        with self.page.expect_file_chooser() as fc_info:
            self.page.locator('.t-upload__trigger > button:nth-child(1)').click()
            file_chooser = fc_info.value
            import pandas as pd
            inovic_file_data = pd.DataFrame(json.loads(invoice_data))
            from django.conf import settings
            file_path = f"{settings.OSS_DIR}/{self.credit_id}/invoicing"
            file_name = f"{self.credit_id}_{int(time.time())}.xlsx"
            # 检查一下文件夹是否存在
            if not os.path.exists(file_path):
                os.makedirs(file_path)

            inovic_file_data.to_excel(file_path + '/' + file_name, index=False, startrow=3)
            time.sleep(0.5)
            file_chooser.set_files(file_path + '/' + file_name)

        url = 'https://dppt.tianjin.chinatax.gov.cn:8443/kpfw/excel/v1/importmx'
        errorlog = []
        with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_list:
            response_list = response_list.value
            tax_list_response = response_list.json()
            tax_list_data = AttrDict(tax_list_response)
        for info in tax_list_data.Response.Data:
            if info.dhsbyy != '' and info.xh != '1':
                errorlog.append({
                    'item_name': info.xmmc,
                    'error_info': info.dhsbyy,
                })

        if errorlog:
            raise InvoicingProductCodeError
        self.page.locator('.t-drawer.t-drawer--right.t-drawer--open .t-drawer__footer').locator('button').filter(has_text="确定").click()
        # 写个备注
        self.page.locator('.t-textarea__inner').fill(remark)
        # 截图预览票
        self.page.locator('.button-group_wrap > button:nth-child(2)').click()
        self.page.wait_for_selector('.t-dialog--center > div:nth-child(1)')

        div_element = self.page.query_selector(".t-dialog--center > div:nth-child(1)")
        bounding_box = div_element.bounding_box()
        initial_viewport_size = self.page.viewport_size
        window_height = int(bounding_box['height']) + 300
        self.page.set_viewport_size({"width": initial_viewport_size['width'], "height": window_height})
        invoice_preview_locator = self.page.locator('.t-dialog--center > div:nth-child(1)')
        self.screenshot(name="invoice preview", locator_obj=invoice_preview_locator)
        self.wait(200)
        self.page.locator('.t-dialog--center > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)').click()
        self.page.set_viewport_size({"width": initial_viewport_size['width'], "height": initial_viewport_size['height']})

        # 开始提交
        self.page.locator('.button-group_wrap > button:nth-child(3)').click()

        # 税率弹窗
        tax_rate_button = self.page.locator('.t-dialog.t-dialog--default.t-dialog__modal-default button').filter(has_text='继续开具')
        if tax_rate_button.count() and tax_rate_button.is_visible():
            tax_rate_button.click()

        # 当前未查询到购买方纳税人信息
        url = 'https://dppt.tianjin.chinatax.gov.cn:8443/kpfw/lzfpkj/v1/tyfpkj'
        with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_list:
            response_list = response_list.value
            invoicing_response = response_list.json()
            invoicing_response = AttrDict(invoicing_response)
            if not invoicing_response.Response.Error:
                # 已经验证过
                return self.down_invicing_file()

            if invoicing_response.Response.Error and invoicing_response.Response.Error.Code != 'GT400010129997':
                InvoicingError.errmsg = invoicing_response.Response.Error.Message
                raise InvoicingError

        self.page.wait_for_selector('#qrcode')
        loading_locator = self.page.locator("#qrcode > img")
        loading_locator.element_handle().wait_for_element_state('stable')

        locator_obj = self.page.locator('.t-dialog').filter(has_text="电子税务局APP扫脸认证")
        self.screenshot(name="get scan code",locator_obj=locator_obj)
        invoicing_wait_signal.send(self.__class__)

        # 状态监控
        success = False
        for i in range(60):
            url = 'https://dppt.tianjin.chinatax.gov.cn:8443/kpfw/slrz/v1/qrslrz'
            with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_info:
                response_info = response_info.value
                response_info = response_info.json()
            if int(response_info['Response']['Data']['Slzt']) == 2:
                success = True
                break
            if int(response_info['Response']['Data']['Slzt']) == 3:
                raise InvoicingUserError()
            logger.debug(f"{response_info['Response']['Data']['Slzt']} ====== {i}")

        # 下载pdf和截图二维码
        if success:
            # 认证通过
            pass_button = self.page.locator('.t-dialog.t-dialog--default.t-dialog__modal-info button').filter(has_text='我已知晓，继续开票')
            if pass_button.count():
                pass_button.click()
            return self.down_invicing_file()


if __name__ == '__main__':
    invoice_data = json.dumps([{
        "项目名称": "橡胶垫",
        "商品和服务税收分类编码": "1070599000000000000",
        "规格型号": "480*200*205mm",
        "单位": "件",
        "商品数量": 4,
        "商品单价": -1000,
        "金额": -4000,
        "税率": 0.13,
        "折扣金额": "",
        "优惠政策类型": ""},
    ], ensure_ascii=False)
    from lib.agent.shell import run, run_all
    run('涞水汇森劳务派遣有限公司天津分公司', Invoicing, Invoicing.invoicing,
        client_name='大连毅捷船舶技术服务有限公司',
        client_code='91210211728882595Q',
        invoice_type='no_ordinary_invoice',
        business_specific='',
        diff_tax='',
        reduced_tax='',
        invoice_data=invoice_data,
        submit=False,
    )
