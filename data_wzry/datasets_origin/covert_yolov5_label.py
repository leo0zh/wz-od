import os
import xml.etree.ElementTree as ET
from pathlib import Path


def convert(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h


def convert_annotation(in_file, _classed_map):
    (filepath, tempfilename) = os.path.split(in_file)
    (filename, extension) = os.path.splitext(tempfilename)
    target = []
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    for obj in root.iter('object'):
        cls = obj.find('name').text
        if cls not in _classed_map:
            continue
        xml_box = obj.find('bndbox')
        b = (float(xml_box.find('xmin').text), float(xml_box.find('xmax').text), float(xml_box.find('ymin').text),
             float(xml_box.find('ymax').text))
        b1, b2, b3, b4 = b
        if b2 > w:
            b2 = w
        if b4 > h:
            b4 = h
        b = (b1, b2, b3, b4)
        bbox = convert((w, h), b)
        line = f"{_classed_map[cls]} {' '.join([str(a) for a in bbox])}"
        target.append(line)
    return filename, target


if __name__ == '__main__':

    path_anno = Path(os.path.abspath(__file__)).parent / Path("./Annotations")
    path_classes = Path(os.path.abspath(__file__)).parent / Path("./Annotations/classes.txt")
    path_photo = Path(os.path.abspath(__file__)).parent / Path("./photo")
    path_out = Path(os.path.abspath(__file__)).parent / Path("../datasets_wzry")
    path_labels = Path(path_out) / Path("./labels")
    path_images = Path(path_out) / Path("./images")

    classed_map = {}
    label_map = {}


    def get_classed():
        classed = open(path_classes).read().splitlines()
        for i in range(len(classed)):
            classed_map[classed[i]] = i


    def covert_label():
        listdir = os.listdir(path_anno)
        for name in listdir:
            if not name.endswith(".xml"):
                continue
            xml_file = Path(path_anno) / Path(name)
            filename, result = convert_annotation(xml_file, classed_map)
            label_map[filename] = result


    def write_label():
        if os.path.exists(path_out):
            os.system(f"rm -rf {path_out}")
        os.makedirs(path_labels)
        for k, v in label_map.items():
            with open(Path(path_labels) / Path(f"{k}.txt"), 'w') as f:
                f.write("\n".join(v))
        os.system(f"cp -r {path_photo} {path_images}")


    get_classed()
    print(classed_map)
    print(classed_map.keys())
    covert_label()
    write_label()
