from PIL import Image
from io import BytesIO
import numpy as np
import requests, cv2, os

# 头像地址，改成要找的vup的
avatar_url = 'http://i0.hdslb.com/bfs/face/b4f8aa684de372e8037f145601bac4e3d86b2e0a.jpg'

# 标记前几个相似的，默认20个
layout_cnt = 20

# 以下不用改

print('Cut Avatars...')
image = Image.open('orig.JPG')

avatar_cut = []

x_cnt = int((6000 - 78) / 126 + 1)
y_cnt = int((6000 - 78) / 94 + 1)

for x_pos in range(0, x_cnt):
    for y_pos in range(0, y_cnt):
        x_start = 126 * x_pos
        if x_pos == x_cnt - 1:
            x_length = 78
        else:
            x_length = 126

        y_start = 94 * y_pos
        if y_pos == y_cnt - 1:
            y_length = 78
        else:
            y_length = 94

        image_box = image.crop((x_start, y_start, x_start + x_length, y_start + y_length))
        avatar_cut.append({
            'x_start': x_start,
            'y_start': y_start,
            'x_end': x_start + x_length,
            'y_end': y_start + y_length,
            'img': image_box
        })
print('Cut Avatars Success')

res = requests.get(avatar_url, stream=True)
if res.status_code != 200:
    print('Get Avatar Url Error')
    exit()
vup = Image.open(BytesIO(res.content))
vup.resize((126, 126), Image.ANTIALIAS).crop((0, 24, 126, 102))
print('Fetch Avatar Success')


# calculate hamming distance
def d_hash(img):
    img = cv2.resize(img, (65, 64))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hash_str = ''
    for i in range(64):
        for j in range(64):
            if gray[i, j] > gray[i, j + 1]:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str


def hamming_distance(hash1, hash2):
    n = 0
    if len(hash1) != len(hash2):
        return -1
    for i in range(len(hash1)):
        if hash1[i] != hash2[i]:
            n = n + 1
    return n


hash_vup = d_hash(cv2.cvtColor(np.asarray(vup), cv2.COLOR_RGB2BGR))

print('Calculating Hash...')
results = []
for cut in avatar_cut:
    img = cv2.cvtColor(np.asarray(cut['img']), cv2.COLOR_RGB2BGR)
    dist = hamming_distance(hash_vup, d_hash(img))
    results.append((dist, cut))

results = sorted(results, key=lambda x: x[0])
print('Calculate Success')

ly = Image.open('orig.JPG', 'r')
b = (0, 255, 0)
for r in results[:layout_cnt]:
    for x in range(r[1]['x_start'], r[1]['x_end']):
        for y in range(r[1]['y_start'], r[1]['y_end']):
            p = ly.getpixel((x, y))
            p = [int(p[i]*0.5+b[i]*0.5) for i in range(3)]
            ly.putpixel((x, y), tuple(p))

ly.save('layout.jpg')

print('Export Success')
