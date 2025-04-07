import os
import traceback
from sys import platform
from lib.logger import logger
from lib.days import get_now

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


class Browser:
    singleton = None

    def __init__(self,
                 name=None,
                 credit_id=None,
                 user_id=None,
                 password=None,
                 headless=None,
                 screenshot_dir=None,
                 download_dir=None,
                 cookies=None,
                 browser_type=None,
                 playwright=None,
                 browser=None,
                 context=None,
                 page=None,
                 ):
        self.result = None
        self.name = name
        self.credit_id = credit_id
        self.user_id = user_id
        self.password = password
        self.browser_type = browser_type or 'chromium' # 'firefox'

        self.headless = headless
        if self.headless is None:
            self.headless = platform == "linux" or platform == "linux2"

        if screenshot_dir:
            self.screenshot_dir = screenshot_dir
        else:
            from django.conf import settings
            self.screenshot_dir = settings.PLAYWRIGHT_SCREENSHOT_DIR
        os.makedirs(self.screenshot_dir, exist_ok=True)

        if download_dir:
            self.download_dir = download_dir
        else:
            from django.conf import settings
            self.download_dir = settings.AGENT_DIR
        os.makedirs(self.download_dir, exist_ok=True)

        self._playwright = playwright
        self._browser = browser
        self._context = context
        self._page = page
        self._cookies = cookies
        self._has_start = True
        self._has_login = False

        if Browser.singleton:
            Browser.singleton.end()
            Browser.singleton = None
        Browser.singleton = self

    def __del__(self):
        self.end()

    def __str__(self):
        return f'{self.name} {self.credit_id} {self.user_id}'

    @property
    def playwright(self):
        if self._playwright is None:
            from playwright.sync_api import sync_playwright
            self._playwright = sync_playwright().start()
            logger.debug('playwright new instance')
        return self._playwright

    @property
    def browser(self):
        if self._browser is None:
            self._browser = getattr(self.playwright, self.browser_type).launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            logger.debug('playwright new browser')
        return self._browser

    @property
    def context(self):
        if self._context is None:
            self._context = self.browser.new_context(locale="zh-CN")
            logger.debug('playwright new context')
        return self._context

    @property
    def page(self):
        if self._page is None:
            self._page = self.context.new_page()
            self._page.set_extra_http_headers({
                'Accept-Charset': 'utf-8'
            })
            logger.debug('playwright new page')
        return self._page

    @page.setter
    def page(self, newpage):
        self._page = newpage


    def new_context(self):
        logger.debug('new context')
        self.new_page()
        self._context = None

    def new_page(self):
        self._page = None

    def end(self):
        if not self._has_start:
            return
        self._has_start = False
        if self._browser:
            logger.debug('playwright close browser')
            self._browser.close()
        if self._playwright:
            logger.debug('playwright close instance')
            self._playwright.stop()

    def screenshot(self, name=None, full_page=False, log=True, locator_obj=None):
        if log and name:
            logger.debug(name)
        now_str = get_now().strftime('%Y%m%d%H%M%S%f')
        name = name.lower().replace(' ', '_') if name else ''
        pic_name = f'{now_str}_{self.user_id}{"_" + name if name else ""}.png'
        path = os.path.join(self.screenshot_dir, pic_name)
        if locator_obj:
            locator_obj.screenshot(path=path)
        else:
            self.page.screenshot(path=path, full_page=full_page)

    def wait(self, duration=1000):
        self.page.wait_for_timeout(duration)

    def wait_for(self, selector,
                 duration=1000,
                 close_dialog=True,
                 close_message_box=True,
                 close_dppt_dialog=True
                 ):
        self.page.wait_for_timeout(duration)

    def wait_cmd(self):
        if self.headless:
            return
        while True:
            cmd = input('Press any cmd to run: ')
            if not cmd:
                break
            try:
                exec(cmd)
            except:
                print(traceback.format_exc())
