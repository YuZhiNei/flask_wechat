import hashlib
import requests
import random
from lxml import etree
import xml.etree.ElementTree as ET
from flask import Flask, request, make_response


# 抓取文字笑话链接
url = 'https://www.qiushibaike.com/text/'


# 创建 Flask 类的实例
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def wechat_auth():
    """微信公众平台开发者文档 http://mp.weixin.qq.com/wiki
    """
    # 处理公众号发来的 GET 请求
    if request.method == 'GET':
        print('coming Get')
        data = request.args
        # 要和公众号开发者的 token 一致
        token = 'xxxxxx'
        signature = data.get('signature', '')
        timestamp = data.get('timestamp', '')
        nonce = data.get('nonce', '')
        echostr = data.get('echostr', '')
        s = [timestamp, nonce, token]
        s.sort()
        s = ''.join(s)
        if (hashlib.sha1(s.encode('utf8')).hexdigest() == signature):
            return make_response(echostr)
    # 处理公众号发来的 POST 请求
    if request.method == 'POST':
        xml_str = request.stream.read()
        xml = ET.fromstring(xml_str)
        toUserName = xml.find('ToUserName').text
        fromUserName = xml.find('FromUserName').text
        createTime = xml.find('CreateTime').text
        msgType = xml.find('MsgType').text
        if msgType != 'text':
            reply = '''
                <xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[%s]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                </xml>
                ''' % (
                    fromUserName,
                    toUserName,
                    createTime,
                    'text',
                    '非常感谢您的关注，目前公众号只有笑话功能，如需看笑话，请发送“笑话”即可。'
                )
            return reply
        content = xml.find('Content').text
        msgId = xml.find('MsgId').text
        # 判断用户发送的关键字是否为笑话
        if u'笑话' in content:
        	# 确定就开始爬虫获取页面
            r = requests.get(url)
            tree = etree.HTML(r.text)
            # 通过 xpath 获取页面指定内容
            contentlist = tree.xpath('//div[contains(@id, "qiushi_tag_")]')
            # 通过索引随机笑话
            contents = contentlist[random.randint(0, len(contentlist))]
            jokes = contents.xpath('a[1]/div[@class="content"]/span[1]/text()')
            # 通过拼接字符串和去掉换行符，再拼接成完整的内容
            joke = ''.join(''.join(jokes).split('\n'))
            reply = '''
                    <xml>
                    <ToUserName><![CDATA[%s]]></ToUserName>
                    <FromUserName><![CDATA[%s]]></FromUserName>
                    <CreateTime>%s</CreateTime>
                    <MsgType><![CDATA[%s]]></MsgType>
                    <Content><![CDATA[%s]]></Content>
                    </xml>
                    ''' % (fromUserName, toUserName, createTime, msgType, joke)
            return reply
        else:
            if type(content).__name__ == "unicode":
                content = '本公众号目前只有笑话功能，如需查看笑话，请输入回复“笑话”即可。'
            elif type(content).__name__ == "str":
                content = '本公众号目前只有笑话功能，如需查看笑话，请输入回复“笑话”即可。'
            reply = '''
                <xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[%s]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                </xml>
                ''' % (fromUserName, toUserName, createTime, msgType, content)
        return reply


if __name__ == '__main__':
	# 启动程序并设置端口为 8080
    app.run(port=8080)