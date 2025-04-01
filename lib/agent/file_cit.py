import json
from lib.logger import logger
from lib.attrdict import AttrDict, AttrList
from lib.agent.bureau import Bureau, login_etax_decorator, StopError


class FileCitError(StopError):
    errcode = 180000
    errmsg = '报税失败'


class FileCitValidateError(StopError):
    errcode = 180100
    errmsg = '账号报税前置检查不通过'

    # [
    #   {
    #     "xh": "1",
    #     "jkxmlxMc": "纳税人状态监控",
    #     "nsrztmc": "正常",
    #     "tsxx": "纳税人状态监控：校验通过。",
    #     "nsrztDm": "03",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "nsrzt"
    #   },
    #   {
    #     "xh": "2",
    #     "jkxmlxMc": "纳税人信用等级监控",
    #     "tsxx": "纳税人信用等级监控：校验通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "nsrxydj"
    #   },
    #   {
    #     "xh": "3",
    #     "jkxmlxMc": "纳税人身份等级监控",
    #     "tsxx": "纳税人身份等级监控：校验通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "nsrsfdj"
    #   },
    #   {
    #     "xh": "4",
    #     "jkxmlxMc": "",
    #     "tsxx": "课征主体类型监控：校验通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": ""
    #   },
    #   {
    #     "xh": "5",
    #     "jkxmlxMc": "",
    #     "tsxx": "登记注册类型监控：校验通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": ""
    #   },
    #   {
    #     "xh": "6",
    #     "jkxmlxMc": "居民企业监控",
    #     "tsxx": "居民企业监控：通过",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "jmqyjk"
    #   },
    #   {
    #     "xh": "7",
    #     "jkxmlxMc": "税费种认定监控",
    #     "tsxx": "税费种认定监控：通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "sfzrdjk"
    #   },
    #   {
    #     "xh": "8",
    #     "jkxmlxMc": "延期申报提醒监控",
    #     "tsxx": "延期申报提醒监控：通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "yqsbjk"
    #   },
    #   {
    #     "xh": "9",
    #     "jkxmlxMc": "财务报表是否报送监控",
    #     "tsxx": "财务报表是否报送监控：通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "cwbbbsjk"
    #   },
    #   {
    #     "xh": "10",
    #     "jkxmlxMc": "上期未申报监控",
    #     "tsxx": "上期未申报监控，通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "sqwsb"
    #   },
    #   {
    #     "xh": "11",
    #     "jkxmlxMc": "重复申报监控",
    #     "tsxx": "重复申报监控，通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "cfsb"
    #   },
    #   {
    #     "xh": "12",
    #     "jkxmlxMc": "逾期申报监控",
    #     "tsxx": "逾期申报：校验通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "yqsb"
    #   },
    #   {
    #     "xh": "13",
    #     "jkxmlxMc": "提前申报监控",
    #     "tsxx": "提前申报：校验通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "tslxBm": "tg",
    #     "jkxmlx": "tqsb"
    #   }
    # ]

    validators = {
        1: ['nsrzt', '纳税人状态'],
        2: ['nsrxydj', '纳税人信用等级'],
        3: ['nsrsfdj', '纳税人身份等级'],
        4: ['', '课征主体类型'],
        5: ['', '登记注册类型'],
        6: ['jmqyjk', '居民企业'],
        7: ['sfzrdjk', '税费种认定'],
        8: ['yqsbjk', '延期申报提醒'],
        9: ['cwbbbsjk', '财务报表是否报送'],
        10: ['sqwsb', '上期未申报'],
        11: ['cfsb', '重复申报'],
        12: ['yqsb', '逾期申报'],
        13: ['tqsb', '提前申报'],
    }

    def __init__(self, payload=None, errcode=None, errmsg=None):
        if not isinstance(payload, AttrDict):
            payload = AttrDict(payload)
        if errcode is None and errcode is None:
            try:
                errcode = self.errcode
                errmsg = self.errmsg
                body = AttrList(json.loads(payload.Response.Data.Body), AttrDict)
                for item in body:
                    if item.tslxBm != 'tg':
                        errcode += self.get_errnum(item.jkxmlx, item.jkxmlxMc)
                        errmsg = item.tsxx
                        break
            except:
                pass
        super().__init__(payload, errcode, errmsg)

    def get_errnum(self, jkxmlx, jkxmlxMc):
        for errnum, [type, keyword] in self.validators.items():
            if type and type == jkxmlx:
                return errnum
            if keyword and keyword in jkxmlxMc:
                return errnum
        return 0


