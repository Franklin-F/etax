import os
import json
import traceback
from lib.logger import logger
from lib.attrdict import AttrDict, AttrList
from lib.agent.bureau import Bureau, login_etax_decorator, StopError


class FileBSISError(StopError):
    errcode = 170000
    errmsg = '财务报表申报失败'


class FileBSISDupError(StopError):
    errcode = 170001
    errmsg = '财务报表无法重复申报'


class FileBSISCheckError(StopError):
    errcode = 170002
    errmsg = '财务报表表格检查错误'


class FileBsisValidateError(StopError):
    errcode = 170100
    errmsg = '账号报税前置检查不通过'

    # [{
    #     "xh": 1,
    #     "jkxmlxMc": "纳税人状态监控",
    #     "tsxx": "纳税人状态监控：校验通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "jkxmlx": "nsrzt",
    #     "tslxBm": "tg"
    # }, {
    #     "xh": 2,
    #     "jkxmlxMc": "纳税人身份等级监控",
    #     "tsxx": "纳税人身份等级监控：校验通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "jkxmlx": "nsrsfdj",
    #     "tslxBm": "tg"
    # }, {
    #     "xh": 3,
    #     "jkxmlxMc": "财务备案监控",
    #     "tsxx": "有备案信息，通过校验。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "jkxmlx": "cwbajk",
    #     "tslxBm": "tg"
    # }, {
    #     "xh": 4,
    #     "jkxmlxMc": "纳税人信用等级监控",
    #     "tsxx": "纳税人信用等级监控：校验通过。",
    #     "urlBm": "",
    #     "anMc": "",
    #     "jkxmlx": "nsrxydj",
    #     "tslxBm": "tg"
    # }]

    validators = {
        1: ['nsrzt', '纳税人状态'],
        2: ['nsrsfdj', '纳税人身份等级'],
        3: ['cwbajk', '财务备案'],
        4: ['nsrxydj', '纳税人信用等级'],
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


class FileBSIS(Bureau):

    def pre_check(self):
        # {
        #     "allProcessTime": 249,
        #     "nsrdProcessTime": 243,
        #     "yfwjcptProcessTime": 238,
        #     "Response": {
        #         "processTime": 58,
        #         "RequestId": "cf1a431d7c634c48",
        #         "Data": {
        #             "BizCode": "00",
        #             "BizMsg": "",
        #             "Body": "[{\"xh\":1,\"jkxmlxMc\":\"纳税人状态监控\",\"tsxx\":\"纳税人状态监控：校验通过。\",\"urlBm\":\"\",\"anMc\":\"\",\"jkxmlx\":\"nsrzt\",\"tslxBm\":\"tg\"},{\"xh\":2,\"jkxmlxMc\":\"纳税人身份等级监控\",\"tsxx\":\"纳税人身份等级监控：校验通过。\",\"urlBm\":\"\",\"anMc\":\"\",\"jkxmlx\":\"nsrsfdj\",\"tslxBm\":\"tg\"},{\"xh\":3,\"jkxmlxMc\":\"财务备案监控\",\"tsxx\":\"有备案信息，通过校验。\",\"urlBm\":\"\",\"anMc\":\"\",\"jkxmlx\":\"cwbajk\",\"tslxBm\":\"tg\"},{\"xh\":4,\"jkxmlxMc\":\"纳税人信用等级监控\",\"tsxx\":\"纳税人信用等级监控：校验通过。\",\"urlBm\":\"\",\"anMc\":\"\",\"jkxmlx\":\"nsrxydj\",\"tslxBm\":\"tg\"}]"
        #         }
        #     }
        # }
        url = '/sbzx/api/sdsfsgjssb/qysdssb/cwbbbs/v1/verifyBegin'
        with self.page.expect_response(
                lambda response: url in response.url and response.status == 200) as response_info:
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            body = AttrList(json.loads(data.Response.Data.Body), AttrDict)
            for item in body:
                if item.tslxBm != 'tg':
                    raise FileBsisValidateError(data)

    def check_dup(self):
        #  {
        #      "allProcessTime": 210,
        #      "nsrdProcessTime": 203,
        #      "yfwjcptProcessTime": 198,
        #      "Response": {
        #          "processTime": 20,
        #          "RequestId": "8d98c24656a54290",
        #          "Data": {
        #              "BizCode": "00",
        #              "BizMsg": "",
        #              "Body": "{\"cfsbBz\":\"Y\",\"formData\":{\"cwbbbsjcsz\":{\"sksq\":\"\",\"bsqj\":\"03\",\"bszlDm\":\"ZLA0610216\",\"ybqyjrqyBz\":\"\",\"zlbszlDm\":\"ZL1001003\",\"kjzdzzDm\":\"102\",\"hyDm\":\"5265\",\"ywbm\":\"CWBB_XQYKJZZ\",\"bsqjs\":\"03,01\",\"qhqyBz\":\"N\",\"sssqz\":\"2024-06-30\",\"zlbsxlDm\":\"ZL1001003\",\"sssqq\":\"2024-04-01\",\"nbnf\":\"\"}}}"
        #          }
        #      }
        #  }
        url = '/sbzx/api/sdsfsgjssb/qysdssb/cwbbbs/v1/saveSetting'
        with self.page.expect_response(
                lambda response: url in response.url and response.status == 200) as response_info:
            response = response_info.value
            data = response.json()
            data = AttrDict(data)
            body = AttrDict(json.loads(data.Response.Data.Body))
            if body.cfsbBz == 'Y':
                raise FileBSISDupError(data)

    def check_table(self):
        self.page.get_by_role("button").filter(has_text="提交申报").wait_for()
        self.page.locator("//input")
        self.page.frame_locator("#frmFrame"). \
            frame_locator("#frmMain"). \
            frame_locator("#frmSheet"). \
            locator("//input").last.wait_for()
        # wait for another implementation
        self.wait(2000)
        error_inputs = self.page.frame_locator("#frmFrame"). \
            frame_locator("#frmMain"). \
            frame_locator("#frmSheet"). \
            locator("//input[contains(@tiptype, 'error')]")
        if not error_inputs.count():
            return
        error_message = error_inputs.first.get_attribute('_tips_title')
        if error_message:
            raise FileBSISCheckError(errmsg=error_message)

    @login_etax_decorator
    def file_bsis(self, sheet_data, submit=True):
        # file Balance Sheet & Income Statement
        self.page.goto('https://etax.tianjin.chinatax.gov.cn:8443/sbzx/view/sdsfsgjssb/#/yyzx/cwbbbs/ydy')

        self.pre_check()
        self.page.get_by_text("财报转换").click()
        self.page.get_by_text("下一步").click()
        self.check_dup()

        with self.page.expect_file_chooser() as fc_info:
            self.page.get_by_role("button").filter(has_text="选择文件").click()
            file_chooser = fc_info.value

            import tempfile
            import pandas as pd
            if isinstance(sheet_data, str):
                sheet_data = json.loads(sheet_data)
            with tempfile.TemporaryDirectory() as tmpdir:
                xls_files = []
                for name, sheet in sheet_data.items():
                    pd_data = pd.DataFrame(sheet)
                    xls_file = os.path.join(tmpdir, f'{name}.xlsx')
                    pd_data.to_excel(xls_file, index=False, header=False, sheet_name=name)
                    xls_files.append(xls_file)
                file_chooser.set_files(xls_files)

                self.page.get_by_role("button").filter(has_text="转换报表").click()

        self.check_table()

        self.page.get_by_role("button").filter(has_text="提交申报").click()
        self.confirm_captcha()
        if not submit:
            return
        self.page.get_by_role("button").filter(has_text="确定").click()

        # {
        #   "allProcessTime": 137,
        #   "nsrdProcessTime": 131,
        #   "yfwjcptProcessTime": 126,
        #   "Response": {
        #     "processTime": 6,
        #     "RequestId": "17393c1b6da94631",
        #     "Data": {
        #       "BizCode": "00",
        #       "Body": "{\"traceId\":\"cf56b5666f6d4150\",\"returnFlag\":\"Y\",\"swsxDm\":\"SXN022011301\",\"yzpzzlDm\":\"ZLA0610216\",\"needPdf\":\"Y\",\"sbrq\":\"2024-07-04\",\"ywmc\":\"财务报表报送与信息采集（小企业会计准则）\",\"sblx\":\"cb\"}",
        #       "Ysqxxid": "7B8187DBFFFFFFC36A5ED5F952BD638A"
        #     }
        #   }
        # }
        query_url = '/sbzx/api/sdsfsgjssb/qysdssb/cwbbbs/v1/getSbResult'
        for i in range(60):
            with self.page.expect_response(
                    lambda response: query_url in response.url and response.status == 200) as response_info:
                logger.debug('get request')
                response = response_info.value
                data = response.json()
                data = AttrDict(data)
                body = AttrDict(json.loads(data.Response.Data.Body))
                if body.returnFlag == 'Y':
                    break
        else:
            raise FileBSISError(data)

        self.wait(2000)
        self.screenshot('file bsis success')
        return data


if __name__ == '__main__':
    data1 = [
        ['资产', '行次', '期末余额', '上年年末余额', '负债和所有者（或股东）权益', '行次', '期末余额', '上年年末余额'],
        ['流动资产：', '0', '', '', '流动负债：', '0', '', ''],
        ['货币资金', '1', '543757.69', '1937984.31', '短期借款', '31', '', ''],
        ['短期投资', '2', '', '', '应付票据', '32', '', ''],
        ['应收票据', '3', '', '', '应付账款', '33', '1429660.41', '1434660.41'],
        ['应收账款', '4', '315818.21', '240874.21', '预收账款', '34', '', ''],
        ['预付账款', '5', '', '', '应付职工薪酬', '35', '', ''],
        ['应收股利', '6', '', '', '应交税费', '36', '-3961.50', '-4205.88'],
        ['应收利息', '7', '', '', '应付利息', '37', '', ''],
        ['其他应收款', '8', '270322.83', '-428178.22', '应付利润', '38', '', ''],
        ['存货', '9', '', '', '其他应付款', '39', '5534310.31', '5955805.12'],
        ['其中：原材料', '10', '', '', '其他流动负债', '40', '', ''],
        ['在产品', '11', '', '', '流动负债合计：', '41', '6960009.22', '7386259.65'],
        ['库存商品', '12', '', '', '非流动负债：', '0', '', ''],
        ['周转材料', '13', '', '', '长期借款', '42', '', ''],
        ['其他流动资产', '14', '', '', '长期应付款', '43', '', ''],
        ['流动资产合计', '15', '1129898.73', '1750680.30', '递延收益', '44', '', ''],
        ['非流动资产：', '0', '', '', '其他非流动负债', '45', '', ''],
        ['长期债券投资', '16', '', '', '非流动负债合计', '46', '', ''],
        ['长期股权投资', '17', '', '', '负债合计', '47', '6960009.22', '7386259.65'],
        ['固定资产原价', '18', '560408.99', '560408.99', '', '', '', ''],
        ['减：累计折旧', '19', '560408.99', '560408.99', '', '', '', ''],
        ['固定资产账面价值', '20', '', '', '', '', '', ''],
        ['在建工程', '21', '', '', '', '', '', ''],
        ['工程物资', '22', '', '', '', '', '', ''],
        ['固定资产清理', '23', '', '', '', '', '', ''],
        ['生产性生物资产', '24', '', '', '所有者权益（或股东权益）：', '0', '', ''],
        ['无形资产', '25', '', '', '实收资本（或股本）', '48', '', ''],
        ['开发支出', '26', '', '', '资本公积', '49', '', ''],
        ['长期待摊费用', '27', '', '', '盈余公积', '50', '', ''],
        ['其他非流动资产', '28', '', '', '未分配利润', '51', '-5830110.49', '-5635579.35'],
        ['非流动资产合计', '29', '', '', '所有者权益（或股东权益）合计', '52', '-5830110.49', '-5635579.35'],
        ['资产总额', '30', '1129898.73', '1750680.30', '负债和所有者权益（或股东权益）总计', '53', '1129898.73', '1750680.30'],
    ]

    data2 = [
        ['项目', '行次', '本年累计金额', '本期金额'],
        ['一、营业收入', '1', '4664.15', '4664.15'],
        ['减：营业成本', '2', '', ''],
        ['税金及附加', '3', '', ''],
        ['其中：消费税', '4', '', ''],
        ['营业税', '5', '', ''],
        ['城市维护建设税', '6', '', ''],
        ['资源税', '7', '', ''],
        ['土地增值税', '8', '', ''],
        ['城镇土地使用税、房产税、车船税、印花税', '9', '', ''],
        ['教育费附加、矿产资源补偿税、排污费', '10', '', ''],
        ['销售费用', '11', '', ''],
        ['其中：商品维修费', '12', '', ''],
        ['广告费和业务宣传费', '13', '', ''],
        ['管理费用', '14', '198893.12', '95852.19'],
        ['其中：开办费', '15', '', ''],
        ['业务招待费', '16', '', ''],
        ['研究费用', '17', '', ''],
        ['财务费用', '18', '302.17', '198.94'],
        ['其中：利息费用（收入以“-”号填列）', '19', '', ''],
        ['加：投资收益（损失以“-”号填列）', '20', '', ''],
        ['二、营业利润（亏损以“-”号填列）', '21', '-194531.14', '-91386.98'],
        ['加：营业外收入', '22', '', ''],
        ['其中：政府补助', '23', '', ''],
        ['减：营业外支出', '24', '', ''],
        ['其中：坏账损失', '25', '', ''],
        ['无法收回的长期债券投资损失', '26', '', ''],
        ['无法收回的长期股权投资损失', '27', '', ''],
        ['自然灾害等不可抗力因素造成的损失', '28', '', ''],
        ['税收滞纳金', '29', '', ''],
        ['三、利润总额（亏损总额以“-”号填列）', '30', '-194531.14', '-91386.98'],
        ['减：所得税费用', '31', '', ''],
        ['四：净利润（净亏损以“-”号填列）', '32', '-194531.14', '-91386.98'],
    ]

    sheet_data = {
        "资产负债表": data1,
        "利润表": data2,
    }

    from lib.agent.shell import run, run_all
    run('涞水汇森劳务派遣有限公司天津分公司', FileBSIS, FileBSIS.file_bsis, sheet_data=sheet_data, submit=False)
