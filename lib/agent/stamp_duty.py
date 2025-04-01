import os
import json
from functools import partial
from lib.logger import logger
from lib.attrdict import AttrDict
from lib.agent.bureau import Bureau, login_etax_decorator, StopError


class StampDutyUploadError(StopError):
    errcode = 190201
    errmsg = '上传失败'


# 报印花税
class StampDuty(Bureau):
    stamp_duty_enum = {'*应税凭证名称': 'credential_name',
                       '*申报期限类型': 'term_type',
                       '*应税凭证数量': 'number_of_vouchers',
                       '*税目': 'tax_items',
                       '*应纳税凭证书立日期': 'tax_certificate_date',
                       '*计税金额': 'amount',
                       '*应纳税额': 'tax_amount',
                       '*税率': 'tax_rate',
                       '*税款所属期起': 'begin_date',
                       '*税款所属期止': 'end_date'
                       }

    @partial(login_etax_decorator, redirect_uri='https://etax.tianjin.chinatax.gov.cn:8443/sbzx/view/cxssb/cchxwsnssb')
    def stamp_duty(self, begin_date, end_date, stamp_duty_data, is_zero_declaration, declaration_type='11|正常申报', submit=True):
        self.page.goto('https://etax.tianjin.chinatax.gov.cn:8443/sbzx/view/cxssb/cchxwsnssb')
        self.page.locator('.t-button--theme-primary').filter(has_text='填表式申报').click()
        self.page.locator('.title-ellipsis').filter(has_text='印花税').click()
        if not is_zero_declaration:
            self.page.locator('.t-button--theme-primary').filter(has_text='导入').click()
            with self.page.expect_file_chooser() as fc_info:
                self.page.locator('.t-button--variant-outline').filter(has_text='选择文件').click()
                file_chooser = fc_info.value
                upload_file_path = self.init_file(begin_date, end_date, declaration_type, stamp_duty_data)
                file_chooser.set_files(upload_file_path)
            self.page.locator('.t-dialog--default').locator("visible=true").locator('.t-button--theme-primary').filter(has_text='确定').click()

            # 文件校验
            url = 'https://etax.tianjin.chinatax.gov.cn:8443/sbzx/api/cxssb/yhssycj/v1/getDrxx'
            with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_list:
                response_list = response_list.value
                tax_list_response = response_list.json()
                tax_list_data = AttrDict(tax_list_response)
                if tax_list_data.rescode != '1001':
                    StampDutyUploadError.errmsg = tax_list_data.resmsg
                    raise StampDutyUploadError

        self.page.locator('.footerbar.submit .t-button--theme-primary').filter(has_text='提交').click()

        url = 'https://etax.tianjin.chinatax.gov.cn:8443/sbzx/api/cxssb/yhssycj/v1/queryXxfpAndJxfp'
        with self.page.expect_response(lambda response: url in response.url and response.status == 200) as response_list:
            response_list = response_list.value
            tax_list_response = response_list.json()
            tax_list_data = AttrDict(tax_list_response)
            if tax_list_data.Response.Data.code == '-1':
                self.page.locator('.t-dialog__footer .t-button--theme-primary').locator("visible=true").filter(has_text='确定').click()

        # 提交
        if not submit:
            return
        self.page.locator('.t-button--theme-primary').filter(has_text='提交申报').click()
        self.confirm_captcha()
        self.page.get_by_role("button").filter(has_text="确定").click()
        # 最后截图
        self.page.locator('.text').filter(has_text="申报成功").wait_for()
        self.screenshot(name='stamp_duty_end')

    def init_file(self, begin_date, end_date, declaration_type, stamp_duty_data):
        """
        将数据处理成规定的格式文件
        """
        from django.conf import settings
        template_file = f"{settings.ASSETS_DIR}/template/印花税采集模板.xlsx"
        import shutil
        import time
        # 复制文件
        file_path = f"{settings.OSS_DIR}/{self.credit_id}/stamp_duty/"
        file_name = f"stamp_duty_{int(time.time())}.xlsx"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        shutil.copy(template_file, file_path + file_name)

        import pandas as pd
        sheet_name = '采集表'
        data = pd.read_excel(file_path + file_name, sheet_name=sheet_name)
        data = data.to_dict(orient='records')
        data[2]['Unnamed: 3'] = begin_date
        data[2]['Unnamed: 6'] = end_date
        data[2]['Unnamed: 10'] = declaration_type
        title = data[5]
        data = data[0:8]
        res = []
        import datetime
        stamp_duty_data = json.loads(stamp_duty_data)
        for tax_info in stamp_duty_data:
            tax_info['begin_date'] = begin_date
            tax_info['end_date'] = end_date
            line_data = {}
            for key in title:
                line_data[key] = tax_info.get(self.stamp_duty_enum.get(title[key], ''), '')
                if self.stamp_duty_enum.get(title[key], '') == 'tax_certificate_date':
                    line_data[key] = datetime.datetime.strptime(tax_info.get(self.stamp_duty_enum.get(title[key], ''), ''), "%Y-%m-%d")
            res.append(line_data)

        data = pd.DataFrame(data)
        res = pd.DataFrame(res)
        end_data = pd.concat([data, res])

        with pd.ExcelWriter(file_path + file_name, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            end_data.to_excel(writer, sheet_name=sheet_name, index=False, )
        self.wait(500)
        return file_path + file_name


if __name__ == '__main__':
    from lib.agent.shell import run

    stamp_duty_data = json.dumps([{
        "credential_name": "例1",
        "term_type": "00|按期申报",
        "number_of_vouchers": "1",
        "tax_items": "101110111|买卖合同",
        "tax_certificate_date": "2024-6-30",
        "amount": 33634.58,
        "tax_rate": 0.0003,
        "tax_amount": 10.09
    }, ], ensure_ascii=False)
    import datetime

    run('天津聚兴旺建材销售有限公司',
        StampDuty, StampDuty.stamp_duty,
        begin_date=datetime.datetime.strptime('2024-04-01', "%Y-%m-%d"),
        end_date=datetime.datetime.strptime('2024-06-30', "%Y-%m-%d"),
        stamp_duty_data=stamp_duty_data,
        is_zero_declaration=0
        )
