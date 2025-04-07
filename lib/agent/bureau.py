import json
import time
import traceback
import urllib.parse
from collections import defaultdict
from playwright.sync_api import expect
from functools import partial, wraps
from lib.logger import logger
from lib.days import *
from lib.attrdict import AttrDict
from .browser import Browser


OLD_ETAX_CLIENT_ID = 'x3ef652ax3294xz6beefnf5zadbf66cc'
OLD_ETAX_HOMEPAGE = 'https://etax.tianjin.chinatax.gov.cn/'

ETAX_CLIENT_ID = 'q4q6b8aa469v4369ae7483c4vb45cvca'
ETAX_HOMEPAGE = 'https://etax.tianjin.chinatax.gov.cn:8443/loginb/'

DPPT_CLIENT_ID = 'EQE42EE6837f496b9a393E4Qdf57a97E'
DPPT_HOMEPAGE = 'https://dppt.tianjin.chinatax.gov.cn:8443/'


class ClientError(Exception):
    pass


class ServerError(Exception):
    pass


class NeedLoginError(Exception):
    pass


class StopError(Exception):
    errcode = 1
    errmsg = "处理失败"

    def __init__(self, payload=None, errcode=None, errmsg=None):
        self.payload = payload
        self.errcode = errcode or self.errcode
        self.errmsg = errmsg or self.errmsg

    def __str__(self):
        return f'{self.__class__.__name__} {self.errcode} {self.errmsg}'


class LoginFailError(StopError):
    errcode = 100000
    errmsg = '登录失败'

    # code=2018 msg=输入的统一社会信用代码或纳税人识别号错误，请重新输入
    # code=2023 msg=连续认证错误次数过多，您的账号已被锁定。建议您直接使用“忘记密码”修改密码
    # code=2034 msg=未查询到您与该企业的关联关系信息，请确认录入的信息是否正确！
    # code=2035 msg=输入的个人账号或密码错误，请重新输入！
    # code=2059 msg=该用户未注册，请在自然人业务入口进行用户注册
    def __init__(self, payload=None, errcode=None, errmsg=None):
        if not isinstance(payload, AttrDict):
            payload = AttrDict(payload)
        if not errcode:
            errcode = self.errcode
            if 'code' in payload:
                errcode += payload.code
        if not errmsg:
            errmsg = self.errmsg
            if 'msg' in payload:
                errmsg = payload.msg
        super().__init__(payload, errcode, errmsg)


class AccountRelationInvalid(StopError):
    errcode = 110001
    errmsg = '账号需要进行关联关系确认'


class MonthInvalid(StopError):
    errcode = 110002
    errmsg = '当前月份不可选'


