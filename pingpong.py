# Patrick McCorkell
# April 2022
# US Naval Academy
# Robotics and Control TSD
#

import board
from time import sleep
from digitalio import DigitalInOut, Direction
import pwmio
import analogio


class Pingpong():
	def __init__(self):
		self.mosfet = self.init_mosfet_pwm()
		# self.pwm_sanity()
		self.sensor = self.init_sensor()

		self.deinit_repository = [
			self.mosfet,
			self.sensor
		]



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
		for i in range(65535):
			self.set_pwm(i/65535)
			sleep(delay_time)
			print(f'%0.6f, %0.3f' %(i/65535, self.sensor.value/65535))

	def tsd_iterate_down(self,delay_time):
		for i in range(65535):
			j = 65535 - i
			self.set_pwm(j/65535)
			sleep(delay_time)
			print(f'%0.6f, %0.3f' %((j/65535), self.sensor.value/65535))

	def tsd_profile_characteristics(self,freq=50,delay_time=0.5):
		self.set_pwm_freq(freq)

		self.tsd_iterate_up(delay_time)

		for _ in range(10):
			self.set_pwm()
			print('NEW TEST')
			sleep(0.1)
		self.tsd_iterate_down(delay_time)

		for _ in range(10):
			print('END TEST')
			self.set_pwm()
			sleep(0.1)



	###################################
	######## Init/Deinit Funcs ########
	###################################

	def init_mosfet_pwm(self):
		p22_pwm = pwmio.PWMOut(pin = board.GP22, frequency = 400, variable_frequency = True)
		p22_pwm.duty_cycle = 0
		return p22_pwm

	def init_mosfet_digital(self):
		p22 = DigitalInOut(board.GP22)
		p22.direction = Direction.OUTPUT
		p22.value = 0
		return p22

	def init_sensor(self):
		p28 = analogio.AnalogIn(board.GP28)
		return p28

	# It's very likely this function can be called more than once depending on the quit conditions and where it was executed from.
	# Therefore, try/except each deinit action. I don't care to see the error messages, I know it was previously deinit'd.
	def deinit_all(self):
		for _ in range(3):
			self.set_pwm(0)
			sleep(0.2)

		for obj in self.deinit_repository:
			# print('deinitializing' + str(obj))
			try:
				obj.deinit()
			except:
				pass


