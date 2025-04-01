import fire
from django.conf import settings
from pathlib import Path
import corpwechatbot


corpwechatbot.app.TOKEN_PATH = Path(settings.TEMPORARY_TOKEN_JSON)
wecom = corpwechatbot.app.AppMsgSender(
    corpid=settings.WECOM_CORPID,
    corpsecret=settings.WECOM_CORPSECRET,
    agentid=settings.WECOM_AGENTID,
)


if __name__ == '__main__':
    fire.Fire()
