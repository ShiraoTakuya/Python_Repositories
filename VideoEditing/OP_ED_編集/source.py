from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import csv
import glob

def main():
	VIDEO_WIDTH = 1920
	VIDEO_HEIGHT = 1080

	sub1_pos = [0, 0, 1920, 1080]

	background_img = read_background_img("background.png")
	sub1_text = read_sub_text("subs1.csv")

	sub1_time = calc_sub_time(sub1_text)

	total_time = sub1_time[-1][1]

	clip_video = view_background_img(background_img, VIDEO_WIDTH, VIDEO_HEIGHT, total_time)
	clip_video = view_sub_text(clip_video, sub1_text, sub1_pos[0], sub1_pos[1], sub1_pos[2], sub1_pos[3], sub1_time)

	output_video("output.mp4", clip_video, light = False)

def read_csv(st):
	fCSV = open(st, 'r', encoding='utf-8')
	csvData = csv.reader(fCSV)
	csvHeader = next(csvData)
	arCSV = []
	for row in csvData:
		arCSV.append(row)
	return arCSV

def read_background_img(str):
	return ImageClip(str)

def read_sub_text(str):
	return read_csv(str)

def calc_sub_time(sub_text):
	arr = []
	total_time = 0
	for ar in sub_text:
		if ar[3] != "":
			total_time = float(ar[3])
		arr.append([total_time, total_time+float(ar[2])])
		total_time += float(ar[2])
	return arr

def view_background_img(background_img, VIDEO_WIDTH, VIDEO_HEIGHT, total_time):
	return background_img.set_duration(total_time).resize(newsize=(VIDEO_WIDTH,VIDEO_HEIGHT))

def view_sub_text(clip_video, sub_text, x, y, width, height, sub_time):
	generator = lambda txt: TextClip(txt, size = (width*1,height), bg_color = 'black', color = 'white', stroke_color="white", stroke_width=2, font='MS-Mincho-&-MS-PMincho')
	sub = [[[ar_time[0], ar_time[1]], ar_text[1].replace("\\n","\n")] for ar_time, ar_text in zip(sub_time, sub_text)]
	clip_sub = SubtitlesClip(sub, generator).set_position((x,y))
	return CompositeVideoClip([clip_video, clip_sub])

def output_video(str, clip, light = True):
	if light:
		clip.write_videofile(str, threads=2, fps=1, codec = 'libx264', ffmpeg_params=["-crf","24"])
	else:
		clip.write_videofile(str, fps=24)

main()
