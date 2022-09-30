# Patrick McCorkell
# April 2022
# US Naval Academy
# Robotics and Control TSD
#

print("Hello " + __name__)
from pingpong import Pingpong	# Class for the lab environment
import atexit		# For error handling.
from controller import *

# Class for the lab environment.
lab = Pingpong()

###################################
######## Reset and Program ########
########## Exit Section ###########
###################################

# Self-explanatory
def reset():
	import microcontroller
	microcontroller.reset()

# Instantiate 'intro' as an integer, so that we can later check if it's been
#	reassigned to the class Music.
intro = 0
def exit_program(reason='None'):
	# Display the function exit_program was called from.
	print('exit_program called from ' + str(reason))

	# Turn the mosfet off before deinit all the objects.
	for _ in range(3):
		lab.set_pwm(0)

	# Deinit all the pin assignments from each Class.
	lab.deinit()


# Causes the registered function() to be called if the program fails for any reason,
#	or the program naturally comes to a logical conclusion.
atexit.register(exit_program)

###################################
######## Startup Section ##########
###################################
###################################

if __name__ == '__main__':
	print("running from main")
	while(1):
		controller(lab,v_target=1)
		sleep(2)
		controller(lab,v_target=2)
		sleep(2)
		lab.play_random_music()
	# lab.tsd_profile_characteristics()
	# lab.play_random_music(-1,600,0.5)


if __name__ == 'code':
	lab.play_random_music(-1,600,0.5)
	# lab.tsd_profile_characteristics()
