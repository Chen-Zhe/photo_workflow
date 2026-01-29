"""监听png_heic子目录下生成的新png文件, 并将其转换为heic文件

转换出的HEIC文件稍微有点色差
需要的额外Python包: pillow, pillow-heif, watchdog
"""
import argparse
import os
import time

import PIL as pillow
import pillow_heif

import watchdog.events as watchdog_events
import watchdog.observers as watchdog_observers


parser=argparse.ArgumentParser()
parser.add_argument("--dir", help="照片目录", type=str, required=True)
args=parser.parse_args()

pillow_heif.register_heif_opener(thumbnails=False)

class Png2Heic(watchdog_events.FileSystemEventHandler):
    """Convert PNG to HEIC with full metadata read from the original JPG"""
    def __init__(self, png_dir, jpg_dir):
        super().__init__()
        self.jpg_dir = jpg_dir
        self.png_dir = png_dir

    def on_moved(self, event: watchdog_events.FileMovedEvent) -> None:
        # This specifically listens to C1's PNG rendering
        file_name_no_suffix = os.path.basename(event.dest_path)[:-4]  # remove .png suffix
        print(f"{file_name_no_suffix}处理中...")
        with pillow.Image.open(event.dest_path) as png:
            with pillow.Image.open(os.path.join(self.jpg_dir, file_name_no_suffix + ".jpg")) as jpg:
                png.save(
                    os.path.join(self.png_dir, file_name_no_suffix + ".heic"),
                    quality=70,
                    exif=jpg.info.get("exif")
                    )
        os.remove(event.dest_path)
        print(f"{file_name_no_suffix}处理完成")


png_dir = os.path.join(args.dir, "png_heic")

if not os.path.isdir(png_dir):
    os.mkdir(png_dir)

event_handler = Png2Heic(png_dir, os.path.join(args.dir, "ori_jpg"))
observer = watchdog_observers.Observer()
observer.schedule(event_handler, png_dir, recursive=False)
observer.start()
print(f"监听{png_dir}中...")
try:
    while True:
        time.sleep(1)
finally:
    observer.stop()
    observer.join()
