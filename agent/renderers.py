from rest_framework.renderers import JSONRenderer


class CodeMsgRenderer(JSONRenderer):
    def render(self, data, *args, **kwargs):
        data = {
            'code': 200,
            'msg': 'OK',
            'data': data,
        }
        return super().render(data, *args, **kwargs)
