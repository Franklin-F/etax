from lib.logger import logger
from lib.attrdict import AttrDict
from lib.agent.bureau import Bureau, login_etax_decorator, StopError


class FileVatError(StopError):
    errcode = 130000
    errmsg = '报税失败'


class FileVatValidateError(StopError):
    errcode = 130100
    errmsg = '账号报税前置检查不通过'

    # 1 jcfzc-nsrztValidator 纳税人状态为正常，通过
    # 2 ybnsrzgValidator 增值税一般纳税人资格监控通过
    # 3 cfsbValidator 您本属期已申报增值税，如需调整，请通过【申报更正与作废】进行处理。
    # 5 kxsfdjValidator 可办理身份监控通过
    # 7 fzjgwxsbValidator 分支机构无需申报监控通过
    # 9 hznsFzjgWsbValidator 汇总纳税的分支机构申报监控通过
    # 10 yqwsbValidator 前期未申报监控通过
    # 11 ybnsrCbsValidator 抄报税监控通过
    # 12 ybnsr-ysbqcValidator 应申报监控通过
    # 13 ybnsrJjdjbqValidator 增值税一般纳税人加计抵减政策纳税人归类信息通过
    # 14 ybnsrYjyhValidator 校验跨省分支机构是否维护地区
    # 15 jzzXgmValidator 一般纳税人季中转小规模监控通过

    # 51 xgmnsrzgValidator 增值税小规模纳税人资格监控监控通过
    # 52 xgm-ysbqcValidator 应申报监控通过
    # 53 xgmChfpValidator 增值税小规模红冲发票监控通过
    validators = {
        'jcfzc-nsrztValidator': 1,
        'ybnsrzgValidator': 2,
        'cfsbValidator': 3,
        'kxsfdjValidator': 5,
        'fzjgwxsbValidator': 7,
        'hznsFzjgWsbValidator': 9,
        'yqwsbValidator': 10,
        'ybnsrCbsValidator': 11,
        'ybnsr-ysbqcValidator': 12,
        'ybnsrJjdjbqValidator': 13,
        'ybnsrYjyhValidator': 14,
        'jzzXgmValidator': 15,
        'xgmnsrzgValidator': 51,
        'xgm-ysbqcValidator': 52,
        'xgmChfpValidator': 53,
    }

    def __init__(self, payload=None, errcode=None, errmsg=None):
        if not isinstance(payload, AttrDict):
            payload = AttrDict(payload)
        if errcode is None and errcode is None:
            try:
                errcode = self.errcode
                errmsg = self.errmsg
                for item in payload.Response.Data.Result.result:
                    if item.mandatoryFlag and not item.ruleResult:
                        errcode += self.validators.get(item.ruleId, 0)
                        errmsg = item.resultTip
                        break
            except:
                pass
        super().__init__(payload, errcode, errmsg)


class FileVatCheckError(StopError):
    errcode = 130200
    errmsg = '账号报税后置检查不通过'


class FileVatCheckSellError(StopError):
    errcode = 130201
    errmsg = '当期开具专用发票金额与申报销售额不符'


class FileVatCheckTaxError(StopError):
    errcode = 130202
    errmsg = '当期开具专用发票税额与申报税额不符'


