# ScribeClient
日志发送及解析类

创建 ErrorLogger 记录错误日志类:

```

class ErrorLogger(ScribeClient):
    entity = 'demo.error'
    code = IntField()
    msg = StringField()


＃ 记录日志
ErrorLogger(code=404, msg='要访问的内容不存在').send()

‘’‘ 日志格式如下：
2016-05-19 16:22:48.793844	demo.error	code=404	msg=要访问的内容不存在
‘’‘
＃ 日志解析，返回 ErrorLogger 对象
logger = ScribeClient.parse(line)
```
