from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import csv
import glob

def main():
	VIDEO_WIDTH = 1920
	VIDEO_HEIGHT = 1080

	sub1_pos = [324, 826, 1100, 233]
	sub2_pos = [1457, 175, 445, 215]
	sub3_pos = [1457, 423, 445, 638]

	background_img = read_background_img("background.png")
	sub1_text = read_sub_text("subs1.csv")
	sub2_text = read_sub_text("subs2.csv")
	sub3_text = read_sub_text("subs3.csv")

	video = read_video("input.mp4")
	background_music = read_background_music("background.mp3")
	sub_voice = read_sub_voice(".\\sub_voice\\*")

	sub1_time = calc_sub_time(sub1_text)
	sub2_time = calc_sub_time(sub2_text)
	sub3_time = calc_sub_time(sub3_text)

	total_time = sub1_time[-1][1]
	sub2_time[-1][1] = total_time
	sub3_time[-1][1] = total_time

	clip_video = view_background_img(background_img, VIDEO_WIDTH, VIDEO_HEIGHT, total_time)
	clip_video = view_video(clip_video, video, 0, 0, 1444, 811, total_time)
	clip_video = view_sub_text(clip_video, sub1_text, sub1_pos[0], sub1_pos[1], sub1_pos[2], sub1_pos[3], sub1_time)
	clip_video = view_sub_text(clip_video, sub2_text, sub2_pos[0], sub2_pos[1], sub2_pos[2], sub2_pos[3], sub2_time)
	clip_video = view_sub_text(clip_video, sub3_text, sub3_pos[0], sub3_pos[1], sub3_pos[2], sub3_pos[3], sub3_time)

	clip_audio = play_background_music(background_music, total_time)
	clip_audio = play_sub_voice(clip_audio, sub_voice, sub1_time)

	clip = merge_video_voice(clip_video, clip_audio)
	clip = merge_opening_video(clip)
	clip = merge_ending_video(clip)

	output_video("output.mp4", clip, light = False)

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

def read_video(str):
	return VideoFileClip(str)

def read_background_music(str):
	return AudioFileClip(str)

def read_sub_voice(str):
	return [AudioFileClip(str) for str in glob.glob(str)]

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
	sub = [[[ar_time[0], ar_time[1]], ar_text[1].replace("\\r\\n","\n")] for ar_time, ar_text in zip(sub_time, sub_text)]
	clip_sub = SubtitlesClip(sub, generator).set_position((x,y))
	return CompositeVideoClip([clip_video, clip_sub])

def view_video(clip_video, video, x, y, width, height, total_time):
	return CompositeVideoClip([clip_video, video.resize(newsize=(width,height)).set_end(total_time).set_position((x,y))])

def play_background_music(background_music, total_time):
	return afx.volumex(background_music.set_end(total_time),0.4)

def play_sub_voice(clip_audio, sub_voice, sub_time):
	ar = [clip_audio]
	[ar.append(voice.set_start(time[0])) for voice, time in zip(sub_voice, sub_time)]
	return CompositeAudioClip(ar)

def merge_video_voice(clip_video, clip_audio):
	return clip_video.set_audio(clip_audio)

def merge_opening_video(clip):
	if os.path.exists("opening.mp4"):
		clip = concatenate_videoclips([VideoFileClip("opening.mp4"), clip])
	return clip

def merge_ending_video(clip):
	if os.path.exists("ending.mp4"):
		clip = concatenate_videoclips([clip, VideoFileClip("ending.mp4")])
	return clip

def output_video(str, clip, light = True):
	if light:
		clip.write_videofile(str, threads=2, fps=1, codec = 'libx264', ffmpeg_params=["-crf","24"])
	else:
		clip.write_videofile(str, threads=2, fps=24, codec = 'libx264', ffmpeg_params=["-crf","24"])

main()
