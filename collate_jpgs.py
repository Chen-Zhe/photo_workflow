"""将目录里的所有jpg文件移动到叫ori_jpg的子目录内"""
import argparse
import os

parser=argparse.ArgumentParser()

parser.add_argument("--dir", help="RAW+JPG目录", type=str, required=True)
parser.add_argument("--jpg_suffix", help="JPG文件后缀。默认为.jpg", type=str, default="jpg", required=False)
parser.add_argument("-r", help="查找下级目录内的文件", type=bool, default=False, required=False)

args=parser.parse_args()

def move_file(photo_dir):
    files = os.listdir(photo_dir)
    jpg_dir = os.path.join(photo_dir, "ori_jpg")
    jpg_count = 0

    for filename in files:
        if filename[-len(args.jpg_suffix)-1:].lower() == "." + args.jpg_suffix:
            if jpg_count == 0:
                # do not make dir if there are no JPGs to move
                os.mkdir(jpg_dir)
            os.rename(os.path.join(photo_dir, filename), os.path.join(jpg_dir, filename))
            jpg_count += 1

    if jpg_count:
        print(f"移动了{jpg_count}个文件到{jpg_dir}")
    else:
        print(f"{photo_dir}里没有找到{args.jpg_suffix}文件")

if args.r:
    for directory in os.listdir(args.dir):
        full_dir = os.path.join(args.dir, directory)
        if os.path.isdir(full_dir):
            move_file(full_dir)
else:
    move_file(args.dir)
