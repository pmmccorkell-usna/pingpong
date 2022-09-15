# Patrick McCorkell
# April 2022
# US Naval Academy
# Robotics and Control TSD
#

import board				# to get GPIO
from time import sleep		# for timing
import pwmio				# PWM
from random import randint	# Used in random playlist


class Music():
	def __init__(self,pass_pwm=None,pass_bpm=120,auto=False):
		if not pass_pwm:
			self.pwm_out = self.init_pwm()
		else:
			self.pwm_out = pass_pwm

		self.bpm = pass_bpm
		# self.update_time = 1 / (self.bpm / 120 * 64)	# 64 resolution within 1 beat
		# 									# 1/4 note = 64 

		self.init_note_lookup()

		# self.timing = Interrupt_Controller()

		# time version
		self.test_tone = [('A4',1/16)]
		# note/beats version

		self.init_score_list()

		if (auto==True):
			self.play_music(self.eva)
		
		self.deinit_repository = [
			self.pwm_out
		]

	def play_random(self,times=1,wait_time=1,effort=0.3):
		while(times):
			rando = randint(1,len(self.score_list))
			sleep(1)
			self.play_music(self.score_list[rando-1],effort)
			sleep(wait_time)
			self.off_note()
			times -= 1

	def play_repertoire(self,times=1,wait_time=10):
		while(times):
			for score in self.score_list:
				play_music(score)
				sleep(wait_time)
				self.off_note()
			times-=1


	# Translate music signature (ie 4/4) and bpm (ie 120) to units the microcontroller can use.
	def translate_note_time(self,notes_in):
		notes_out = []
		for note in notes_in:
			notes_out.append((note[0], 4*note[1] / ((self.bpm/60))))
		# print(notes_out)
		return notes_out

	# 'effort' is pwm duty cycle, normalized to [0,1]
	#	Higher efforts will cause the motor to actively spin and not play audible tones.
	#	Ideally, need enough pwm to "ring" but remain in motor stall condition.
	#	This needs to be matched against the Voltage being fed to the motor. More voltage across motor leads --> less effort.
	#	If the effort is too far away from 0.5, it may also be washed out by the mosfet delays and lose the frequency fidelity for some notes.
	#		Generally, [0.3,0.8] are acceptable for this purpose, but again: need to be matched against the Voltage.
	def play_music(self,score=[],effort=0.3):
		# If there's a score, use it. Otherwise play test tone by default.
		if score:
			music_in = score[0]
		else:
			music_in = self.test_tone

		# If there's a BPM update, implement it.
		if len(score) > 1:
			self.bpm = score[1]
			print("bpm: %d",self.bpm)

		# If there's metadata information, display it.
		if len(score) > 2:
			print("\r\nNow playing: ",end="\r\n\r\n")
			print(score[2][0])
			print("by ")
			print(score[2][1],end="\r\n\r\n")

		# Derive the glottal stop after updating bpm.
		glottal_stop_time = self.set_glottal_stop()

		# Transform note lengths (ie quarter note, eight note, etc.) into actual times related to "beats per minute".
		music_list = self.translate_note_time(music_in)

		# Iterate through the notes and play each note.
		for note in music_list:
			self.set_note(note[0],effort)
			print(note[1]*self.bpm/240)
			# Hold note for assigned length, minus the glottal stop.
			sleep(max(note[1]-glottal_stop_time,0))
			# Glottal stop between notes.
			self.off_note()
			sleep(glottal_stop_time)

	# Set glottal stop to be relative to quarter note.
	# 	Somewhat experimental, adjust to preference.
	def set_glottal_stop(self,proportional_value=0.1):
		# return = 60/self.bpm * 0.0625		# 1/64th note
		# return = 60/self.bpm * 0.125		# 1/32nd note
		# return 60/self.bpm * 0.1			# 1/40th note
		return 60/self.bpm * proportional_value

	# Use lookup table to change PWM frequency for desired note.
	def set_note(self,note_in='A4',duty=0.5):
		freq = int(self.note_lookup.get(note_in,self.default_note))
		note_exists = bool(freq)
		self.pwm_out.frequency = max(freq,1)
		duty *= note_exists
		print(note_in,freq,end=" ")
		self.pwm_out.duty_cycle = int(duty*65535)

	def off_note(self):
		self.pwm_out.duty_cycle = 0

	def deinit(self):
		for _ in range(3):
			self.off_note()
			sleep(0.2)

	def init_pwm(self):
		p22 = pwmio.PWMOut(pin = board.GP22, frequency = 440, variable_frequency = True)
		p22.duty_cycle = 0
		return p22

	def init_score_list(self):
		# https://www.musicnotes.com/sheetmusic/mtd.asp?ppn=MN0017607
		self.empire = [
			[
			('G4',1/4),('G4',1/4),('G4',1/4),('D#4',3/16),('A#4',1/16),('G4',1/4),('D#4',3/16),('A#4',1/16),('G4',1/2),('D5',1/4),('D5',1/4),('D5',1/4),('D#5',3/16),('A#4',1/16),('F#4',1/4),('D#4',3/16),('A#4',1/16),('G4',3/4)
			],
			120,	# bpm
			["The Imperial March (intro)","John Williams"]
		]
		self.empire_extended = [
			[
				('G4',1/4),('G4',1/4),('G4',1/4),('D#4',3/16),('A#4',1/16),('G4',1/4),('D#4',3/16),('A#4',1/16),('G4',1/2),('D5',1/4),('D5',1/4),('D5',1/4),('D#5',3/16),('A#4',1/16),('F#4',1/4),('D#4',3/16),('A#4',1/16),('G4',3/4),
				('G5',1/4),('G4',3/16),('G4',1/16),('G5',1/4),('F#5',3/16),('F5',1/16),('E5',1/16),('D#5',1/16),('E5',1/8),('silence',1/8),('G#4',1/8),('C#5',1/4),('B#4',3/16),('B4',1/16),('A#4',1/16),('A4',1/16),('A#4',1/8),('silence',1/8),('D#4',1/8),('F#4',1/4),('D#4',3/16),('F#4',1/16),('A#4',1/4),('G4',3/16),('A#4',1/16),('D5',1/2),('G5',1/4),('G4',3/16),('G4',1/16),('G5',1/4),('F#5',3/16),('F5',1/16),('E5',1/16),('D#5',1/16),('E5',1/8),('silence',1/8),('G4',1/8),('C#5',1/4),('B#4',3/16),('B4',1/16),('A#4',1/16),('A4',1/16),('A#4',1/8),('silence',1/8),('D#4',1/8),('F#4',1/4),('D#4',3/16),('A#4',1/16),('G4',1/4),('D#4',3/16),('A#4',1/16),('G4',1/2)
			],
			120, # bpm
			["The Imperial March (extended intro)","John Williams"]
		]

		# https://www.musicnotes.com/sheetmusic/mtd.asp?ppn=MN0245391
		self.eva = [
			[
				('C5',1/4),('D#5',1/4),('F5',3/16),('D#5',3/16),('F5',1/8),('F5',1/8),('F5',1/8),('A#5',1/8),('G#5',1/8),('G5',1/16),('F5',1/8),('G5',5/16),('G5',1/4),('A#5',1/4),('C6',1/8),('F5',3/16),('D#5',1/8),('A#5',1/8),('A#5',1/8),('G5',1/8),('A#5',1/8),('A#5',3/16),('C6',3/4)
			], #21/16)],
			140,			# bpm
			["A Cruel Angel's Thesis","Sato Hideotoshi and Omori Toshiyuki"]
		]

		# https://musescore.com/fakeyourdeath/scores/5654925
		self.great_escape = [
			[
				('Bb4',1/8),('Eb5',1/8),('silence',1/4),('silence',1/8),('Bb4',1/8),('G5',3/16),('F5',1/16),('Eb5',1/8),('C5',1/8),('silence',1/4),('silence',1/2),('F5',1/8),('F5',1/4),('Eb5',1/8),('D5',3/16),('Eb5',1/16),('D5',1/8),('C5',1/8),('Bb4',1/8),('G4',1/8),('silence',1/4),('silence',1/8),('G4',1/8),('Ab4',1/8),('A4',1/8),('Bb4',1/8),('Eb5',1/8),('silence',1/4),('silence',1/8),('Bb4',1/8),('G5',3/16),('F5',1/16),('Eb5',1/8),('C5',1/8),('silence',1/4),('silence',1/2),('F5',1/8),('F5',1/4),('Eb5',1/8),('D5',1/8),('Bb4',1/4),('F5',1/8),('Eb5',3/4)
			], #1)],
			160,		# bpm
			["The Great Escape", "Elmer Bernstein"]
		]

		self.honey = [
			[
				('D4', 1/8),('G4', 1/8),('silence', 1/2),('silence', 1/8),('D4',1/8),('Bb4',1/8),('D5',1/8),('silence', 1/2),('silence', 1/8),('D4',1/8),('D5',1/8),('E5',1/8),('F5',7/8),('G5',1/8),('E5',1/8),('D5',1/8),('C5',1/8),('silence',1/4),('G4',1/8),('D4',1/8),('G4',1/8),('silence', 1/2),('silence', 1/8),('D4',1/8),('G4',1/8),('D5',1/8),('silence', 1/2),('silence', 1/8),('D4',1/8),('D5',1/8,),('E5',1/8),('F5',7/8),('G5',1/8),('E5',1/8),('D5',1/8),('C5',1/8),('silence',1/4),('C5',1/8),('D5',1/8),('F5',1/8),('G5',1/8),('F5',1/8),('G5',7/4),('silence', 1/8),('F5',3/8),('D5',1/4),('silence',1/4),('silence', 1/8),('C5',3/8),('A4',1/4),('silence',1/4),('silence',1/2),('G4',1/4),('G4',1/4),
				#('Bb4',5/8),('silence',1/8),('C4',3/16),('F4',1/16),('silence',1/2),('silence',1/8),('C4',1/16),('F4',1/8),('C5',1/16),('silence',1/2),('silence',1/8),('F4',1/16),('C5',1/8),('D5',1/16),('Eb5',15/16),('F5',1/16),('D5',1/16),('C5',1/8),('Bb4',1/16),('silence',1/2),('C4',3/16),('F4',1/16),('silence',1/2),('silence',1/4),('C4',1/16),('F4',1/8),('C5',1/16),('silence',1/2),('silence',1/4),('F4',1/16),('C5',1/8),('D5',1/16),('Eb5',15/16),('F5',1/16),('D5',1/16),('C5',1/8),('B4',1/4),('silence',1/4),('silence',1/16),('Bb4',1/16),('C5',1/8),('Eb5',1/16),('F5',1/16),('Eb5',1/8),('F5',3/16),('C5',1/16),('D5',1/8),('C5',3/16),('Gb4',1/16),('F4',1/8),('Gb4',3/16),('silence',1/2),('silence',1/8),('Eb5',3/8),('C5',1/4)
			],
			200,	# bpm
			["A Taste of Honey", "Herb Alpert & the Tijuana Brass"]
		]

		self.score_list = [
			self.empire,
			self.empire_extended,
			self.eva,
			self.great_escape,
			self.honey,
		]


	def init_note_lookup(self):
		self.default_note = 1000
		self.note_lookup = {
			"silence" : 0,
			"C0":	16.35,
			"C#0":	17.32,
			"Db0":	17.32,
			"D0":	18.35,
			"D#0":	19.45,
			"Eb0":	19.45,
			"E0":	20.6,
			"E#0":	21.83,
			"Fb0":	20.6,
			"F0":	21.83,
			"F#0":	23.12,
			"Gb0":	23.12,
			"G0":	24.5,
			"G#0":	25.96,
			"Ab0":	25.96,
			"A0":	27.5,
			"A#0":	29.14,
			"Bb0":	29.14,
			"B0":	30.87,
			"B#0":	32.7,
			"Cb1":	30.87,
			"C1":	32.7,
			"C#1":	34.65,
			"Db1":	34.65,
			"D1":	36.71,
			"D#1":	38.89,
			"Eb1":	38.89,
			"E1":	41.2,
			"E#1":	43.65,
			"Fb1":	41.2,
			"F1":	43.65,
			"F#1":	46.25,
			"Gb1":	46.25,
			"G1":	49,
			"G#1":	51.91,
			"Ab1":	51.91,
			"A1":	55,
			"A#1":	58.27,
			"Bb1":	58.27,
			"B1":	61.74,
			"B#1":	65.41,
			"Cb2":	61.74,
			"C2":	65.41,
			"C#2":	69.3,
			"Db2":	69.3,
			"D2":	73.42,
			"D#2":	77.78,
			"Eb2":	77.78,
			"E2":	82.41,
			"E#2":	87.31,
			"Fb2":	82.41,
			"F2":	87.31,
			"F#2":	92.5,
			"Gb2":	92.5,
			"G2":	98,
			"G#2":	103.83,
			"Ab2":	103.83,
			"A2":	110,
			"A#2":	116.54,
			"Bb2":	116.54,
			"B2":	123.47,
			"B#2":	130.81,
			"Cb3":	123.47,
			"C3":	130.81,
			"C#3":	138.59,
			"Db3":	138.59,
			"D3":	146.83,
			"D#3":	155.56,
			"Eb3":	155.56,
			"E3":	164.81,
			"E#3":	174.61,
			"Fb3":	164.81,
			"F3":	174.61,
			"F#3":	185,
			"Gb3":	185,
			"G3":	196,
			"G#3":	207.65,
			"Ab3":	207.65,
			"A3":	220,
			"A#3":	233.08,
			"Bb3":	233.08,
			"B3":	246.94,
			"B#3":	261.63,
			"Cb4":	246.94,
			"C4":	261.63,
			"C#4":	277.18,
			"Db4":	277.18,
			"D4":	293.66,
			"D#4":	311.13,
			"Eb4":	311.13,
			"E4":	329.63,
			"E#4":	349.23,
			"Fb4":	329.63,
			"F4":	349.23,
			"F#4":	369.99,
			"Gb4":	369.99,
			"G4":	392,
			"G#4":	415.3,
			"Ab4":	415.3,
			"A4":	440,
			"A#4":	466.16,
			"Bb4":	466.16,
			"B4":	493.88,
			"B#4":	523.25,
			"Cb5":	493.88,
			"C5":	523.25,
			"C#5":	554.37,
			"Db5":	554.37,
			"D5":	587.33,
			"D#5":	622.25,
			"Eb5":	622.25,
			"E5":	659.25,
			"E#5":	698.46,
			"Fb5":	659.25,
			"F5":	698.46,
			"F#5":	739.99,
			"Gb5":	739.99,
			"G5":	783.99,
			"G#5":	830.61,
			"Ab5":	830.61,
			"A5":	880,
			"A#5":	932.33,
			"Bb5":	932.33,
			"B5":	987.77,
			"B#5":	1046.5,
			"Cb6":	987.77,
			"C6":	1046.5,
			"C#6":	1108.73,
			"Db6":	1108.73,
			"D6":	1174.66,
			"D#6":	1244.51,
			"Eb6":	1244.51,
			"E6":	1318.51,
			"E#6":	1396.91,
			"Fb6":	1318.51,
			"F6":	1396.91,
			"F#6":	1479.98,
			"Gb6":	1479.98,
			"G6":	1567.98,
			"G#6":	1661.22,
			"Ab6":	1661.22,
			"A6":	1760,
			"A#6":	1864.66,
			"Bb6":	1864.66,
			"B6":	1975.53,
			"B6#":	2093,
			"Cb7":	1975.53,
			"C7":	2093,
			"C#7":	2217.46,
			"Db7":	2217.46,
			"D7":	2349.32,
			"D#7":	2489.02,
			"Eb7":	2489.02,
			"E7":	2637.02,
			"E#7":	2793.83,
			"Fb7":	2637.02,
			"F7":	2793.83,
			"F#7":	2959.96,
			"Gb7":	2959.96,
			"G7":	3135.96,
			"G#7":	3322.44,
			"Ab7":	3322.44,
			"A7":	3520,
			"A#7":	3729.31,
			"Bb7":	3729.31,
			"B7":	3951.07,
			"B#7":	4186.01,
			"Cb8":	3951.07,
			"C8":	4186.01,
			"C#8":	4434.92,
			"Db8":	4434.92,
			"D8":	4698.63,
			"D#8":	4978.03,
			"Eb8":	4978.03,
			"E8":	5274.04,
			"E#8":	5587.65,
			"Fb8":	5274.04,
			"F8":	5587.65,
			"F#8":	5919.91,
			"Gb8":	5919.91,
			"G8":	6271.93,
			"G#8":	6644.88,
			"Ab8":	6644.88,
			"A8":	7040,
			"A#8":	7458.62,
			"Bb8":	7458.62,
			"B8":	7902.13
		}

