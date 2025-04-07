import os
import math
import base64
from functools import partial
from lib.logger import logger
from lib.attrdict import AttrDict
from lib.days import *
from lib.agent.bureau import Bureau, login_dppt_decorator, login_new_etax_decorator, login_new_dppt_decorator


class GetInvoice(Bureau):

    @partial(login_new_dppt_decorator, redirect_uri='https://dppt.tianjin.chinatax.gov.cn:8443/invoice-query/invoice-query')
    def download_invoice(self, mode='all', begin_date=None, end_date=None):
        output = []
        if mode in ['all', 'out']:
            output = list(self.download_invoice_filedata(mode='out', begin_date=begin_date, end_date=end_date))
        if mode in ['all']:
            begin_date = None
            end_date = None
        input = []
        if mode in ['all', 'in']:
            input = list(self.download_invoice_filedata(mode='in', begin_date=begin_date, end_date=end_date))
        return {'out': output, 'in': input}

    @partial(login_new_etax_decorator, redirect_uri='https://dppt.tianjin.chinatax.gov.cn:8443/invoice-query/invoice-query')
    def get_invoice_file(self, mode='all', begin_date=None, end_date=None):
        logger.debug(f'{self} {mode} {begin_date} {end_date}')
        output = None
        if mode in ['all', 'out']:
            output = self.get_invoice_filedata(mode='out', begin_date=begin_date, end_date=end_date)
            output = base64.b64encode(output).decode('ascii') if output else None
        if mode in ['all']:
            begin_date = None
            end_date = None
        input = None
        if mode in ['all', 'in']:
            input = self.get_invoice_filedata(mode='in', begin_date=begin_date, end_date=end_date)
            input = base64.b64encode(input).decode('ascii') if input else None
        return {'out': output, 'in': input}

    def save_invoice_file(self, *args, out_file=None, in_file=None, save_dir=None, **kwargs):
        data = self.get_invoice_file(*args, **kwargs)
        save_dir = save_dir or os.getcwd()
        out_file = out_file or os.path.join(save_dir, f'{get_now_packstr()}_out.xlsx')
        in_file = in_file or os.path.join(save_dir, f'{get_now_packstr()}_in.xlsx')
        if data['out']:
            with open(out_file, 'wb+') as f:
                f.write(base64.b64decode(data['out'].encode('ascii')))
            logger.info(f'Save out invoice in {out_file}')
        else:
            logger.info(f'No out invoice')

        if data['in']:
            with open(in_file, 'wb+') as f:
                f.write(base64.b64decode(data['in'].encode('ascii')))
            logger.info(f'Save in invoice in {out_file}')
        else:
            logger.info(f'No in invoice')

    @partial(login_new_etax_decorator, redirect_uri='https://dppt.tianjin.chinatax.gov.cn:8443/invoice-query/invoice-query')
    def get_invoice(self, mode='all', begin_date=None, end_date=None):
        logger.debug(f'{self} {mode} {begin_date} {end_date}')
        output = []
        if mode in ['all', 'out']:
            for invoice in self.gen_invoice(mode='out', begin_date=begin_date, end_date=end_date):
                output.append(invoice.to_dict())
        if mode in ['all']:
            begin_date = None
            end_date = None
        input = []
        if mode in ['all', 'in']:
            for invoice in self.gen_invoice(mode='in', begin_date=begin_date, end_date=end_date):
                input.append(invoice.to_dict())
        return {'out': output, 'in': input}

    def input_query(self, mode='out', begin_date=None, end_date=None):
        self.page.get_by_role("button").filter(has_text="查询").wait_for()
        self.wait(1000)

        if mode == 'in':
            if self.page.locator("//div[contains(@class, 't-form-item__gjbq')]//input").input_value() != '取得发票':
                self.page.locator("//div[contains(@class, 't-form-item__gjbq')]//input").click()
                self.page.locator("//div[contains(@class, 't-select__dropdown')]//li").locator("visible=true").filter(has_text="取得发票").click()

        if mode == 'out':
            if self.page.locator("//div[contains(@class, 't-form-item__gjbq')]//input").input_value() != '开具发票':
                self.page.locator("//div[contains(@class, 't-form-item__gjbq')]//input").click()
                self.page.locator("//div[contains(@class, 't-select__dropdown')]//li").locator("visible=true").filter(has_text="开具发票").click()

        if begin_date:
            from_date = get_delta_day(days=-15)
            to_date = get_day(begin_date)
            selector = self.page.get_by_placeholder("开票日期起")
            self.select_date(from_date, to_date, selector)

        if end_date:
            from_date = get_delta_day(days=1)
            to_date = get_day(end_date)
            selector = self.page.get_by_placeholder("开票日期止")
            self.select_date(from_date, to_date, selector)

    def get_invoice_filedata(self, mode='out', begin_date=None, end_date=None):
        self.input_query(mode=mode, begin_date=begin_date, end_date=end_date)

        query_path = '/szzhzz/qlfpcx/v1/queryFpjcxx?'
        with self.page.expect_response(lambda response: query_path in response.url and response.status == 200) as response_info:
            self.page.get_by_role("button").filter(has_text="查询").click()
            self.screenshot('click invoice query')
        self.screenshot('invoice api success')

        export = self.page.get_by_text("导出", exact=True)
        nodata = self.page.get_by_text("暂无数据", exact=True)
        logger.debug('Wait for invoices query result')
        export.or_(nodata).wait_for()

        if nodata.count():
            self.screenshot("no invoices", full_page=True)
            return None

        self.screenshot('click export')
        export.click()
        with self.page.expect_download() as download_info:
            self.screenshot('click export_all')
            self.page.get_by_text("导出全部", exact=True).click()
        download = download_info.value
        filename = download.suggested_filename
        _, fileext = os.path.splitext(filename)
        import tempfile
        now = get_now_str('%Y%m%d%H%M%S')
        filepath = os.path.join(tempfile.gettempdir(), f'{now}_{self.user_id}_{mode}{fileext}')
        download.save_as(filepath)
        with open(filepath, 'rb') as f:
            filedata = f.read()
        return filedata

    def gen_invoice(self, mode='out', begin_date=None, end_date=None):
        # Invoice out:
        # {
        #   "Response": {
        #     "RequestId": "dcfcd78def466a8b",
        #     "Data": {
        #       "PageNumber": 1,
        #       "PageSize": 20,
        #       "Total": 26,
        #       "List": [
        #         {
        #           "Gjbq": "1",
        #           "Fphm": "24122000000008948856",
        #           "Zzfphm": "",
        #           "ZzfpDm": "",
        #           "FplyDm": "2",
        #           "FplxDm": "81",
        #           "FppzDm": "01",
        #           "FpztDm": "01",
        #           "Sflzfp": "Y",
        #           "Kpfnsrsbh": "91120116MAC213UY3F",
        #           "Xsfnsrsbh": "91120116MAC213UY3F",
        #           "Xsfmc": "天津一联通物流服务有限公司",
        #           "Gmfnsrsbh": "91120118MA07358G5Q",
        #           "Gmfmc": "天津众合赢顺货运代理有限公司",
        #           "Kprq": "2024-02-19 10:17:57",
        #           "Hjje": 7462.26,
        #           "Hjse": 447.74,
        #           "XsfssjswjgDm": "11200000000",
        #           "GmfssjswjgDm": "11200000000",
        #           "Gmfssjswjgmc": "国家税务总局天津市税务局",
        #           "FpkjfsDm": "1",
        #           "Kpr": "田慧慧",
        #           "Jshj": 7910,
        #           "Gmfzrrbz": "N",
        #           "Tdyslxmc": "",
        #           "Xsfssjswjgmc": "国家税务总局天津市税务局"
        #         }
        #       ]
        #     }
        #   }
        # }
        #
        # Invoice in:
        # {
        #   "Response": {
        #     "RequestId": "9b922ca1ef4366d6",
        #     "Data": {
        #       "PageNumber": 1,
        #       "PageSize": 20,
        #       "Total": 12,
        #       "List": [
        #         {
        #           "Gjbq": "2",
        #           "Fphm": "24122000000008920726",
        #           "Zzfphm": "",
        #           "ZzfpDm": "",
        #           "FplyDm": "2",
        #           "FplxDm": "82",
        #           "FppzDm": "02",
        #           "FpkjfxlxDm": "01",
        #           "FpztDm": "01",
        #           "Sflzfp": "Y",
        #           "Xsfnsrsbh": "9112011674136811XC",
        #           "Xsfmc": "天津市金世界酒店有限公司",
        #           "Gmfnsrsbh": "91120116MAC213UY3F",
        #           "Gmfmc": "天津一联通物流服务有限公司",
        #           "Kprq": "2024-02-18 20:19:55",
        #           "Hjje": 2830.19,
        #           "Hjse": 169.81,
        #           "XsfssjswjgDm": "11200000000",
        #           "GmfssjswjgDm": "11200000000",
        #           "Gmfssjswjgmc": "国家税务总局天津市税务局",
        #           "FpkjfsDm": "1",
        #           "Kpr": "朱聪慧",
        #           "Jshj": 3000,
        #           "Gmfzrrbz": "N",
        #           "Tdyslxmc": "",
        #           "Xsfssjswjgmc": "国家税务总局天津市税务局"
        #         }
        #       ]
        #     }
        #   }
        # }

        self.input_query(mode=mode, begin_date=begin_date, end_date=end_date)

        query_path = '/szzhzz/qlfpcx/v1/queryFpjcxx?'
        with self.page.expect_response(lambda response: query_path in response.url and response.status == 200) as response_info:
            self.page.get_by_role("button").filter(has_text="查询").click()
            self.screenshot('click invoice query')
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            yield from data['Response']['Data']['List']

        if not data.Response.Data.Total:
            return

        page_num = math.ceil(data.Response.Data.Total / data.Response.Data.PageSize)
        for num in range(2, page_num + 1):
            with self.page.expect_response(lambda response: query_path in response.url and response.status == 200) as response_info:
                self.page.locator("//div[contains(@class, 't-input-number')]//input").fill(str(num))
                self.page.locator("//div[contains(@class, 't-input-number')]//input").press("Enter")
                self.screenshot('get invoice')
                response = response_info.value
                data = response.json()
                data = AttrDict(data)
                yield from data['Response']['Data']['List']

    def download_invoice_filedata(self, mode='out', begin_date=None, end_date=None):
        self.input_query(mode=mode, begin_date=begin_date, end_date=end_date)

        query_path = '/szzhzz/qlfpcx/v1/queryFpjcxx?'
        with self.page.expect_response(
                lambda response: query_path in response.url and response.status == 200) as response_info:
            self.page.get_by_role("button").filter(has_text="查询").click()
            self.screenshot('click invoice query')
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            yield from self.gen_invoice_pdf(data)

        if not data.Response.Data.Total:
            return

        page_num = math.ceil(data.Response.Data.Total / data.Response.Data.PageSize)
        for num in range(2, page_num + 1):
            with self.page.expect_response(
                    lambda response: query_path in response.url and response.status == 200) as response_info:
                self.page.locator("//div[contains(@class, 't-input-number')]//input").fill(str(num))
                self.page.locator("//div[contains(@class, 't-input-number')]//input").press("Enter")
                self.screenshot('get invoice')
                response = response_info.value
                data = response.json()
                data = AttrDict(data)
                yield from self.gen_invoice_pdf(data)

    def gen_invoice_pdf(self, data):
        for item in data['Response']['Data']['List']:
            if 'Fphm' in item and item['Fphm'] and 'FplyDm' in item and item['FplyDm'] == '2':
                logger.debug(f"download invoice {item['Fphm']}")
                action_loc = self.page.locator(f"//div[contains(@class, 'invoiceQuery__table')]//table/tbody/tr[td[5]/descendant::*[contains(text(),'{item['Fphm']}')]]/td[last()]")
                action_loc.wait_for()
                if action_loc.get_by_text('下载', exact=True).count():
                    action_loc.get_by_text('下载').click()
                    pdf_name = self.get_invoice_pdf()
                    self.close_dppt_dialog()
                    item['invoice_pdf'] = pdf_name
                elif action_loc.get_by_text('交付', exact=True).count():
                    action_loc.get_by_text('交付').click()
                    pdf_name = self.get_invoice_pdf()
                    self.close_dppt_dialog()
                    item['invoice_pdf'] = pdf_name
                else:
                    item['invoice_pdf'] = None
            else:
                item['invoice_pdf'] = None
            yield item

    def get_invoice_pdf(self):
        with self.page.expect_download() as download_info:
            self.page.get_by_text('发票下载PDF').click()
            self.screenshot('click export')
        download = download_info.value
        filename = download.suggested_filename
        now_str = get_now().strftime('%Y%m%d%H%M%S%f')
        filename = f'{now_str}_{filename}'
        filepath = os.path.join(self.download_dir, filename)
        download.save_as(filepath)
        logger.info(f'download pdf {filepath}')
        return filename


if __name__ == '__main__':
    from lib.agent.shell import run, run_all
    run('拓顺物资（天津）有限公司', GetInvoice, GetInvoice.get_invoice, mode='all', begin_date='2024-02-01', end_date='2024-02-27')
    run('拓顺物资（天津）有限公司', GetInvoice, GetInvoice.download_invoice, mode='all', begin_date='2023-10-01', end_date='2024-04-29')
    run('拓顺物资（天津）有限公司', GetInvoice, GetInvoice.get_invoice_file, mode='all', begin_date='2024-02-02', end_date='2024-05-29')
    run('拓顺物资（天津）有限公司', GetInvoice, GetInvoice.save_invoice_file, mode='all', begin_date='2024-02-03', end_date='2024-06-29')
