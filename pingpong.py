# Patrick McCorkell
# April 2022
# US Naval Academy
# Robotics and Control TSD
#

import board
from time import sleep, monotonic_ns
from digitalio import DigitalInOut, Direction
import pwmio
# import analogio
from sbc import SBC
from music import Music
from random import randint

class Pingpong():
	def __init__(self):
		self.mosfet = self.init_mosfet_pwm()
		# self.pwm_sanity()
		self.sensor_board = self.init_sbc()
		self.sensor = self.sensor_board._adc_device
		self.sensor.default_channel = 7

		self.intro = Music(pass_pwm=self.mosfet,auto=False)

		self.deinit_repository = [
			self.sensor_board,
			self.mosfet,
			self.intro,
			# self.sensor
		]

		random_music = randint(0,99)
		if random_music < 10:
			self.play_random_music()


	def play_random_music(self,times_to_play=1,wait_time_between=1,effort=0.3):
		self.intro.play_random(times_to_play,wait_time_between,effort)
		self.set_pwm_freq()

	def break_stall(self,effort=0.7,delay_time=2):
		self.set_pwm_freq()		# Set PWM frequency to the default.
		self.set_pwm(effort)
		sleep(delay_time)
		self.set_pwm(0)

	# v_target in Voltage, time_limit in seconds.
	def set_voltage(self,v_target=1.0,time_limit=10):
		bias = 0.35
		kp = 0.9
		ki = 0
		# ki = .18 / (10**9)
		kd = 0.0
		last_error = 0
		i_term = 0

		# Knock the pingpall ball off the bottom to break fan stall.
		self.break_stall()

		start_time = monotonic_ns()
		last_time = start_time
		end_time = start_time + (time_limit * 10**9)

		while(last_time < end_time):
			# Update our measurement
			now = monotonic_ns()
			v_meas = self.sensor.volts

			# Calculate components for PID
			error = v_target - v_meas
			dt = now - last_time

			# Calculate the PID elements
			p_term = kp * error
			i_term += ki * error * dt
			try:	# try/except to avoid Zero Division error on dt.
				d_term = kd * (error-last_error) / dt
			except ZeroDivisionError:
				d_term = 0

			# Join the PID
			duty_cycle = p_term + i_term + d_term + bias

			# Set the PWM duty cycle
			self.set_pwm(duty_cycle)

			# Serial output to Teraterm
			print(f'{v_meas:0.2f}, {error:0.2f}, {duty_cycle:0.3f}') #, %0.3f, %0.3f'.format(v_meas,error,duty_cycle))

			# Update values for the next cycle
			last_error = error
			last_time = now

			# Can run without this, but... it's already updating faster than the PWM Frequency
			sleep(0.01)


	###################################
	########### I/O Section ###########
	###################################

	def poll_sensor(self):
		return self.sensor.value / 65535

	def set_pwm(self,setval=0):
		setval*=65535
		self.mosfet.duty_cycle = int(self.clamp(setval))

	# FQP50N06L rise + fall delays = 1290ns
	#	Let's say times 100 of that for the smallest period -> 129us -> ~ 7.5kHz
	#	Quantitative playing around found that 50Hz has good response
	def set_pwm_freq(self,freq_val=50):
		self.mosfet.frequency = int(self.clamp(freq_val,0,7500))


	###################################
	########## Helper Funcs ###########
	###################################

	def clamp(self,n,minn=0,maxn=65535):
		return min(maxn,max(minn,n))

	def pwm_sanity(self,interval=0.5,val=1):
		self.set_pwm(val)
		sleep(interval)
		self.set_pwm(0)

	def digital_sanity(self,interval=0.5):
		self.mosfet_digital.value = 1
		sleep(interval)
		self.mosfet_digital.value = 0

	def tsd_iterate_up(self,delay_time):
		for i in range(512):
			self.set_pwm(i/512)
			sleep(delay_time)
			print(f'%0.6f, %0.3f' %(i/512, self.sensor.value))
			# print(f'%0.6f, %0.3f' %(i/512, 3.3 * self.sensor.value/65535))

	def tsd_iterate_down(self,delay_time):
		for i in range(512):
			j = 512 - i
			self.set_pwm(j/1024)
			sleep(delay_time)
			print(f'%0.6f, %0.3f' %((j/1024), self.sensor.value))
			# print(f'%0.6f, %0.3f' %((j/1024), 3.3 * self.sensor.value/65535))

	def tsd_profile_characteristics(self,freq=50,delay_time=0.5):
		print("tsd_profile_characteristics")

		# print(f'%0.6f, %0.3f' %((65536/65536), 3.3 * self.sensor.value/65535))
		# self.tsd_iterate_up(delay_time)

		# for _ in range(10):
		# 	self.set_pwm()
		# 	print('NEW TEST')
		# 	sleep(0.1)
		# self.tsd_iterate_down(delay_time)

		# for i in range(275,450):
		# 	self.set_pwm(0.5)
		# 	sleep(2)
		# 	self.set_pwm(i/1024)
		# 	print(f'%0.6f, %0.3f' %((i/1024), 3.3 * self.sensor.value/65535))
		# 	sleep(5)

		# for i in range(18000/16,65536/16):  #28500):
		# for i in range(270,750):  #28500):
		start = .35
		stop = .99
		resolution = 1024
		while(1):
			self.set_pwm_freq(freq)
			# self.set_pwm(0.7)

			# sleep(delay_time*3)
			self.break_stall()
			print(f'%0.3f, %0.6f' %((65536/65536), self.sensor.value))

			for i in range(int(start*resolution),int(stop*resolution)):
				self.set_pwm(i/resolution)
				print(f'%0.6f, %0.3f' %((i/resolution), self.sensor.volts))
				sleep(0.125)

			self.set_pwm(0)
			sleep(5)

		for _ in range(10):
			print('END TEST')
			self.set_pwm()
			sleep(0.1)


	###################################
	######## Init/Deinit Funcs ########
	###################################

	def init_mosfet_pwm(self):
		p_pwm = pwmio.PWMOut(pin = board.GP12, frequency = 400, variable_frequency = True)
		p_pwm.duty_cycle = 0
		return p_pwm

	def init_mosfet_digital(self):
		p26 = DigitalInOut(board.GP5)
		p26.direction = Direction.OUTPUT
		p26.value = 0
		return p26

	def init_sbc(self):
		return SBC()

	# def init_sensor(self):
	# 	# sensor = analogio.AnalogIn(board.GP27)
	# 	sensor = self.sensor_board.read_adc()
	# 	print(f"pingpong init_sensor")
	# 	sensor.default_channel = 7
	# 	return sensor

	# It's very likely this function can be called more than once depending on the quit conditions and where it was executed from.
	# Therefore, try/except each deinit action. I don't care to see the error messages, I know it was previously deinit'd.
	def deinit(self):
		for _ in range(3):
			self.set_pwm(0)
			sleep(0.2)

		for obj in self.deinit_repository:
			print('deinitializing' + str(obj))
			try:
				obj_type = type(obj)
				obj.deinit()
				print('deinitialized %s of type %s.' %(obj,obj_type))
			except Exception as e:
				print(obj)
				print(e)
				print('FAILED deinitialized %s of type %s.' %(obj,obj_type))
				pass 


