import subprocess
import srt
import re
from paddleocr import PaddleOCR
from PIL import Image


def assTime(x):
    ms = (x.microseconds + 5000) // 10000
    h = x.seconds // 3600
    m = (x.seconds // 60) % 60
    s = x.seconds % 60
    return "%d:%02d:%02d.%02d" % (h, m, s, ms)


def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


infile = "字幕组.mp4"
insrt = "eng.srt"

EN = []
CN = []
ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory
img_path = 'R:/test1.jpg'

subtitles = list(srt.parse(''.join(open(insrt, encoding='utf-8').readlines())))

for i in range(len(subtitles)):
    line = subtitles[i].content.replace('\n', ' ')
    line = re.sub(r'(\([^\)]+\))', '', line)  # 匹配(asdfg)
    line = re.sub(r'<([^>]+)>', '', line)  # 匹配<asdfg>
    line = re.sub(r'\[([^\]]+)\]', '', line)  # 匹配[asdfg]
    EN.append(line)
    subprocess.call('C:/FFmpeg/ffmpeg.exe -ss %s -i %s -vframes 1 -y R:/test1.jpg' % (
        subtitles[i].start.total_seconds() + 0.7, infile))
    img = Image.open("R:/test1.jpg")
    cropped = img.crop((0, 955, 1920, 1030))  # (left, upper, right, lower)
    im_new = add_margin(cropped, 100, 0, 100, 0, (0, 0, 0))
    im_new.save("R:/test1.jpg")
    result = ocr.ocr(img_path, cls=True)
    try:
        CN.append(result[0][1][0])
    except:
        CN.append("{\\识别失败\\r}"+line)

f = open('out.ass', 'w', encoding='UTF-8-sig')
f.write("""[Script Info]
ScriptType: v4.00+
ScaledBorderAndShadow: no
YCbCr Matrix: TV.601
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CN,方正黑体_GBK,22,&H00FFFFFF,&HF0000000,&H00000000,&H32000000,0,0,0,0,100,100,0,0,1,2,1,2,5,5,2,134
Style: CN2,方正黑体_GBK,20,&H00FFFFFF,&HF0000000,&H00000000,&H32000000,0,0,0,0,100,100,0,0,1,2,1,2,5,5,2,134
Style: EN,微软雅黑,14,&H00FFFFFF,&HF0000000,&H00000000,&H32000000,0,0,0,0,100,100,0,0,1,2,1,2,5,5,2,134
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")

for i in range(len(EN)):
    f.write("Dialogue: 0,%s,%s,CN,,0,0,0,,%s\\N{\\rEN}%s\n" % (
        assTime(subtitles[i].start), assTime(subtitles[i].end), CN[i],EN[i]))
f.close()