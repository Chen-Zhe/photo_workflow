"""基于照片名检查JPG目录中被删除的图片, 并同时删除RAW目录中的对应图片

我最常用的功能之一。需要先运行一遍collate_jpgs.py将所有jpg文件移动进ori_jpg子目录下, 再运行这段代码。可以多次运行。
"""
import argparse
import os
import sys

CAMERA_MAKE_FILE_SUFFIXES = dict(fuji=(".raf", ".jpg"), sony=(".arw", ".jpg"), canon=(".cr2", ".jpg"), nikon=(".nef", ".jpg"))


parser=argparse.ArgumentParser()

parser.add_argument("--dir", help="RAW+JPG或RAW目录", type=str, required=True)
parser.add_argument("--jpg_dir", help="JPG目录。默认为ori_jpg", default=None, type=str, required=False)
parser.add_argument("--camera_make", help=f"相机厂商。目前仅支持：{', '.join(CAMERA_MAKE_FILE_SUFFIXES.keys())}", type=str, required=True)

args=parser.parse_args()

raw_files = os.listdir(args.dir)

if args.jpg_dir is None:
    if os.path.isdir(os.path.join(args.dir, "ori_jpg")):
        jpg_files = os.listdir(os.path.join(args.dir, "ori_jpg"))
    else:
        jpg_files = raw_files
else:
    jpg_files = os.listdir(args.jpg_dir)

if args.camera_make in CAMERA_MAKE_FILE_SUFFIXES:
    raw_suffix, jpg_suffix = CAMERA_MAKE_FILE_SUFFIXES[args.camera_make]
    raw_suffix_len = len(raw_suffix)
    jpg_suffix_len = len(jpg_suffix)
else:
    print(f"不支持的相机厂商：{args.camera_make}。目前仅支持：{', '.join(CAMERA_MAKE_FILE_SUFFIXES.keys())}")
    sys.exit(1)

raw_set = set()

for filename in raw_files:
    if filename[-raw_suffix_len:].lower() == raw_suffix:
        raw_set.add(filename[0:-raw_suffix_len])

raw_files_count = len(raw_set)
valid_jpg_files_count = 0
unmatched_jpg_count = 0

for filename in jpg_files:
    if filename[-jpg_suffix_len:].lower() == jpg_suffix:
        try:
            raw_set.remove(filename[0:-jpg_suffix_len])
            valid_jpg_files_count += 1
        except KeyError:
            print(filename[0:-jpg_suffix_len] + f"没有对应的{raw_suffix}文件")
            unmatched_jpg_count += 1


if valid_jpg_files_count <= raw_files_count and raw_files_count > 0 and unmatched_jpg_count < 0.02 * raw_files_count:
    print(f"RAW图片：{raw_files_count} | 留下：{raw_files_count - len(raw_set)} | 删除：{len(raw_set)}")

    if raw_set:
        if len(raw_set) / raw_files_count > 0.8:
            user_confirmation = input("确认执行永久删除[y/n]").strip().lower()
            if user_confirmation != "y":
                print("取消删除")
                sys.exit()
        else:
            input("按回车键执行永久删除")

        for filename in raw_set:
            os.remove(os.path.join(args.dir, f"{filename}{raw_suffix}"))
    else:
        print("没有需要删除的RAW图片")
else:
    print("遇到了一些问题！请检查目录是否正确")