class FileCIT(Bureau):

    def pre_check(self):
        url = '/sbzx/api/sdsfsgjssb/qysdssb/qysds_a_yjd/v1/verifyBegin'
        with self.page.expect_response(
                lambda response: url in response.url and response.status == 200) as response_info:
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            body = AttrList(json.loads(data.Response.Data.Body), AttrDict)
            for item in body:
                if item.tslxBm != 'tg':
                    return FileCitValidateError(data)

    def post_check(self):
        url = '/sbzx/api/sdsfsgjssb/qysdssb/qysds_a_yjd/v1/getSbResult'
        for i in range(60):
            with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_info:
                logger.debug('post check request')
                response = response_info.value
                data = response.json()
                data = AttrDict(data)
                body = AttrDict(json.loads(data.Response.Data.Body))
                if body.returnFlag == 'Y':
                    self.screenshot('file cit success')
                    return data
        self.screenshot('file cit fail')
        raise FileCitError(data)

    def fill_staff(self, begin_staff=None, end_staff=None):
        import re
        from playwright.sync_api import expect

        if begin_staff:
            begin_input = self.page.frame_locator("#frmFrame"). \
                frame_locator("#frmMain"). \
                frame_locator("#frmSheet"). \
                locator("//input[@ng-model='sbxx.qccyrs2']")
            expect(begin_input).to_have_value(re.compile(r"[0-9]+"))
            begin_input.fill(str(begin_staff))

        if end_staff:
            end_input = self.page.frame_locator("#frmFrame"). \
                frame_locator("#frmMain"). \
                frame_locator("#frmSheet"). \
                locator("//input[@ng-model='sbxx.qmcyrs2']")
            expect(end_input).to_have_value(re.compile(r"[0-9]+"))
            end_input.fill(str(end_staff))

    def confirm_submit(self):
        self.page.locator("//div[contains(@class, 't-dialog__footer')]//button").\
            filter(has_text="确定").\
            locator("visible=true").\
            click()

    @login_etax_decorator
    def file_cit(self, begin_staff=None, end_staff=None, submit=True):
        cit_url = 'https://etax.tianjin.chinatax.gov.cn:8443/sbzx/view/sdsfsgjssb/#/yyzx/qysds_a_yjd'
        self.wait()
        self.page.goto(cit_url)
        self.page.wait_for_load_state()

        if err := self.pre_check():
            self.page.get_by_text("检测不通过").locator("visible=true").wait_for()
            raise err

        submit_loc = self.page.get_by_role("button").filter(has_text="提交申报")
        self.screenshot('precit check ok')
        while self.page.get_by_text('加载中...').locator("visible=true").count():
            self.wait(500)
        self.screenshot('open cit return')
        self.close_dppt_dialog()
        self.screenshot('close dialog')
        self.fill_staff(begin_staff, end_staff)
        submit_loc.click()
        self.confirm_dppt_dialog()
        self.page.frame_locator("#frmFrame").frame_locator("#frmMain").get_by_text("提交申报", exact=True).click()

        self.confirm_captcha()
        if not submit:
            return
        self.confirm_submit()
        return self.post_check()


if __name__ == '__main__':
    from lib.agent.shell import run
    run('涞水汇森劳务派遣有限公司天津分公司', FileCIT, FileCIT.file_cit, begin_staff=8, end_staff=9, submit=False)
