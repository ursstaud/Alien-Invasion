import sys
from time import sleep
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
	"""Overall class to mamage game assets and behaviors"""

	def __init__(self):
		"""initialize the game and create game resources"""
		#setup
		pygame.init()
		self.settings = Settings()
		self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
		self.settings.screen_width = self.screen.get_rect().width 
		self.settings.screen_height = self.screen.get_rect().height
		pygame.display.set_caption("Alien Invasion")

		#create instances of classes imported
		self.stats = GameStats(self)
		self.ship=Ship(self)
		self.bullets = pygame.sprite.Group() 
		self.aliens = pygame.sprite.Group() 
		self.sb = Scoreboard(self)
		self.play_button = Button(self, "Play")

		#create the fleet of aliens
		self._create_fleet() 
		
		#name the highscore text file
		self.high_score_txt = 'highscore.txt'


	def run_game(self):
		"""start the main loop for the game"""
		while True:
			self._check_events() 

			#steps only run if the game is active
			if self.stats.game_active:
				self.ship.update() 
				self._update_bullets() 
				self._update_aliens() 
			
			self._update_screen() 


	def _update_bullets(self):
		"""update position of bullets and get rid of old bullets"""
		self.bullets.update() 
			
		#Get rid of bullets that have disappeared
		for bullet in self.bullets.copy():
			if bullet.rect.bottom <= 0:
				self.bullets.remove(bullet)

		self._check_bullet_alien_collisions()


	def _update_aliens(self):
		"""check if the fleet is at an edge, 
		then update the positions of all aliens in the fleet"""
		self._check_fleet_edges()
		self.aliens.update() 

		#look for alien-ship collisions
		if pygame.sprite.spritecollideany(self.ship, self.aliens):
			self._ship_hit()

		#look for aliens hitting the bottom of the screen
		self._check_aliens_bottom()


	def _check_bullet_alien_collisions(self):
		"""respond to bullet-alien collisions"""
		#remove any bullets and aliens that have collided
		#check for bullets that have hit aliens, if so, get rid of both
		collisions = pygame.sprite.groupcollide(
			self.bullets, self.aliens, True, True) 

		if collisions:
			for aliens in collisions.values():
				self.stats.score += self.settings.alien_points * len(aliens)
			self.sb.prep_score()
			self.sb.check_high_score()

		if not self.aliens: #checking to see if the alien group is empty
			#destroy existing bullets and create a new fleet
			self.bullets.empty()
			self._create_fleet()
			self.settings.increase_speed()

			#increase level
			self.stats.level += 1
			self.sb.prep_level()


	def _check_events(self): 
		"""respond to keyboard/mouse events"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = pygame.mouse.get_pos() 
				self._check_play_button(mouse_pos) 
			elif event.type == pygame.KEYDOWN: 
				self._check_keydown_events(event)
			elif event.type == pygame.KEYUP: 
				self._check_keyup_events(event)


	def _check_keydown_events(self, event): 
		"""respond to keypresses"""
		if event.key == pygame.K_RIGHT: 
			self.ship.moving_right = True 
		elif event.key == pygame.K_LEFT:
			self.ship.moving_left = True
		elif event.key == pygame.K_q:
			sys.exit()
		elif event.key == pygame.K_SPACE:
			self._fire_bullet()


	def _check_keyup_events(self,event): #this is a helper method
		"""respond to key releases"""
		if event.key == pygame.K_RIGHT: 
			self.ship.moving_right = False 
		elif event.key == pygame.K_LEFT:
			self.ship.moving_left = False


	def _check_aliens_bottom(self):
		"""check if any aliens have reached the bottom of the screen"""
		screen_rect = self.screen.get_rect()
		for alien in self.aliens.sprites():
			if alien.rect.bottom >= screen_rect.bottom:
				#treat this the same as if the ship got hit
				self._ship_hit()
				break


	def _check_play_button(self, mouse_pos):
		"""start a new game when the player clicks play"""
		button_clicked = self.play_button.rect.collidepoint(mouse_pos)
		if button_clicked and not self.stats.game_active: 
			self.settings.initialize_dynamic_settings()
			self.stats.reset_stats()
			self.stats.game_active = True
			self.sb.prep_score()
			self.sb.prep_level()
			self.sb.prep_ships()

			#get rid of any remaining aliens and bullets
			self.aliens.empty()
			self.bullets.empty()

			#create a new fleet and center the ship
			self._create_fleet()
			self.ship.center_ship()

			#hide the mouse
			pygame.mouse.set_visible(False)


	def _fire_bullet(self):
		"""create a new bullet and add it to the bullets group"""
		if len(self.bullets) < self.settings.bullets_allowed:
			new_bullet = Bullet(self)
			self.bullets.add(new_bullet) 


	def _create_fleet(self):
		"""create the fleet of aliens"""
		#make an alien and find the number of aliens in a row
		alien = Alien(self)
		alien_width, alien_height = alien.rect.size
		available_space_x = self.settings.screen_width - (2 * alien_width)
		number_aliens_x = available_space_x // (2 * alien_width) 

		#determine the number of rows of aliens that fit on the screen
		ship_height = self.ship.rect.height
		available_space_y = (self.settings.screen_height -
								 (3 * alien_height) - ship_height)
		number_rows = available_space_y // (3 * alien_height)

		#create the first row of aliens
		for row_number in range(number_rows):
			for alien_number in range(number_aliens_x):
				self._create_alien(alien_number, row_number)


	def _create_alien(self, alien_number, row_number):
		#create an alien and place it in the row
		alien = Alien(self)
		alien_width, alien_height = alien.rect.size
		alien.x = alien_width + 2 * alien_width * alien_number
		alien.rect.x = alien.x
		alien.rect.y = 3 * alien.rect.height + 2 * alien.rect.height * row_number
		self.aliens.add(alien)


	def _check_fleet_edges(self):
		"""respond appropriately if any aliens have reached an edge"""
		for alien in self.aliens.sprites():
			if alien.check_edges():
				self._change_fleet_direction()
				break


	def _ship_hit(self):
		"""respond to the ship being hit by an alien"""
		if self.stats.ships_left > 0:
			#decrement ships_left
			self.stats.ships_left -= 1
			self.sb.prep_ships()

			#empty the aliens/bullets in the group
			self.aliens.empty()
			self.bullets.empty() 

			#create a new fleet and center the ship
			self._create_fleet()
			self.ship.center_ship()

			#pause
			sleep(0.5)
		else:
			self.stats.game_active = False 
			#ends the game if the player runs out of ships
			pygame.mouse.set_visible(True)


	def _change_fleet_direction(self):
		"""drop the entire fleet and change the fleet's direction"""
		for alien in self.aliens.sprites():
			alien.rect.y += self.settings.fleet_drop_speed
		self.settings.fleet_direction *= -1


	def _update_screen(self): 
		"""update images on screen, flip to new screen"""
		self.screen.fill(self.settings.bg_color)
		self.ship.blitme() 
		for bullet in self.bullets.sprites():
			bullet.draw_bullet() 
		self.aliens.draw(self.screen) 

		#show the score information
		self.sb.show_score()
		
		#draw button screen if game is inactive
		if not self.stats.game_active:
			self.play_button.draw_button()

		#move to next screen
		pygame.display.flip()



if __name__ == '__main__': 
	ai = AlienInvasion()
	ai.run_game()