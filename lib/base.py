from django.db import models


class BaseModel(models.Model):
    status = models.PositiveIntegerField(default=0)
    flag = models.PositiveBigIntegerField(default=0)
    addtime = models.DateTimeField(auto_now_add=True)
    modtime = models.DateTimeField(auto_now=True)
    attr = models.TextField(blank=True, null=True)

    STATUS_NEW = 0  # 新建
    STATUS_DOING = 32  # 处理中
    STATUS_DONE = 64  # 成功
    STATUS_FAIL = 128  # 失败
    STATUS_DELETE = 255  # 删除
    STATUS_WAIT = 48  # 等待操作

    class Meta:
        abstract = True
