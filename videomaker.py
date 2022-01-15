import tqdm
import subprocess

from generate_map import *

LENGTH_LIMIT = 1 * 60 + 40

END_CAR_LENGTH_EACH = 3


dates = sorted(set(load_statistics()))

FRAMERATE = len(dates) / (LENGTH_LIMIT - 2 * END_CAR_LENGTH_EACH)

subprocess.check_call("mkdir -p outputs", shell=True)
for date in tqdm.tqdm(dates):
    #     generate_map(date)
    continue

os.system(f"cp outputs/{date}.png outputs/slide_1.png")
os.system(
    'inkscape --export-type="png" slide.svg --export-filename=outputs/slide_2.png'
)
subprocess.check_call(
    f"ffmpeg -framerate {FRAMERATE} -pattern_type glob -i 'outputs/20*.png' "
    "-c:v libx264 -r 30 -pix_fmt yuv420p outputs/main.mp4",
    shell=True,
)
subprocess.check_call(
    f"ffmpeg -framerate 1/{END_CAR_LENGTH_EACH} -pattern_type glob -i "
    "'outputs/slide*.png' -c:v libx264 -r 30 -pix_fmt yuv420p outputs/end_credits.mp4",
    shell=True,
)
subprocess.check_call(
    [
        "bash",
        "-c",
        "(echo file 'outputs/main.mp4' ; echo file 'outputs/end_credits.mp4')"
        + " | ffmpeg -protocol_whitelist file,pipe -f concat -safe 0 -i pipe:"
        + " -vcodec copy -acodec copy outputs/without_music.mp4",
    ],
)
subprocess.check_call(
    f"ffmpeg -i outputs/without_music.mp4 -i SSB.ogg -map 0:v -map 1:a -c:v copy outputs/final.mp4",
    shell=True,
)
