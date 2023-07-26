from BilibiliQRcode import BilibiliQRcode

# 示例用法
bilibili = BilibiliQRcode()
bilibili.login()
print(bilibili.get_user_info())
print(bilibili.get_sso_login(0))
