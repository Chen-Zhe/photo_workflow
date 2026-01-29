"""如果目录里有过多的大图片(>5MB), 将重新把所有图片重压缩为80%质量的jpg

需要的额外Python包: pillow
"""
import argparse
import multiprocessing
import os
from PIL import Image


LARGE_FILE_SIZE = 5 * 1024 * 1024  # 5MB
SUPPORTED_IMG_SUFFIX = (".jpg", ".jpeg", ".png")

parser=argparse.ArgumentParser()
parser.add_argument("--dir", help="照片目录", type=str, required=True)
parser.add_argument("-r", help="查找下级目录内的文件", type=bool, default=False, required=False)
parser.add_argument("--dry_run", help="只检测，不处理文件", type=bool, default=False, required=False)


def is_file_a_supported_img(filename: str):
    for suffix in SUPPORTED_IMG_SUFFIX:
        if filename[-len(suffix):].lower() == suffix:
            return True, filename[:-len(suffix)]
    return False, ""


def _compress(args):
    photo_dir, filename, file_name_no_suffix = args
    full_file_path = os.path.join(photo_dir, filename)

    with Image.open(full_file_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.save(
            os.path.join(photo_dir, f"c_{file_name_no_suffix}.jpg"),
            quality=80,
            )
    os.remove(full_file_path)


def compress_photo_dir(photo_dir, dry_run):
    files = os.listdir(photo_dir)
    imgs_to_compress = []
    num_large_imgs = 0

    for filename in files:
        supported, file_name_no_suffix = is_file_a_supported_img(filename)
        if supported:
            imgs_to_compress.append((photo_dir, filename, file_name_no_suffix))
            if os.path.getsize(os.path.join(photo_dir, filename)) > LARGE_FILE_SIZE:
                num_large_imgs += 1

    if len(imgs_to_compress) * 0.7 <= num_large_imgs:
        if not dry_run:
            with multiprocessing.Pool(processes=16) as pool:
                pool.map(_compress, imgs_to_compress)
        print(f"{photo_dir}里共{len(imgs_to_compress)}个文件被压缩")
    elif num_large_imgs == 0:
        print(f"{photo_dir}里没有大文件")
    else:
        print(f"{photo_dir}里大文件较少 ({num_large_imgs}/{len(imgs_to_compress)})")


if __name__ == "__main__":
    args=parser.parse_args()

    if args.r:
        for directory in os.listdir(args.dir):
            full_dir = os.path.join(args.dir, directory)
            if os.path.isdir(full_dir):
                compress_photo_dir(full_dir, args.dry_run)
    else:
        compress_photo_dir(args.dir, args.dry_run)