class Bureau(Browser):

    def login(self,
              name=None,
              credit_id=None,
              user_id=None,
              password=None,
              client_id=ETAX_CLIENT_ID,
              redirect_uri=ETAX_HOMEPAGE,
              submit=True,
              ):

        self.name = name or self.name
        self.credit_id = credit_id or self.credit_id
        self.user_id = user_id or self.user_id
        self.password = password or self.password

        login_host = 'https://tpass.tianjin.chinatax.gov.cn:8443/#/login'
        login_api = 'https://tpass.tianjin.chinatax.gov.cn:8443/sys-api/v1.0/auth/enterprise/quick/accountLogin'
        for attempt in range(3):
            try:
                redirect_uri_encoded = urllib.parse.quote_plus(redirect_uri)
                login_url = f'{login_host}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri_encoded}'
                logger.debug(f'Login {self.name} {login_url}')
                self.page.goto(login_url)
                self.page.get_by_placeholder("统一社会信用代码/纳税人识别号").wait_for()
                self.screenshot('open login page')
                self.page.get_by_placeholder("统一社会信用代码/纳税人识别号").fill(self.credit_id)
                self.page.get_by_placeholder("居民身份证号码/手机号码/用户名").fill(self.user_id)
                self.page.get_by_placeholder("个人用户密码(初始密码为证件号码后六位)").fill(self.password)
                self.drag_box()
                self.screenshot('fill login form')

                if not submit:
                    return

                with self.page.expect_response(lambda response: login_api in response.url) as response_info:
                    self.page.get_by_role("button").filter(has_text="登录").click()
                    self.screenshot('click login button')

                # {
                #     "code": 1000,
                #     "msg": "处理成功！",
                #     "zipCode": "0",
                #     "encryptCode": "2",
                #     "datagram": "7843b00d79588ffc54040939e61b205f91c5d7c3cac45146263f5d08778c6c1d08098ea8f9d6cb3a603de61f495f11e111c05d5724faccccaf04f6c992f75f46d6ff81af430edcee99f3727c035b10ac91f6ba04aa8b4d6ec72a7adccdbd5589316ce495cf03a8dac243eb3a2d39009a0597d7deee84869c32974707a0f07d4253fb446f55b97e2a71b76172ef19324d",
                #     "signtype": "HMacSHA256",
                #     "signature": "76F307F327B9F395639F486744EE962AE492D696A717E33FE55DCB218CBEC2C7",
                #     "timestamp": "20240221085136",
                #     "requestId": "33441a6de94d41de"
                # }
                data = None
                response = response_info.value
                if response.status >= 500:
                    raise ServerError
                elif 500 > response.status >= 400:
                    raise ClientError
                elif 300 > response.status >= 200:
                    data = response.json()
                    data = AttrDict(data)
                    if data.code != 1000:
                        raise LoginFailError(data)

                self.screenshot('login api success')
                # self.page.on("dialog", self.handle_dialog)
                # 这里有新增加办税人开票人等信息第一次登录会让确认
                login_confirmation = self.page.locator(".el-message-box")
                if login_confirmation.count():
                    login_confirmation.locator(".el-button.el-button--primary").click()
                for i in range(10):
                    self.wait(500)
                    if self.page.url and not self.page.url.startswith(login_host):
                        self.page.wait_for_load_state()
                        self._has_login = True
                        self.screenshot('login success')
                        return data
                    self.close_el_dialog()

            except LoginFailError as err:
                self.screenshot('login fail')
                raise err
            except StopError as err:
                self.screenshot('login error')
                raise err
            except ClientError as err:
                self.screenshot('login client error')
                raise err
            except ServerError as err:
                logger.warning(err)
                self.screenshot('login server error')
            except Exception as err:
                logger.error(err)
                logger.error(traceback.format_exc())
                self.screenshot('login exception')

            self.new_context()

    def login_with_auth_state(self,name=None,
              credit_id=None,
              user_id=None, auth_state=None,client_id=None, redirect_uri=None):
        self.name = name or self.name
        self.credit_id = credit_id or self.credit_id
        self.user_id = user_id or self.user_id
        if isinstance(auth_state, str):
            auth_state = json.loads(auth_state)
        self._context = self.browser.new_context(storage_state=auth_state)
        self.page = self._context.new_page()
        logger.debug(f'login_with_auth_state {self.name} {ETAX_HOMEPAGE} {auth_state}')
        self.page.goto(ETAX_HOMEPAGE)
        logger.debug(f'login_with_auth_state END')
        return {"status": "success", "message": "Auth state loaded successfully."}

    def drag_box(self):
        track = self.page.wait_for_selector(".drag")
        track_box = track.bounding_box()
        slider = self.page.wait_for_selector(".drag .handler")
        slider_box = slider.bounding_box()

        start_x = slider_box['x'] + slider_box['width'] / 2
        start_y = slider_box['y'] + slider_box['height'] / 2
        drag_distance = track_box['width'] - slider_box['width']

        self.page.mouse.move(start_x, start_y)
        self.page.mouse.down()
        self.page.mouse.move(start_x + drag_distance + 50.54379, start_y + 2.70499, steps=10)
        self.page.mouse.up()

    def confirm_captcha(self):
        canvas = self.page.locator('//canvas').locator("visible=true")
        canvas.wait_for()
        self.wait(300)
        canvas.click(position={"x": 120, "y": 27}, force=True)
        self.wait(200)
        canvas.click(position={"x": 282, "y": 50}, force=True)
        self.wait(200)
        canvas.click(position={"x": 414, "y": 36}, force=True)
        self.wait(200)
        canvas.click(position={"x": 508, "y": 50}, force=True)
        self.wait(300)
        self.screenshot('click confirm captcha')

    def close_el_dialog(self):
        clicked = defaultdict(bool)
        for i in range(60):
            self.page.wait_for_load_state()
            dialog_locator = self.page.locator("//div[contains(@class, 'el-dialog') and not(contains(@class, 'el-dialog__'))]").locator("visible=true")
            message_locator = self.page.locator("//div[contains(@class, 'el-message-box') and not(contains(@class, 'el-message-box__'))]").locator("visible=true")
            dialog_count = dialog_locator.count()
            message_count = message_locator.count()
            logger.debug(f'Dialog count {dialog_count} Message count {message_count}')
            if not dialog_count and not message_count:
                return

            for i in reversed(range(dialog_count)):
                header = dialog_locator.nth(i).locator(
                    "//span[contains(@class, 'el-dialog__title')]").text_content()
                button_locator = dialog_locator.nth(i).locator(
                    "//div[contains(@class, 'el-dialog__footer')]//button")
                button_count = button_locator.count()
                logger.debug(f'Dialog button count {button_count} {header.strip()}')
                if not button_count:
                    continue
                if not clicked[header]:
                    button_locator.last.click()
                    expect(button_locator).to_have_count(0, timeout=30000)
                    clicked[header] = True
                    break

            message_box_count = self.page.locator(
                "//div[contains(@class, 'el-message-box') and not(contains(@class, 'el-message-box__'))]"). \
                locator("visible=true"). \
                locator("p:has-text('是否确认成为该企业的财务负责人?')"). \
                count()
            if message_box_count:
                raise AccountRelationInvalid

            for i in reversed(range(message_count)):
                header = message_locator.nth(i).locator(
                    "//span[contains(@class, 'el-message-box__title')]").text_content()
                button_locator = message_locator.nth(i).locator(
                    "//div[contains(@class, 'el-message-box__btns')]//button")
                button_count = button_locator.count()
                logger.debug(f'Message button count {button_count} {header.strip()}')
                if not button_count:
                    continue
                if not clicked[header]:
                    button_locator.last.click()
                    expect(button_locator).to_have_count(0, timeout=30000)
                    clicked[header] = True
                    break
        raise ClientError

    def close_dppt_dialog(self):
        clicked = False
        for i in range(60):
            dialog_loc = self.page.locator("//div[contains(@class, 't-dialog__ctx--fixed')]").locator("visible=true")
            dialog_count = dialog_loc.count()
            logger.debug(f'Dialog count {dialog_count}')
            if not dialog_count:
                return
            close_loc = dialog_loc.locator("//div[contains(@class, 't-dialog__header')]//span[contains(@class, 't-dialog__close')]").locator("visible=true")
            clicked or close_loc.click()
            clicked = True
            self.wait(500)

    def confirm_dppt_dialog(self):
        clicked = False
        for i in range(60):
            dialog_loc = self.page.locator("//div[contains(@class, 't-dialog__ctx--fixed')]").locator("visible=true")
            dialog_count = dialog_loc.count()
            logger.debug(f'Dialog count {dialog_count}')
            if not dialog_count:
                return
            close_loc = dialog_loc.locator("//div[contains(@class, 't-dialog__footer')]//button[contains(@class, 't-dialog__confirm')]").locator("visible=true")
            clicked or close_loc.click()
            clicked = True
            self.wait(500)

    def select_date(self, from_date, to_date, selector):
        if isinstance(from_date, str):
            from_date = get_day(from_date)
        if isinstance(to_date, str):
            to_date = get_day(to_date)
        if is_same_day(from_date, to_date):
            return
        selector.click()
        date_pannel = self.page.locator("//div[@class='t-date-picker__panel']").locator("visible=true")
        date_pannel.wait_for()
        if from_date.year != to_date.year:
            date_pannel.locator("//div[contains(@class, 't-date-picker__header-controller-year')]//input").click()
            date_pannel.get_by_text(f"{to_date.year}", exact=True).click()
            self.wait(500)
        if from_date.month != to_date.month:
            # Rechoose the year will NOT disannul the month
            date_pannel.locator("//div[contains(@class, 't-date-picker__header-controller-month')]//input").click()
            date_pannel.get_by_text(f"{to_date.month} 月", exact=True).click()
            self.wait(500)
        if True:
            # Must need to choose day
            # Rechoose the year or month will disannul the day, so choose it always
            table_xpath = "div[contains(@class, 't-date-picker__table')]"
            td_xpath = "td[contains(@class, 't-date-picker__cell') and " \
                       "not(contains(@class, 't-date-picker__cell--disabled')) and " \
                       "not(contains(@class, 't-date-picker__cell--additional'))]"
            date_pannel.locator(f"//{table_xpath}//{td_xpath}").get_by_text(f'{to_date.day}', exact=True).click()
            self.wait(500)

    def select_month(self, to_month, date_picker=None):
        from_month = ''
        for i in range(2):
            if not date_picker:
                date_picker = self.page.locator("//div[@class='t-date-picker']").locator("visible=true")
            from_month = date_picker.locator("//input").input_value()
            if not from_month:
                self.wait(500)
                continue

        from_month = from_month.replace('-', '')
        from_month = from_month or '100001'
        from_month = f'{from_month[:4]}-{from_month[4:]}'
        if isinstance(from_month, str):
            from_month = get_month(from_month)
        if isinstance(to_month, str):
            to_month = get_month(to_month)
        if is_same_month(from_month, to_month):
            return

        date_picker.click()
        date_pannel = self.page.locator("//div[@class='t-date-picker__panel']").locator("visible=true")
        date_pannel.wait_for()

        if from_month.year != to_month.year:
            date_pannel.locator("//div[contains(@class, 't-date-picker__header-controller-year')]//input").click()
            date_pannel.get_by_text(f"{to_month.year}", exact=True).click()
            self.wait(500)
        if True:
            # Must need to choose month
            # Rechoose the year will disannul the month, so choose it always
            table_xpath = "div[contains(@class, 't-date-picker__table')]"
            disable_td_xpath = "td[contains(@class, 't-date-picker__cell--disabled') or " \
                       "contains(@class, 't-date-picker__cell--additional')]"
            disable_month_loc = date_pannel.locator(f"//{table_xpath}//{disable_td_xpath}").get_by_text(f'{to_month.month} 月', exact=True)
            if disable_month_loc.count():
                raise MonthInvalid

            enable_td_xpath = "td[contains(@class, 't-date-picker__cell') and " \
                       "not(contains(@class, 't-date-picker__cell--disabled')) and " \
                       "not(contains(@class, 't-date-picker__cell--additional'))]"
            enable_month_loc = date_pannel.locator(f"//{table_xpath}//{enable_td_xpath}").get_by_text(f'{to_month.month} 月', exact=True)
            enable_month_loc.click()
            self.wait(500)


