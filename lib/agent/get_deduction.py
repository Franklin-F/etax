import os
import json
import traceback
from functools import partial
from lib.logger import logger
from lib.days import *
from lib.attrdict import AttrDict
from lib.agent.bureau import Bureau, login_dppt_decorator, StopError, MonthInvalid, login_new_etax_decorator, login_new_dppt_decorator


class DeductionError(StopError):
    errcode = 120000
    errmsg = '获取已确认勾选发票信息失败'


class DeductionMonthInvalid(StopError):
    errcode = 120001
    errmsg = '当前税期不可选'


class DeductionUserError(StopError):
    errcode = 120002
    errmsg = '本功能仅提供给增值税一般纳税人或辅导期一般纳税人使用。'


class DeductionEtaxUserError(StopError):
    errcode = 120003
    errmsg = '您不是电子发票服务平台用票试点纳税人，请前往增值税发票综合服务平台办理相关业务！'


class GetDeduction(Bureau):

    @partial(login_new_etax_decorator, redirect_uri='https://dppt.tianjin.chinatax.gov.cn:8443/dedeuction-type-checked-business')
    def get_deduction(self, period=None):
        return [d.to_dict() for d in self.gen_deduction(period)]

    def check_deduction(self):
        query_path = '/ypfw/ypcommon/v1/ypnsrxx?'
        with self.page.expect_response(lambda response: query_path in response.url and response.status == 200) as response_info:
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            if data.Response.Data.ypsdnsrbz == 'N':
                self.wait(500)
                raise DeductionEtaxUserError

        query_path = '/ypfw/ckts/v1/dkgxincheck?'
        with self.page.expect_response(lambda response: query_path in response.url and response.status == 200) as response_info:
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            if 'Error' in data.Response:
                self.wait(500)
                if data.Response.Error.Message == '本功能仅提供给增值税一般纳税人或辅导期一般纳税人使用。':
                    raise DeductionUserError
                raise DeductionError(errmsg=data.Response.Error.Message)

    def gen_deduction(self, period=None):
        self.check_deduction()
        self.page.get_by_text("统计确认", exact=True).wait_for()
        self.wait(1000)
        self.screenshot('landing page')
        self.close_dppt_dialog()
        self.page.get_by_text("统计确认", exact=True).click()
        self.wait(3000)
        self.screenshot('click stat_confirm')
        self.close_dppt_dialog()
        self.screenshot('close dppt_dialog')
        self.page.get_by_text("查看历史确认信息").click()
        self.screenshot('click history deduction')

        to_month = get_month(period)
        try:
            self.select_month(to_month)
        except MonthInvalid:
            raise DeductionMonthInvalid
        self.wait(1000)
        self.screenshot('select month')

        vats = self.page.locator('//table//tr[td[1]/descendant-or-self::*[contains(text(),"本期认证相符的增值税专用发票（第2行）")]]/td[2]//span')
        nodata = self.page.locator('//table[thead/descendant-or-self::*[contains(text(),"进项抵扣类型")]]').get_by_text("暂无数据", exact=True).locator("visible=true")
        vats.or_(nodata).wait_for()

        if nodata.count():
            self.screenshot("no data", full_page=True)
            return None

        page_num = int(vats.inner_html())
        if not page_num:
            self.screenshot("no invoices", full_page=True)
            return

        self.screenshot('has invoices')
        query_path = '/ypfw/ytqr/v1/ytxxcx?'
        with self.page.expect_response(
            lambda response: query_path in response.url and response.status == 200
        ) as response_info:
            vats.click()
            self.screenshot('get deduction')
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            if 'Response' in data:
                yield from data.Response.Data.fpxx.List

        for i in range(500):
            self.page.locator("//div[contains(@class, 't-pagination__btn-next')]").wait_for()
            loc = self.page.locator("//div[contains(@class, 't-pagination__btn-next') and not(@disabled)]")
            has_next = loc.count()
            if not has_next:
                break
            loc.click()
            with self.page.expect_response(
                lambda response: query_path in response.url and response.status == 200
            ) as response_info:
                self.screenshot('get deduction')
                response = response_info.value
                data = response.json()
                data = AttrDict(data)
                if 'Response' in data:
                    yield from data.Response.Data.fpxx.List

    @partial(login_new_dppt_decorator, redirect_uri='https://dppt.tianjin.chinatax.gov.cn:8443/dedeuction-type-checked-business')
    def get_current_deduction(self):
        return [d.to_dict() for d in self.gen_current_deduction()]

    def gen_current_deduction(self):
        self.check_deduction()
        self.page.get_by_text("统计确认", exact=True).wait_for()
        self.wait(1000)
        self.screenshot('landing page')
        self.close_dppt_dialog()
        self.page.get_by_text("统计确认", exact=True).click()
        self.wait(3000)
        self.screenshot('click stat_confirm')
        self.close_dppt_dialog()
        self.wait(1000)
        self.screenshot('close dppt_dialog')

        if self.page.get_by_role("button").filter(has_text="申请统计").count():
            self.screenshot('confirm stage 1')
            return
        if self.page.locator("//div[contains(@class, 'stepsty')]//div[contains(@class, 'liitem')]//div[contains(@class, 'xhnum')]").count():
            self.screenshot('confirm stage 2')
            return
        loc = self.page.locator('//table//tr[td[1]/descendant-or-self::*[contains(text(),"本期认证相符的增值税专用发票（第2行）")]]/td[2]//span')
        page_num = int(loc.inner_html())
        if not page_num:
            self.screenshot('no invoice file')
            return

        loc.click()
        query_path = '/ypfw/ytqr/v1/ytxxcx?'
        with self.page.expect_response(
            lambda response: query_path in response.url and response.status == 200
        ) as response_info:
            self.screenshot('get deduction')
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            if 'Response' in data:
                yield from data.Response.Data.fpxx.List

        for i in range(500):
            self.page.locator("//div[contains(@class, 't-pagination__btn-next')]").wait_for()
            loc = self.page.locator("//div[contains(@class, 't-pagination__btn-next') and not(@disabled)]")
            has_next = loc.count()
            if not has_next:
                break
            loc.click()
            with self.page.expect_response(
                lambda response: query_path in response.url and response.status == 200
            ) as response_info:
                self.screenshot('get deduction')
                response = response_info.value
                data = response.json()
                data = AttrDict(data)
                if 'Response' in data:
                    yield from data.Response.Data.fpxx.List


if __name__ == '__main__':
    from lib.agent.shell import run, run_all
    run('拓顺物资（天津）有限公司', GetDeduction, GetDeduction.get_deduction, period='2024-05')