class FileVAT(Bureau):

    # 简易确认式申报 https://etax.tianjin.chinatax.gov.cn:8443/xxbg/view/zhsffw/#/mixDeclare/nav
    # 一般人增值税及附加税申报 https://etax.tianjin.chinatax.gov.cn:8443/sbzx/view/lzsfjssb/#/declare/zzsybnsrsb?jyjkId=10
    # 小规模增值税及附加税申报 https://etax.tianjin.chinatax.gov.cn:8443/sbzx/view/lzsfjssb/#/declare/zzsxgmnsrsb?jyjkId=20
    @login_etax_decorator
    def file_vat(self, submit=True):

        normal_loc = self.page.locator("//div[contains(@class, 'rightMain')]//tbody/tr[td[1]/div[contains(text(),'增值税及附加税费申报（一般纳税人适用）')]]/td[3]")
        small_loc = self.page.locator("//div[contains(@class, 'rightMain')]//tbody/tr[td[1]/div[contains(text(),'增值税及附加税费申报（小规模纳税人）')]]/td[3]")
        table_loc = self.page.locator("//div[contains(@class, 'rightMain')]//tbody/tr[1]/td[1]").locator("visible=true")
        normal_loc.or_(small_loc).wait_for()
        self.screenshot('open home page')
        if small_loc.count():
            vat_url = 'https://etax.tianjin.chinatax.gov.cn:8443/sbzx/view/lzsfjssb/#/declare/zzsxgmnsrsb?jyjkId=20'
            check_url = '/sbzx/api/lzsfjssb/sffw/zzsxgmsb/zcsb/v1/sbbc?'
            query_url = '/sbzx/api/lzsfjssb/sffw/zzsxgmsb/zcsb/v1/sbjgcx?'
        else:
            vat_url = 'https://etax.tianjin.chinatax.gov.cn:8443/sbzx/view/lzsfjssb/#/declare/zzsybnsrsb?jyjkId=10'
            check_url = '/sbzx/api/lzsfjssb/sffw/zzsybnsrsb/sbbc/v1?'
            query_url = '/sbzx/api/lzsfjssb/sffw/zzsybnsrsb/sbjgcx/v1?'
        self.page.goto(vat_url)
        self.page.wait_for_load_state()

        cbs = self.page.locator('body > div:nth-child(13) > div.t-dialog__wrap > div > div')
        if cbs.count():
            cbs.locator('button').filter(has_text="确定").click()

        err = None
        url = '/sbzx/api/lzsfjssb/sffw/public/v1/qzjk?'
        with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_info:
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            for item in data.Response.Data.Result.result:
                if not item.ruleResult:
                    err = FileVatValidateError(data)
                    break

        fail_loc = self.page.get_by_text("检测不通过")
        submit_loc = self.page.get_by_role("button").filter(has_text="提交")
        submit_loc.or_(fail_loc).wait_for()
        if fail_loc.count():
            raise err

        # 这里可能有弹窗哦
        url = '/sbzx/api/lzsfjssb/sffw/sbzc/getSbsj?'
        with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_info:
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            if data.Response.Data.Result:
                self.confirm_dppt_dialog()

        self.close_cbs()
        self.screenshot_table()

        # 这里可能有弹窗哦
        url = '/sbzx/api/lzsfjssb/sffw/sbzc/getSbsj?'
        with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_info:
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            if data.Response.Data.Result:
                self.wait(500)
                self.confirm_dppt_dialog()

        self.page.wait_for_load_state()
        self.page.wait_for_selector('.g-layout')

        self.screenshot('prevat check ok')
        while self.page.get_by_text('加载中...').locator("visible=true").count():
            self.wait(500)
        self.screenshot('open vat return')
        self.close_dppt_dialog()
        self.screenshot('close dialog')

        submit_loc.click()
        self.confirm_captcha()
        if not submit:
            return

        with self.page.expect_response(
                lambda response: check_url in response.url and response.status == 200) as response_info:
            self.page.locator("//div[contains(@class, 't-dialog__footer')]//button").locator("visible=true").last.click()
            self.screenshot('click file vat button')
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            if 'mxjgList' not in data.Response.Data.Result:
                pass
            elif not data.Response.Data.Result.mxjgList:
                pass
            elif 'bdjgList' not in data.Response.Data.Result.mxjgList[0]:
                pass
            elif not data.Response.Data.Result.mxjgList[0].bdjgList:
                pass
            elif data.Response.Data.Result.mxjgList[0].bdjgList[0].bdxmDm == '011022001':
                raise FileVatCheckSellError(data)
            elif data.Response.Data.Result.mxjgList[0].bdjgList[0].bdxmDm == '011022002':
                raise FileVatCheckTaxError(data)
            else:
                raise FileVatCheckError(data)

        while True:
            with self.page.expect_response(
                    lambda response: query_url in response.url and response.status == 200) as response_info:
                logger.debug('get request')
                response = response_info.value
                data = response.json()
                data = AttrDict(data)
                if data.Response.Data.Result.sbztMs != '受理中':
                    break

        self.wait(2000)
        if data.Response.Data.Result.sbztMs == '申报成功':
            self.screenshot('file vat success')
            return data
        else:
            self.screenshot('file vat fail')
            raise FileVatError(data)

    def screenshot_table(self):
        # 点明细
        period_button = self.page.locator("#tax-period__operation > button:nth-child(1)")
        if period_button.count():
            period_button.click()

        # 检测是否loading
        loading_locator = self.page.locator('div.t-loading--center.t-size-m').filter(has_text="加载中")
        if loading_locator.count():
            loading_locator.element_handle().wait_for_element_state('hidden')

        # 截图明细
        self.page.wait_for_selector(".pl-16 > div:nth-child(1) > div:nth-child(1)")
        div_element = self.page.query_selector(".pl-16 > div:nth-child(1) > div:nth-child(1)")
        bounding_box = div_element.bounding_box()
        initial_viewport_size = self.page.viewport_size
        window_height = int(bounding_box['height']) + 300
        self.page.set_viewport_size({"width": initial_viewport_size['width'], "height": window_height})
        self.screenshot(name='vat detail', full_page=True)
        self.wait(500)
        # 修改原来的页面大小， 并刷新页面
        self.page.set_viewport_size({
            "width": initial_viewport_size['width'],
            "height": initial_viewport_size['height']
        })
        self.page.reload()

    def close_cbs(self):
        url = '/sbzx/api/lzsfjssb/sffw/zzsybnsrsb/jy/isCbs?'
        with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_info:
            response = response_info.value
            data = response.json()
            if data['Response']['Data']['Result'] == '02':
                dialog_loc = self.page.locator(".t-dialog.t-dialog--default.t-dialog__modal-info").locator("visible=true")
                dialog_count = dialog_loc.count()
                if dialog_count:
                    dialog_loc.locator("button").filter(has_text="确定").click()


if __name__ == '__main__':
    from lib.agent.shell import run, run_all
    run('天津稳胜物流有限公司', FileVAT, FileVAT.file_vat, submit=False)
    # run('天津市金禾物流有限公司', FileVAT, FileVAT.file_vat, submit=False)
    # run('天津亿之源贸易有限公司', FileVAT, FileVAT.file_vat, submit=False)
    # run_all(FileVAT, FileVAT.file_vat, submit=False, wait_cmd=False)