def login_decorator(fun, client_id, redirect_uri):
    # magic sauce to lift the name and doc of the function
    @wraps(fun)
    def ret_fun(self, *args, **kwargs):
        # pre function execution stuff here
        if not self._has_login:
            self.login(client_id=client_id, redirect_uri=redirect_uri)
        elif not self.page.url or redirect_uri not in self.page.url:
            self.login(client_id=client_id, redirect_uri=redirect_uri)
        returned_value = None
        for i in range(2):
            try:
                returned_value = fun(self, *args, **kwargs)
            except NeedLoginError:
                self.login(client_id=client_id, redirect_uri=redirect_uri)
            except StopError as err:
                self.wait(500)
                self.screenshot('fail')
                raise err
            else:
                break
        # post function execution stuff here

        return returned_value

    return ret_fun

def login_with_state_decorator(fun, client_id, redirect_uri):
    @wraps(fun)
    def wrapped(self, *args, **kwargs):
        auth_state = kwargs.pop('auth_state', None)
        logger.debug(f"[LOGIN] 登录装饰器被调用: {self.name} {auth_state}")
        try:
            if auth_state:
                logger.debug(f"[LOGIN] 使用 auth_state 登录: {self.name}")
                self.login_with_auth_state(
                    client_id=client_id,
                    redirect_uri=redirect_uri,
                    auth_state=auth_state
                )
                self.wait(500)
                self.screenshot('fail_auth_state')
            else:
                #原来的登录保留
                if not getattr(self, '_has_login', False):
                    logger.debug(f"[LOGIN] 未登录，开始 login")
                    self.login(client_id=client_id, redirect_uri=redirect_uri)
                elif not getattr(self, 'page', None) or redirect_uri not in self.page.url:
                    logger.debug(f"[LOGIN] 页面未就绪或跳转失效，重新 login")
                    self.login(client_id=client_id, redirect_uri=redirect_uri)

        except Exception as e:
            logger.error(f"[LOGIN STATE ERROR] 登录异常: {e}")
            raise

        for i in range(2):
            try:
                return fun(self, *args, **kwargs)
            except NeedLoginError:
                logger.warning(f"[LOGIN RETRY] NeedLoginError 第 {i+1} 次触发重新登录")
                self.login(client_id=client_id, redirect_uri=redirect_uri)
            except StopError as err:
                logger.error(f"[STOP ERROR] {err}")
                self.wait(500)
                self.screenshot('fail')
                raise err
    return wrapped

login_dppt_decorator = partial(login_decorator,
    client_id=DPPT_CLIENT_ID,
    redirect_uri=DPPT_HOMEPAGE,
)

login_etax_decorator = partial(login_decorator,
    client_id=ETAX_CLIENT_ID,
    redirect_uri=ETAX_HOMEPAGE,
)
login_new_dppt_decorator = partial(
    login_with_state_decorator,
    client_id=DPPT_CLIENT_ID,
    redirect_uri=DPPT_HOMEPAGE,
)
login_new_etax_decorator = partial(
    login_with_state_decorator,
    client_id=ETAX_CLIENT_ID,
    redirect_uri=ETAX_HOMEPAGE,
)


if __name__ == '__main__':
    from lib.agent.shell import run, run_all
    run('涞水汇森劳务派遣有限公司天津分公司', Bureau, Bureau.login)