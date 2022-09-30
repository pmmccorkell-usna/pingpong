from time import sleep, monotonic_ns

#
# CHANGE THIS TO SELECT P, PI, or PID
#
active_loop_func = 'p'


###################################
########## PID FUNCTIONS ##########
###################################
###################################

i_term = 0
last_error = 0

def p(dt,error):
	global i_term,last_error
	bias = 0.35
	kp = 0.9

	p_term = kp * error
	i_term += 0
	d_term = 0

	return p_term + i_term + d_term + bias


def pi(dt,error):
	global i_term,last_error
	bias = 0.35
	kp = 0.9
	ki = 0.18 / (10**9)

	p_term = kp * error
	i_term += ki * error * dt
	d_term = 0

	return p_term + i_term + d_term + bias


def pid(dt,error):
	global i_term,last_error
	bias = 0.35
	kp = 0.9
	ki = 0.18 / (10**9)
	kd = 0.0

	p_term = kp * error
	i_term += ki * error * dt
	d_term = kd * (error-last_error) / dt

	return p_term + i_term + d_term + bias



###################################
####### Controller Section ########
###################################
###################################

# Create a list of the controller functions.
controller_list = {
	'p':p,
	'pi':pi,
	'pid':pid
}


def controller(pingpong_lab,v_target = 1.0,time_limit = 10):
	global i_term,last_error

	# Assign the controller function being used.
	# 	If "active_loop_func" doesn't point at a valid key, it will substitute the P controller.
	active_controller = controller_list.get(active_loop_func,p)

	# Zero out memory terms for I and D.
	i_term = 0
	last_error = 0

	# Break the pingpong ball off the bottom.
	pingpong_lab.break_stall()

	# Initiate times.
	start_time = monotonic_ns()
	last_time = start_time
	end_time = start_time + (time_limit * 10**9)

	# Run the control loop for the duration of the time limit.
	while (last_time < end_time):

		# Immediately update the time and sensor measurement.
		now = monotonic_ns()
		v_meas = pingpong_lab.sensor.volts

		# Calculate error and dt.
		error_val = v_target - v_meas
		dt_val = max(now - last_time,1/10**9)	# use max() to avoid 0 Division errors. If dt=0, then set it to 1 ns.

		# Poll the appropriate controller for duty cycle.
		duty_cycle = active_controller(dt_val,error_val)

		# Set the duty cycle.
		pingpong_lab.set_pwm(duty_cycle)

		# Print error and duty cycle to serial.
		print(error_val,duty_cycle)

		# Update memory aspects of I and D.
		last_error = error_val
		last_time = now

		# Can run without this, but... it's already updating faster than the PWM Frequency
		sleep(0.01)

	# After the time limit has expired, set the pwm  duty cycle to 0.
	pingpong_lab.set_pwm(0)

