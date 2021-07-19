import os
import random
import shutil

from PIL import Image, ImageDraw


def get_filename(f):
    (filepath, tempfilename) = os.path.split(f)
    (filename, extension) = os.path.splitext(tempfilename)
    return filename


def check_dir(f):
    if os.path.exists(f):
        shutil.rmtree(f)
    os.makedirs(f)
    return f


def webp2jpg(source):
    im = Image.open(source).convert("RGB")
    im.save(source.replace("webp", "jpg"), "jpeg")


def convert(size, box):
    bg_w, bg_h = size
    l, t, r, b = box
    dw = 1. / bg_w
    dh = 1. / bg_h
    x = (l + r) / 2.0 - 1
    y = (t + b) / 2.0 - 1
    w = r - l
    h = b - t
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h


def mock_img(source, bg):
    img_bg = Image.open(bg)
    img_bg = img_bg.convert('RGBA')

    img_source = Image.open(source)
    img_source = img_source.convert('RGBA')

    l = random.randint(0, img_bg.size[0] - img_source.size[0])
    t = random.randint(0, img_bg.size[1] - img_source.size[1])

    img_bg = img_bg.convert("RGB")
    img_bg.paste(img_source, (l, t), mask=None)

    bg_size = (img_bg.size[0], img_bg.size[1])
    label_box = (l, t, l + img_source.size[0], t + img_source.size[1])
    # check box
    a = ImageDraw.ImageDraw(img_bg)
    a.rectangle(label_box, outline='red', width=1)
    img_bg.show()

    return img_bg, convert(bg_size, label_box)


if __name__ == '__main__':
    path_base_hero = "/Users/leo/Desktop/datasets_hero/newd/hero"
    path_base_bg = "/Users/leo/Desktop/datasets_hero/newd/bg"
    path_base_output = "/Users/leo/Desktop/datasets_hero/newd/output"
    out_img = check_dir(os.path.join(path_base_output, "images"))
    out_label = check_dir(os.path.join(path_base_output, "labels"))

    heros = []

    for h_img in os.listdir(path_base_hero):
        if not h_img.endswith("jpg"):
            continue
        for bg_img in os.listdir(path_base_bg):
            if not bg_img.endswith("jpg"):
                continue
            hero = os.path.join(path_base_hero, h_img)
            bg = os.path.join(path_base_bg, bg_img)
            hero_name = get_filename(hero)
            img_name = f"{hero_name}-{get_filename(bg)}.jpg"

            img, location = mock_img(hero, bg)
            img.save(os.path.join(out_img, img_name))

            if hero_name not in heros:
                heros.append(hero_name)
            classes_id = len(heros) - 1
            label_name = f"{hero_name}-{get_filename(bg)}.txt"
            content = f"{classes_id} {' '.join('%s' % _id for _id in location)}"
            open(os.path.join(out_label, label_name), "w").write(content)
    open(os.path.join(path_base_output, "classes.txt"), "w").write("\n".join(heros))
