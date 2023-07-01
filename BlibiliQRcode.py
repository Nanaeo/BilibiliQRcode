import json
import os
import time
import urllib.parse
from http.cookies import SimpleCookie
import requests


def http_get(url, params=None, headers=None, cookies=None):
    response = requests.get(url, params=params, headers=headers, cookies=cookies)
    return response


def http_post(url, data=None, json_data=None, headers=None, cookies=None):
    response = requests.post(url, data=data, json=json_data, headers=headers, cookies=cookies)
    return response


def get_mid_string(text, head_str, end_str):
    if not isinstance(text, str) or not isinstance(head_str, str) or not isinstance(end_str, str):
        raise ValueError("text, head_str, and end_str must be strings")
    start = text.find(head_str)
    if start >= 0:
        start += len(head_str)
        end = text.find(end_str, start)
        if end >= 0:
            return text[start:end].strip()

    return None


def merge_cookies(cookie_str1, cookie_str2):
    # 创建两个 SimpleCookie 对象，用于加载 cookies 字符串
    cookies1 = SimpleCookie()
    cookies1.load(cookie_str1)  # 将第一个 cookies 字符串加载到 cookies1 对象中
    cookies2 = SimpleCookie()
    cookies2.load(cookie_str2)  # 将第二个 cookies 字符串加载到 cookies2 对象中
    # 创建一个新的 SimpleCookie 对象，用于存储合并后的 cookies
    merged_cookies = SimpleCookie()
    # 将第二个 cookies 中的值添加到 merged_cookies，覆盖相同的键
    for key, morsel2 in cookies2.items():
        merged_cookies[key] = morsel2.value
    # 将第一个 cookies 中的值添加到 merged_cookies
    for key, morsel1 in cookies1.items():
        merged_cookies[key] = morsel1.value
    # 将 merged_cookies 转换为字符串格式
    merged_cookie_str = merged_cookies.output(header='', sep=';')
    return merged_cookie_str


def convert_cookiejar_to_str(cookiejar):
    # 创建一个空的SimpleCookie对象
    cookies = SimpleCookie()
    # 从cookiejar加载cookie
    cookies.load(cookiejar)
    # 创建一个空字典来存储合并后的cookie
    merged_cookies = {}
    # 遍历cookies并将其转换为字典
    for key, morsel in cookies.items():
        merged_cookies[key] = morsel.value
    # 将字典转换为标准字符串
    cookie_str = "; ".join([f"{key}={value}" for key, value in merged_cookies.items()])
    return cookie_str


def convert_cookies_to_dict(cookie_str):
    cookie_dict = {}
    cookies = SimpleCookie()  # 创建一个 SimpleCookie 对象
    cookies.load(cookie_str)  # 加载 cookie 字符串到 SimpleCookie 对象
    for key, morsel in cookies.items():  # 遍历 SimpleCookie 中的键值对
        cookie_dict[key] = morsel.value  # 将键值对存储到字典中
    return cookie_dict


# 初始化获取 Cookies
res = http_get(url="https://passport.bilibili.com/x/passport-login/web/qrcode/generate")
res = json.loads(res.text)
if res["code"] != 0:
    print('Boot Error')
    exit(1)
qrcode_url = 'https://api.pwmqr.com/qrcode/create/?url=' + urllib.parse.quote(res["data"]["url"])
qrcode_key = res["data"]["qrcode_key"]
print("Scan URL：" + qrcode_url)
print("Scan Key：" + qrcode_key)
os.system('"C:/Program Files/Internet Explorer/iexplore.exe" ' + qrcode_url)
# 使用浏览器有利于减少体积

while True:
    time.sleep(3)
    verify_url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key=' + qrcode_key
    res = http_get(verify_url)
    custom_cookies = res.cookies
    res = json.loads(res.text)
    print("Scan Result：" + res["data"]["message"])
    if res["data"]["url"] != '':
        break

print("Bilibili Login...")
csrf = get_mid_string(res["data"]["url"], 'bili_jct=', '&')
user_id = get_mid_string(res["data"]["url"], 'DedeUserID=', '&')
sess_data = get_mid_string(res["data"]["url"], '&SESSDATA=', '&')
print("Bilibili Csrf：" + csrf)
print("Bilibili User ID：" + user_id)
print("Bilibili Sessdata：" + sess_data)
sso_url = 'https://passport.bilibili.com/x/passport-login/web/sso/list?biliCSRF=' + csrf
res = http_get(url=sso_url, cookies=convert_cookies_to_dict(custom_cookies))
res = json.loads(res.text)
if res["code"] != 0:
    print('Login Error')
    exit(1)
sso_dict = res["data"]["sso"]
print("SsoAuthLink:" + sso_dict[3])
res = http_get(url=sso_dict[3], cookies=convert_cookies_to_dict(custom_cookies))
custom_cookies = merge_cookies(res.cookies, custom_cookies)
print('Login OK!')
print('Cookies:' + convert_cookiejar_to_str(custom_cookies))
nav_url = 'https://api.bilibili.com/x/web-interface/nav'
res = http_get(url=nav_url, cookies=convert_cookies_to_dict(custom_cookies))
res = json.loads(res.text)
# res = json.dumps(res)  # 使用 json.dumps() 函数将 JSON 对象转换为字符串并打印
if res["code"] != 0:
    print('Login Fail')
    exit(1)
print('isLogin:' + str(res["data"]["isLogin"]))
print('uname:' + res["data"]["uname"])
print('current_face:' + res["data"]["face"])
print('current_level:' + str(res["data"]["level_info"]["current_level"]))
print('current_exp:' + str(res["data"]["level_info"]["current_exp"]))
