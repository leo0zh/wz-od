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


def mock_img(bg_img, paste_img):
    paste_img = Image.open(paste_img)
    paste_img = paste_img.convert('RGBA')

    l = random.randint(0, bg_img.size[0] - paste_img.size[0])
    t = random.randint(0, bg_img.size[1] - paste_img.size[1])

    bg_img.paste(paste_img, (l, t), mask=paste_img)

    bg_size = (bg_img.size[0], bg_img.size[1])
    label_box = (l, t, l + paste_img.size[0], t + paste_img.size[1])

    # check box
    # a = ImageDraw.ImageDraw(bg_img)
    # a.rectangle(label_box, outline='red', width=1)
    # bg_img.show()

    return bg_img, convert(bg_size, label_box)


def webp2png(source):
    img = Image.open(source).convert("RGBA")
    return img


def img_corp(img, crop_size=10):
    width, height = img.size
    left = 0
    top = 0
    right = width - crop_size
    bottom = height - crop_size
    return img.crop((left, top, right, bottom))


def img_corp_center(img, crop_size=10):
    width, height = img.size
    left = crop_size
    top = crop_size
    right = width - crop_size
    bottom = height - crop_size
    return img.crop((left, top, right, bottom))


def img_to_l(source):
    img = Image.open(source).convert('L')
    return img


def img_resize(source, size):
    w, h = size
    img = Image.open(source).resize((w, h))
    return img


def circle_img(source):
    ima = Image.open(source).convert("RGBA")
    size = ima.size
    r2 = min(size[0], size[1])
    if size[0] != size[1]:
        ima = ima.resize((r2, r2), Image.ANTIALIAS)
    r3 = int(r2 / 2)
    imb = Image.new('RGBA', (r3 * 2, r3 * 2), (255, 255, 255, 0))
    pima = ima.load()
    pimb = imb.load()
    r = float(r2 / 2)

    for i in range(r2):
        for j in range(r2):
            lx = abs(i - r)
            ly = abs(j - r)
            l = (pow(lx, 2) + pow(ly, 2)) ** 0.5
            if l < r3:
                pimb[i - (r - r3), j - (r - r3)] = pima[i, j]

    return imb


if __name__ == '__main__':
    path_base_hero = "/Users/leo/Desktop/yolo-data/hero_office"
    path_base_bg = "/Users/leo/Desktop/yolo-data/base_bg"
    # path_base_bg = "/Users/leo/Desktop/datasets_hero/newd/bg"

    path_base_output = check_dir("/Users/leo/Desktop/yolo-data/output")

    out_hero_mock = check_dir(os.path.join(path_base_output, "hero"))
    out_img = check_dir(os.path.join(path_base_output, "images"))
    out_label = check_dir(os.path.join(path_base_output, "labels"))

    heros = []


    def create_mock_base():
        for h_img in list(filter(lambda item: item.endswith(".webp"), os.listdir(path_base_hero))):
            # create dir
            webp_f = os.path.join(path_base_hero, h_img)
            filename = get_filename(webp_f)
            hero_dif = os.path.join(out_hero_mock, filename)
            os.makedirs(hero_dif)

            # p1 webp to png 原始png
            img_png = webp2png(webp_f)
            img_png_path = os.path.join(hero_dif, f"{filename}.png")
            img_png.save(img_png_path, "png")

            # p1-l 中心裁剪 中心裁剪png
            cc_l_img = img_corp(img_png)
            cc_l_img_path = os.path.join(hero_dif, f"{filename}_cc_l.png")
            cc_l_img.save(cc_l_img_path, "png")

            # p2 中心裁剪 中心裁剪png
            cc_img = img_corp_center(img_png)
            cc_img_path = os.path.join(hero_dif, f"{filename}_cc10.png")
            cc_img.save(cc_img_path, "png")

            # p2-1 中心裁剪 中心裁剪png
            # cc_img20 = img_corp_center(img_png, crop_size=14)
            # cc_img20_path = os.path.join(hero_dif, f"{filename}_cc20.png")
            # cc_img20.save(cc_img20_path, "png")

            # p3 圆角裁剪png
            c_img = circle_img(img_png_path)
            c_img_path = os.path.join(hero_dif, f"{filename}#circle.png")
            c_img.save(c_img_path, "png")

            # p4 圆角裁剪png
            c_img2 = circle_img(cc_img_path)
            c_img2_path = os.path.join(hero_dif, f"{filename}_cc#circle.png")
            c_img2.save(c_img2_path, "png")

            # p5 圆角裁剪png
            # c_img20 = circle_img(cc_img20_path)
            # c_img20_path = os.path.join(hero_dif, f"{filename}_cc20#circle.png")
            # c_img20.save(c_img20_path, "png")

            def mock_from(source_png_path):

                # resize_list = [(160, 160), (60, 60), (45, 45), (30, 30)]
                resize_list = [(60, 60), (45, 45), (30, 30)]
                for size in resize_list:
                    img = img_resize(source_png_path, size)
                    img.save(source_png_path.replace(".png", f"-{size[0]}.png"), "png")

            # mock_from(img_png_path)
            # mock_from(cc_img_path)
            mock_from(c_img_path)
            mock_from(c_img2_path)

            os.remove(img_png_path)
            os.remove(cc_l_img_path)
            os.remove(cc_img_path)

            # for file in os.listdir(hero_dif):
            #     _path = os.path.abspath(os.path.join(hero_dif, file))
            #     img = img_to_l(_path)
            #     img.save(_path.replace(".png", f"=l.png"), "png")


    def combine(count=0):
        classes_dict = dict(map(reversed, enumerate(os.listdir(out_hero_mock))))
        print("\n".join(list(classes_dict.keys())))
        print(list(classes_dict.keys()))
        print(len(list(classes_dict.keys())))
        txt_map = {}

        for hero_dir in classes_dict.keys():
            for bg_img in os.listdir(path_base_bg):
                if bg_img.endswith(".DS_Store"):
                    continue
                label_image_name_transform = f"{bg_img.replace('.jpg', f'{hero_dir}-{count}')}"
                txt_map[label_image_name_transform] = []
                label_image_path = os.path.join(path_base_bg, bg_img)

                img_bg = Image.open(label_image_path)
                pasted_img = img_bg.convert('RGBA')
                hero_dir_path = os.path.join(out_hero_mock, hero_dir)
                for i in range(0, 3):
                    for hero_img in os.listdir(hero_dir_path):
                        if bg_img.endswith(".DS_Store"):
                            continue
                        if bool(random.getrandbits(1)):
                            # gens ?
                            classes_id = classes_dict[hero_dir]
                            pasted_img, location = mock_img(pasted_img,
                                                            os.path.join(hero_dir_path, hero_img))
                            txt_map[label_image_name_transform].append(
                                f"{classes_id} {' '.join('%s' % _id for _id in location)}")
                # save pasted img
                pasted_img = pasted_img.convert("RGB")
                pasted_img.save(os.path.join(out_img, f"{label_image_name_transform}.jpg"))
                # save label txt
                open(os.path.join(out_label, f"{label_image_name_transform}.txt"), "w").write(
                    "\n".join(txt_map[label_image_name_transform]))


    create_mock_base()
    for i in range(0, 10):
        combine(i)
