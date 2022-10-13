"""
参考来自：https://github.com/alishtory/qrcode-terminal
"""
import qrcode

white_block = "\033[0;37;47m  "
black_block = "\033[0;37;40m  "
new_line = "\033[0m\n"


def draw_qrcode(url: str, version=1):
    """
    说明:
        控制台画出二维码

    参数:
        * `url`：二维码链接
        * `version`：二维码版本
            * `1`：Small大小
            * `3`：Middle大小
            * `5`：Large大小
    """
    qr = qrcode.QRCode(version)
    qr.add_data(url)
    qr.make()
    output = white_block * (qr.modules_count + 2) + new_line
    for mn in qr.modules:
        output += white_block
        for m in mn:
            if m:
                output += black_block
            else:
                output += white_block
        output += white_block + new_line
    output += white_block * (qr.modules_count + 2) + new_line
    print(output)
