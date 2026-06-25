import requests, json, os
BASE='http://127.0.0.1:5000'
img_path=os.path.abspath('uploads/13a2cdb3971444f18a75c207ee5552a2.jpg')
files={'image': open(img_path,'rb')}
resp=requests.post(f'{BASE}/predict', files=files)
print('status', resp.status_code)
print('len', len(resp.text))
# find img src
import re
m = re.search(r'<img[^>]+src="([^"]+/uploads/[^\"]+)"', resp.text)
if m:
    print('IMG_SRC', m.group(1))
else:
    print('NO IMG')
