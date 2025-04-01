from lib.notice import wecom
from django.core.management import BaseCommand


class Wecom(BaseCommand):
    def handle(self, *args, **options):
        wecom.send_text('测试测试')
        wecom.send_markdown(content="# Hi \n > 好家伙，我tm直接好家伙")
        wecom.send_image(image_path='/tmp/wecom/test.jpg')
        wecom.send_voice(voice_path='/tmp/wecom/test.amr')
        wecom.send_video(video_path="/tmp/wecom/test.mp4", safe=1)
        wecom.send_file(file_path="/tmp/wecom/test.txt", safe=1)
        wecom.send_news(
            title="Hi, it's GentleCP",
            desp="Welcome to my world!",
            url="https://blog.gentlecp.com",
            picurl="https://gitee.com/gentlecp/ImgUrl/raw/master/20210313141425.jpg"
        )
        wecom.send_card(
            title='求索｜CP',
            desp='CP的个人博客',
            url="https://blog.gentlecp.com",
            btntxt="more",
        )
        wecom.send_mpnews(
            title='你好，我是CP',
            image_path='data/test.png',
            content='<a href="https://blog.gentlecp.com">Hello World</a>',
            content_source_url='https://blog.gentlecp.com',
            author='GentleCP',
            digest='这是一段描述',
            safe=1
        )
