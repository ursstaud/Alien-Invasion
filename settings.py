class Settings:
	"""a class to store all the settings for the Alien Invasion game"""

	def __init__(self):
		"""initialize the game's static settings"""
		self.screen_width = 1200
		self.screen_height = 800
		self.bg_color = (124, 185, 232) 

		#ship settings
		self.ship_limit = 2

		#bullet settings
		self.bullet_width = 3
		self.bullet_height = 15
		self.bullet_color = (60, 60, 60)
		self.bullets_allowed = 3

		#alien settings
		self.fleet_drop_speed = 50

		#how quickly the game speeds up
		self.speedup_scale = 1.1
		self.score_scale = 1.5

		self.initialize_dynamic_settings()


	def initialize_dynamic_settings(self):
		"""Settings that change throughout the game"""
		self.ship_speed = 4.0
		self.bullet_speed = 5.0
		self.alien_speed = 1.0

		#fleet direction, -1 is left
		self.fleet_direction = 1

		#scoring
		self.alien_points = 50

	def increase_speed(self):
		"""increase the pace of the game"""
		self.ship_speed *= self.speedup_scale
		self.bullet_speed *= self.speedup_scale
		self.alien_speed *= self.speedup_scale

		self.alien_points = int(self.alien_points * self.score_scale)

		
		