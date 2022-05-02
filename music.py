# Patrick McCorkell
# April 2022
# US Naval Academy
# Robotics and Control TSD
#

import board
from time import sleep
import pwmio
# from ticker import Interrupt_Controller


class Music():
	def __init__(self,pass_pwm=None,pass_bpm=120,auto=False):
		if not pass_pwm:
			self.pwm_out = self.init_pwm()
		else:
			self.pwm_out = pass_pwm

		self.bpm = pass_bpm	# bpm / 60 seconds -> beats per second
		self.update_time = 1 / (self.bpm / 120 * 64)	# 64 resolution within 1 beat
											# 1/4 note = 64 

		self.init_note_lookup()

		# self.timing = Interrupt_Controller()

		# https://www.musicnotes.com/sheetmusic/mtd.asp?ppn=MN0017607
		# time version
		self.test_tone = [('A4',0.25)]
		# note/beats version

		self.empire = [('G4',1/4),('G4',1/4),('G4',1/4),('D#4',3/16),('A#4',1/16),('G4',1/4),('D#4',3/16),('A#4',1/16),('G4',1/2),('D5',1/4),('D5',1/4),('D5',1/4),('D#5',3/16),('A#4',1/16),('F#4',1/4),('D#4',3/16),('A#4',1/16),('G4',3/4)]

		if (auto==True):
			self.play_music()
		
		self.deinit_repository = [
			self.pwm_out
		]



	def translate_note_time(self,notes_in):
		notes_out = []
		for note in notes_in:
			notes_out.append((note[0], 4*note[1] / ((self.bpm/60))))
		# print(notes_out)
		return notes_out

	def play_music(self,music_in=None):
		if not music_in:
			# music_in = self.test_tone
			music_in = self.empire
		music_list = self.translate_note_time(music_in)
		# print(music_list)
		for note in music_list:
			# print(note)	
			self.set_note(note[0])
			sleep(note[1]-0.05)
			self.off_note()
			sleep(0.05)

	def set_note(self,note_in='A4',duty=0.3):
		# print(note_in,duty)
		self.pwm_out.frequency = int(self.note_lookup.get(note_in,self.default_note))
		self.pwm_out.duty_cycle = int(duty*65535)

	def off_note(self):
		self.pwm_out.duty_cycle = 0


	def deinit_all(self):
		for _ in range(3):
			self.off_note()
			sleep(0.2)

	def init_pwm(self):
		p22 = pwmio.PWMOut(pin = board.GP22, frequency = 440, variable_frequency = True)
		p22.duty_cycle = 0
		return p22

	def init_note_lookup(self):
		self.default_note = 1000
		self.note_lookup = {
			"C0":	16.35,
			"C#0":	17.32,
			"D0":	18.35,
			"D#0":	19.45,
			"E0":	20.6,
			"F0":	21.83,
			"F#0":	23.12,
			"G0":	24.5,
			"G#0":	25.96,
			"A0":	27.5,
			"A#0":	29.14,
			"B0":	30.87,
			"C1":	32.7,
			"C#1":	34.65,
			"D1":	36.71,
			"D#1":	38.89,
			"E1":	41.2,
			"F1":	43.65,
			"F#1":	46.25,
			"G1":	49,
			"G#1":	51.91,
			"A1":	55,
			"A#1":	58.27,
			"B1":	61.74,
			"C2":	65.41,
			"C#2":	69.3,
			"D2":	73.42,
			"D#2":	77.78,
			"E2":	82.41,
			"F2":	87.31,
			"F#2":	92.5,
			"G2":	98,
			"G#2":	103.83,
			"A2":	110,
			"A#2":	116.54,
			"B2":	123.47,
			"C3":	130.81,
			"C#3":	138.59,
			"D3":	146.83,
			"D#3":	155.56,
			"E3":	164.81,
			"F3":	174.61,
			"F#3":	185,
			"G3":	196,
			"G#3":	207.65,
			"A3":	220,
			"A#3":	233.08,
			"B3":	246.94,
			"C4":	261.63,
			"C#4":	277.18,
			"D4":	293.66,
			"D#4":	311.13,
			"E4":	329.63,
			"F4":	349.23,
			"F#4":	369.99,
			"G4":	392,
			"G#4":	415.3,
			"A4":	440,
			"A#4":	466.16,
			"B4":	493.88,
			"C5":	523.25,
			"C#5":	554.37,
			"D5":	587.33,
			"D#5":	622.25,
			"E5":	659.25,
			"F5":	698.46,
			"F#5":	739.99,
			"G5":	783.99,
			"G#5":	830.61,
			"A5":	880,
			"A#5":	932.33,
			"B5":	987.77,
			"C6":	1046.5,
			"C#6":	1108.73,
			"D6":	1174.66,
			"D#6":	1244.51,
			"E6":	1318.51,
			"F6":	1396.91,
			"F#6":	1479.98,
			"G6":	1567.98,
			"G#6":	1661.22,
			"A6":	1760,
			"A#6":	1864.66,
			"B6":	1975.53,
			"C7":	2093,
			"C#7":	2217.46,
			"D7":	2349.32,
			"D#7":	2489.02,
			"E7":	2637.02,
			"F7":	2793.83,
			"F#7":	2959.96,
			"G7":	3135.96,
			"G#7":	3322.44,
			"A7":	3520,
			"A#7":	3729.31,
			"B7":	3951.07,
			"C8":	4186.01,
			"C#8":	4434.92,
			"D8":	4698.63,
			"D#8":	4978.03,
			"E8":	5274.04,
			"F8":	5587.65,
			"F#8":	5919.91,
			"G8":	6271.93,
			"G#8":	6644.88,
			"A8":	7040,
			"A#8":	7458.62,
			"B8":	7902.13
		}

