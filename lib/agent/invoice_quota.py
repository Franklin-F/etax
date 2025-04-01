from lib.agent.bureau import Bureau, login_etax_decorator


class InvoiceQuota(Bureau):

    @login_etax_decorator
    def invoice_quota(self, begin_date, end_date):
        self.page.goto('https://dppt.tianjin.chinatax.gov.cn:8443/Invoice-information-inquiry-statistics')
        self.page.locator('#parent').wait_for()
        self.page.evaluate(f"""() => {{ document.getElementById('parent').style.zIndex = 1 }}""")
        self.page.locator('.t-form__item').filter(has_text='发票来源').click()
        self.page.locator('.t-select-option').filter(has_text='全部').click()
        self.page.locator('.t-form__item').filter(has_text='票种').click()
        self.page.locator('.t-checkbox__label').filter(has_text='全选').click()
        begin_selector = self.page.locator('.t-form__item').filter(has_text='起始时间').locator('.t-date-picker')
        self.select_month(to_month=begin_date, date_picker=begin_selector)
        end_selector = self.page.locator('.t-form__item').filter(has_text='终止时间').locator('.t-date-picker')
        self.select_month(to_month=end_date, date_picker=end_selector)
        self.page.locator('.tdesign-demo-block-row div span').filter(has_text='查询').click()

        url = 'https://dppt.tianjin.chinatax.gov.cn:8443/szzhzz/FpzlcxtjController/v1/queryFpzltjxx'
        with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_list:
            response_list = response_list.value
            invoice_list_response = response_list.json()
            return invoice_list_response['Response']['Data']


if __name__ == '__main__':
    from lib.agent.shell import run, run_all
    run('涞水汇森劳务派遣有限公司天津分公司', InvoiceQuota, InvoiceQuota.invoice_quota, begin_date='2024-01', end_date='2024-03')
