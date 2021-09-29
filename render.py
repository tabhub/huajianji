# -*- coding: utf-8 -*-
import jinja2
import random
import os, json
import sys
from uuid import uuid4
from os.path import splitext
from collections import defaultdict
from datetime import datetime
#from pagination import Pagination

version = uuid4().hex


template_loader = jinja2.FileSystemLoader(searchpath="templates")
template_env = jinja2.Environment(loader=template_loader)
WORD_TEMPLATE_FILE = "detail.html"
images = json.loads(open('config/images.json', 'r', encoding='utf-8').read())
imageMaps = {x['src']: x for x in images}
specify = json.loads(open('config/specify_cover.json').read())


if os.path.exists('.image.json'):
    with open('.image.json', 'r', encoding="utf-8") as f:
        image_map = json.loads(f.read())
else:
    image_map = {}


def get_image(_id):
    global image_map
    if _id in specify:
        image = imageMaps.get(specify[_id], None)
        if image:
            return image

    if _id in image_map:
        return image_map[_id]
    else:
        image = random.choice(images)
        image_map[_id] = image
        return image

dirs = {
        '花间集':  ('赵崇祚', 'huajianji'),
        '南唐二主词': ('李煜 李璟', 'erzhuci'),
        '唐诗三百首': ('蘅塘退士', 'tangshi300'),
        '宋词三百首': ('', 'songci300'),
        '教科书选诗': ('教科书出版社\n包含人民教育出版社、江苏教育出版社等', 'jks_shixuan'),
        '古诗十九首': ('无名氏', 'gushi19'),
        '诗经': ('佚名', 'shijing'),
        '千家诗': ('南宋·謝枋得\n明代·王相', 'qianjiashi'),
        '声律启蒙':  ('清·车万育', 'shenglvqimeng'),
        '三字经': ('王應麟', 'sanzijing'),
        '唐诗三百首·蒙学': ('清代·蘅塘退士', 'tangshi300mengxue'),
        }

paths = []

for name, info in dirs.items():
    pfiles = os.listdir(u'./data/%s/' % name)

    for pfile in pfiles:
        if 'json' not in pfile:
            continue

        if 'author' in pfile:
            continue

        path = os.path.join(u'./data/%s/' % name, pfile)
        juan = pfile.split('.')[1]
        paths.append((name, path, juan))


books = defaultdict(list)
tabhub = {}

for book, path, juan in paths:

    books[(book, dirs[book][0])].append(juan)

    with open(path, 'r', encoding="utf-8") as f:
        content = f.read()

    poetrys = json.loads(content)
    for poetry in poetrys:
        notes = []

        poetry["id"] = str(hash(juan + poetry["title"])).replace('-','')

        note_items = poetry.get('notes', [])

        for note in note_items:
            if '--' in note:
                left, right = note.split('--')
            elif '-' in note:
                left, right = note.split('-')
            else:
                left, right = '1', right

            first = left[0]
            if first.isdigit():
                left = left.replace(first, '').replace('.', '')

            first = right[0]
            if first.isdigit():
                right  = right.replace(first, '').replace('.', '')
            notes.append((left, right))

        poetry["notes"] = notes

        root = '../../'
        image = get_image(poetry["id"])
        template = template_env.get_template(WORD_TEMPLATE_FILE)
        output = template.render(poetry=poetry, juan=juan, image=image, root=root)

        html_filename = 'www/poetrys/%s.html' % poetry["id"]

        with open(html_filename, 'w', encoding="utf-8") as f:
             f.write(output)

        item = {"name": "%s" % poetry["id"],
                "type": "tabhub-app",
                "url": "https://tabhub.io/huajianji/www/poetrys/%s.html" % poetry["id"]}
        if book in tabhub:
            tabhub[book].append(item)
        else:
            tabhub[book] = [item]


    root = '../../'
    image = get_image(juan)
    template = template_env.get_template('list.html')
    output = template.render(poetrys=poetrys, juan=juan, image=image, root=root, book=book)
    with open('www/list/%s.html' % juan, 'w', encoding="utf-8") as f:
        f.write(output)

for book, its in tabhub.items():
    pinyin = dirs[book][1]
    r = {"name": book, "type": "resource", "version": "1.0", "items": its}
    with open('tabhub/%s.json' % pinyin, 'w', encoding="utf-8") as f:
        f.write(json.dumps(r, indent=2, ensure_ascii=False))
    print("[%s](https://raw.githubusercontent.com/tabhub/huajianji/master/tabhub/%s.json)" % (book, pinyin))

for book, juans in books.items():
    root = '../'
    image = get_image(str(hash(book[0])).replace('-', ''))
    template = template_env.get_template('book.html')
    output = template.render(book=book, juans=juans, image=image, root=root)

    with open('www/%s.html' % book[0], 'w', encoding="utf-8") as f:
        f.write(output)

root = './'
image = get_image('index')
template = template_env.get_template('index.html')
output = template.render(books=books, image=image, author="", root=root)
with open('index.html' ,'w', encoding="utf-8") as f:
    f.write(output)


with open('.image.json', 'w', encoding="utf-8") as f:
    f.write(json.dumps(image_map, indent=2, ensure_ascii=False))

