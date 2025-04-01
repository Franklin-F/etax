import fire
import traceback
from playwright.sync_api import sync_playwright
from lib.logger import logger
from lib.agent.bureau import Bureau as Agent
from lib.agent.bureau import ETAX_HOMEPAGE
from lib.agent.accounts import default_account, search_account


def reload():
    """
    this method cannot reload class and replace existing object
    wait for more insightful minds on this
    """
    import sys
    import importlib
    for name, module in sys.modules.copy().items():
        if name.startswith('lib'):
            logger.debug(f'Reloaded {name}')
            importlib.reload(module)


def run(account, cls, method, *args, wait_cmd=True, **kwargs):
    from lib.agent.accounts import get_account
    account = get_account(account)
    agent = cls(
        name=account.name,
        credit_id=account.credit_id,
        user_id=account.user_id,
        password=account.password,
    )
    try:
        cls_str = cls.__name__
        method_str = method.__name__
        args_str = ' '.join(str(arg) for arg in args)
        kwargs_str = ' '.join(f'--{key}={val}' for key, val in kwargs.items())
        logger.debug(f'Run {cls_str} {method_str} {args_str} {kwargs_str}')
        logger.info(method(agent, *args, **kwargs))
    except KeyboardInterrupt as err:
        logger.error(err)
        logger.error(traceback.format_exc())
    except Exception as err:
        logger.error(err)
        logger.error(traceback.format_exc())
    if wait_cmd:
        agent.wait_cmd()


def run_all(cls, method, *args, **kwargs):
    from lib.agent.accounts import accounts
    for account in accounts:
        run(account.name, cls, method, *args, **kwargs)


def main(account=None, redirect_uri=ETAX_HOMEPAGE):
    if isinstance(account, str) and account.startswith('http'):
        account, redirect_uri = None, account
    account = search_account(account) if account else default_account
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context()
    # context = browser.new_context(storage_state=r'C:\Users\pc\Desktop\91120221MA06DLX78N.json')
    page = context.new_page()
    self = Agent(
        playwright=playwright,
        browser=browser,
        context=context,
        page=page,
        name=account.name,
        user_id=account.user_id,
        credit_id=account.credit_id,
        password=account.password,
    )
    self.login()
    self.page.goto(redirect_uri)

    import code
    # please do not delete next line: import readline
    # otherwise it will NOT read last command in MacOS by pressing UP key
    import readline
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()


if __name__ == '__main__':
    fire.Fire(main)