import time
from lib.logger import logger
from lib.attrdict import AttrDict
from lib.agent.bureau import Bureau, login_etax_decorator, StopError


class ReovkeTaxTaxationFormListError(StopError):
    errcode = 140201
    errmsg = '请求申报表单失败'


class ReovkeTaxParseError(StopError):
    errcode = 140202
    errmsg = '纳税信息解析错误'


class ReovkeTaxMatchError(StopError):
    errcode = 140203
    errmsg = '未匹配到对应的报税信息'


class ReovkeTaxError(StopError):
    errcode = 140204
    errmsg = '撤销失败'


class RevokeTax(Bureau):

    @login_etax_decorator
    def revoke_tax(self, tax_type='BDA0610606', submit=True):
        self.page.goto('https://etax.tianjin.chinatax.gov.cn:8443/sbzx/view/ggsfsb/#/declare/correct')
        self.page.wait_for_load_state()
        query_path = '/sbzx/api/ggsfsb/gzsb/v1/listSbxx'
        with self.page.expect_response(lambda response: query_path in response.url and response.status == 200) as response_list:
            response_list = response_list.value
            tax_list_response = response_list.json()
            tax_list_data = AttrDict(tax_list_response)
            logger.debug('get tax_list_data over')
            # 判断是否存在可退的税
            tax_info = {}
            try:
                taxation_form_list = tax_list_data.Response.Data.Result.List
                for taxation_form in taxation_form_list:
                    if taxation_form.yzpzzlDm == tax_type:
                        for tax_revoke_status in taxation_form.buttonVOs:
                            if tax_revoke_status.pzdz == "/sbzx/api/ggsfsb/sffw/sbzf/common/v1":
                                tax_info = taxation_form
                                break
            except:
                logger.debug('get taxation_form_list fail')
                raise ReovkeTaxParseError()
            if not tax_info:
                raise ReovkeTaxMatchError()
        if not submit:
            return
        # 作废(撤回)当前报税
        revoke_tax_url = f"https://etax.tianjin.chinatax.gov.cn:8443/sbzx/api/ggsfsb/sffw/sbzf/common/v1?_={int(time.time() * 1000)}"
        revoke_tax_response = self.context.request.post(
            revoke_tax_url,
            data={
                "Pzxh": tax_info['pzxh'],
                "YzpzzlDm": tax_type,
                "Skssqq": tax_info['skssqq'],
                "Skssqz": tax_info['skssqz'],
                "Sbuuid": tax_info['sbuuid'],
                "ZsxmDm": tax_info['zsxmDm'],
                "Zfyy": ""
            }
        )
        if revoke_tax_response.status != 200:
            logger.debug('get revoke tax request fail')
            raise ReovkeTaxTaxationFormListError()
        revoke_tax_data = AttrDict(revoke_tax_response.json())

        try:
            if revoke_tax_data.Response.Data.Result is True and revoke_tax_data.Response.Data.Error is None:
                return revoke_tax_data
            self.screenshot('revoke tax fail')
            raise ReovkeTaxError(revoke_tax_data)
        except:
            ReovkeTaxError()


if __name__ == '__main__':
    from lib.agent.shell import run
    run('天津市金禾物流有限公司', RevokeTax, RevokeTax.revoke_tax, submit=False)
