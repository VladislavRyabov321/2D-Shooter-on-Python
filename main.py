import pygame
from pygame import mixer
import os
import random
import csv
import button
import time
from database import (
    save_result,
    get_all_games,
    get_avg_kills,
    get_avg_time,
    get_fastest_run,
    get_longest_run
)

mixer.init()
pygame.init()

level = 1
last_completed_level = 0
game_over = False
result_saved = False
start_time = time.time()
elapsed_time = 0  # итоговое время после смерти
player_name = "Player1"  # или сделать окно ввода
enemies_killed = 0       # увеличивать при убийстве врага
viewing_all_games = False

avg_kills_text = ""
avg_time_text = ""
fastest_run_text = ""
longest_run_text = ""

table_scroll = 0  # глобальная переменная для вертикального сдвига
scroll_speed = 30  # на сколько пикселей прокручивать за один шаг
scroll_offset = 0


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

visible_table_height = SCREEN_HEIGHT - 100

DARK_GREY = (50, 50, 50)  # тёмно-серый цвет

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

clock = pygame.time.Clock()
FPS = 60

GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
font_minecraft = pygame.font.Font('fonts/minecraft.ttf', 18)


moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

restart_panel_y = -300  # Начальная позиция окна (вне экрана)
restart_panel_target_y = SCREEN_HEIGHT // 2 - 100  # Центр экрана
restart_panel_speed = 30
show_restart_panel = False

viewing_all_games = False
TABLE_MODAL_TARGET_Y = 100
TABLE_MODAL_HEIGHT = 500
TABLE_ANIM_DURATION = 30
table_animation_progress = 0


pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.05)


#button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
all_games_img =  pygame.image.load('img/all_games_btn.png').convert_alpha()
back_img =  pygame.image.load('img/back_btn.png').convert_alpha()
avg_kills_img =  pygame.image.load('img/avg_kills_btn.png').convert_alpha()
fastest_run_img =  pygame.image.load('img/fastest_run_btn.png').convert_alpha()
longest_run_img =  pygame.image.load('img/longest_run_btn.png').convert_alpha()
avg_time_img =  pygame.image.load('img/avg_time_btn.png').convert_alpha()
#background
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()

img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/Tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)
#bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
#grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
#pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Grenade'	: grenade_box_img
}


BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def draw_bg():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(5):
		screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
		screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
		screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
		screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	data = []
	for row in range(ROWS):
		r = [-1] * COLS
		data.append(r)

	return data




class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#ai specific variables
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0

		animation_types = ['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_types:
			temp_list = []
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()


	def update(self):
		self.update_animation()
		self.check_alive()
		#update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		screen_scroll = 0
		dx = 0
		dy = 0

		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -12
			self.jump = False
			self.in_air = True

		#gravity
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#collision
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom


		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0


		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0

		self.rect.x += dx
		self.rect.y += dy

		if self.char_type == 'player':
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll, level_complete



	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			#reduce ammo
			self.ammo -= 1
			shot_fx.play()


	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)#0: idle
				self.idling = True
				self.idling_counter = 50
			if self.vision.colliderect(player.rect):
				self.update_action(0)#0: idle
				#shoot
				self.shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)#1: run
					self.move_counter += 1
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

		#scroll
		self.rect.x += screen_scroll


	def update_animation(self):
		ANIMATION_COOLDOWN = 100
		self.image = self.animation_list[self.action][self.frame_index]
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0



	def update_action(self, new_action):
		if new_action != self.action:
			self.action = new_action
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()



	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		player = None
		health_bar = None

		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)

					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15:  # create player
						player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16:  # create enemies
						enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
						enemy_group.add(enemy)
					elif tile == 17:  # create ammo box
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 18:  # create grenade box
						item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19:  # create health box
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20:  # create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)

		# Если игрок не найден, создаём в дефолтной позиции (например, 0, 0)
		if player is None:
			player = Soldier('player', 0, 0, 1.65, 5, 20, 5)
			health_bar = HealthBar(10, 10, player.health, player.health)

		return player, health_bar


	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


	def update(self):
		#scroll
		self.rect.x += screen_scroll
		#check if the player has picked up the box
		if pygame.sprite.collide_rect(self, player):
			#check what kind of box it was
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
			elif self.item_type == 'Grenade':
				player.grenades += 3
			#delete the item box
			self.kill()


class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		self.health = health
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		global enemies_killed
		self.rect.x += (self.direction * self.speed) + screen_scroll
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					if enemy.health <= 0:
						enemies_killed += 1
					self.kill()



class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	


		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			grenade_fx.play()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


	def update(self):
		#scroll
		self.rect.x += screen_scroll

		EXPLOSION_SPEED = 4
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]


class ScreenFade():
	def __init__(self, direction, colour, speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0


	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
		if self.direction == 2:
			pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= SCREEN_WIDTH:
			fade_complete = True

		return fade_complete


intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)


start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

all_games_button = button.Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 180, all_games_img, 0.6)

avg_kills_button = button.Button(SCREEN_WIDTH // 2 + 75, 50, avg_kills_img, 0.6)
avg_time_button = button.Button(SCREEN_WIDTH // 2 + 75, 160, avg_time_img, 0.6)
fastest_run_button = button.Button(SCREEN_WIDTH // 2 + 75, 270, fastest_run_img, 0.6)
longest_run_button = button.Button(SCREEN_WIDTH // 2 + 75, 380, longest_run_img, 0.6)
back_button = button.Button(SCREEN_WIDTH // 2 + 75, 490, back_img, 0.6)

enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:

	clock.tick(FPS)
	show_text = ""

	if start_game == False:
		screen.fill(BG)
		if start_button.draw(screen):
			start_game = True
			start_intro = True
		if exit_button.draw(screen):
			run = False
	else:
		draw_bg()
		world.draw()
		health_bar.draw(player.health)
		draw_text('AMMO: ', font_minecraft, WHITE, 10, 35)
		for x in range(player.ammo):
			screen.blit(bullet_img, (90 + (x * 10), 40))

		draw_text('GRENADES: ', font_minecraft, WHITE, 10, 60)
		for x in range(player.grenades):
			screen.blit(grenade_img, (135 + (x * 15), 60))


		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()

		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)

		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0


		if player.alive:
			game_over = False
			elapsed_time = int(time.time() - start_time)
			if shoot:
				player.shoot()
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
								  player.rect.top, player.direction)
				grenade_group.add(grenade)
				player.grenades -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2)  # 2: jump
			elif moving_left or moving_right:
				player.update_action(1)  # 1: run
			else:
				player.update_action(0)  # 0: idle
			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			if level_complete:
				start_intro = True
				last_completed_level = level  # обновляем последний пройденный уровень
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				if level <= MAX_LEVELS:
					# load in level data and create world
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)
		else:
			if not result_saved:
				save_result(player_name, level, enemies_killed, start_time)
				result_saved = True

			game_over = True
			screen_scroll = 0

		if viewing_all_games:
			screen.fill(DARK_GREY)

			font_path = 'fonts/minecraft.ttf'
			font_size = 20  # Было 24, уменьшили
			font = pygame.font.Font(font_path, font_size)
			table_data = get_all_games()

			y_start = 50  # стартовая позиция вывода таблицы

			# Увеличиваем прогресс анимации
			if table_animation_progress < TABLE_ANIM_DURATION:
				table_animation_progress += 1

			# Смещение для плавного появления
			animation_offset = int((TABLE_ANIM_DURATION - table_animation_progress) / TABLE_ANIM_DURATION * 100)

			for i, row in enumerate(table_data):
				y = y_start + i * 30 - scroll_offset + animation_offset
				if 50 <= y <= SCREEN_HEIGHT - 100:  # отрисовываем только видимую часть
					row_text = f"#{row[0]} | Time: {row[4]}s | Kills: {row[3]} | Levels: {row[2]}"
					text_surf = font.render(row_text, True, WHITE)
					screen.blit(text_surf, (50, y))

			# Отрисовка кнопок и обработка нажатий
			if back_button.draw(screen):
				viewing_all_games = False
				# Очистка текстов при выходе
				avg_kills_text = ""
				avg_time_text = ""
				fastest_run_text = ""
				longest_run_text = ""

			if avg_kills_button.draw(screen):
				avg_kills = get_avg_kills()
				avg_kills_text = f"Average kills: {avg_kills}"

			if avg_time_button.draw(screen):
				avg_time = get_avg_time()
				avg_time_text = f"Average time: {avg_time}s"

			if fastest_run_button.draw(screen):
				fastest = get_fastest_run()
				fastest_run_text = f"Fastest run: {fastest}s"

			if longest_run_button.draw(screen):
				longest = get_longest_run()
				longest_run_text = f"Longest run: {longest}s"

			result_font = pygame.font.Font('fonts/minecraft.ttf', 22)
			text_color = (255, 255, 255)

			if avg_kills_text:
				kills_text_surf = result_font.render(avg_kills_text, True, text_color)
				screen.blit(kills_text_surf, (avg_kills_button.rect.x, avg_kills_button.rect.bottom + 5))

			if avg_time_text:
				time_text_surf = result_font.render(avg_time_text, True, text_color)
				screen.blit(time_text_surf, (avg_time_button.rect.x, avg_time_button.rect.bottom + 5))

			if fastest_run_text:
				fast_text_surf = result_font.render(fastest_run_text, True, text_color)
				screen.blit(fast_text_surf, (fastest_run_button.rect.x, fastest_run_button.rect.bottom + 5))

			if longest_run_text:
				long_text_surf = result_font.render(longest_run_text, True, text_color)
				screen.blit(long_text_surf, (longest_run_button.rect.x, longest_run_button.rect.bottom + 5))

			# Показать результат запроса
			if show_text:
				result_font = pygame.font.Font('fonts/minecraft.ttf', 18)
				result_surface = result_font.render(show_text, True, (255, 255, 255))
				result_x = SCREEN_WIDTH // 2 + 75  # по центру правой колонки
				result_y = back_button.rect.bottom + 10  # сразу под кнопкой "Back"
				screen.blit(result_surface, (result_x, result_y))

		elif game_over:
			# Запускаем анимацию появления панели, если ещё не началась
			if not show_restart_panel:
				restart_panel_y = -300
				show_restart_panel = True

			# Плавное движение панели к целевой позиции
			if restart_panel_y < restart_panel_target_y:
				restart_panel_y += restart_panel_speed
				if restart_panel_y > restart_panel_target_y:
					restart_panel_y = restart_panel_target_y

			# Затемняем фон
			overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
			overlay.set_alpha(180)  # Прозрачность
			overlay.fill((0, 0, 0))  # Черный полупрозрачный фон
			screen.blit(overlay, (0, 0))

			# Отрисовка окна рестарта
			panel_width, panel_height = 400, 300
			panel_x = (SCREEN_WIDTH - panel_width) // 2
			panel_rect = pygame.Rect(panel_x, restart_panel_y, panel_width, panel_height)
			pygame.draw.rect(screen, (50, 50, 50), panel_rect, border_radius=12)
			pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3, border_radius=12)

			# Шрифт
			font = pygame.font.Font('fonts/minecraft.ttf', 24)
			white = (255, 255, 255)

			# Данные
			play_time = elapsed_time
			level_display = last_completed_level if game_over else level
			enemies_text = font.render(f"Врагов убито: {enemies_killed}", True, white)
			level_text = font.render(f"Пройдено уровней: {level_display}", True, white)
			time_text = font.render(f"Время игры: {play_time} сек", True, white)

			# Позиции текста
			screen.blit(enemies_text, (panel_x + 20, restart_panel_y + 20))
			screen.blit(level_text, (panel_x + 20, restart_panel_y + 60))
			screen.blit(time_text, (panel_x + 20, restart_panel_y + 100))

			# Обновляем позицию кнопки рестарт
			restart_button.rect.centerx = panel_rect.centerx
			restart_button.rect.top = restart_panel_y + 150
			if restart_button.draw(screen):

				# Сброс игры
				game_over = False
				result_saved = False
				level = 1
				enemies_killed = 0
				start_time = time.time()
				elapsed_time = 0
				start_intro = True
				bg_scroll = 0
				show_restart_panel = False
				world_data = reset_level()
				with open(f'level{level}_data.csv', newline='') as csvfile:
					reader = csv.reader(csvfile, delimiter=',')
					for x, row in enumerate(reader):
						for y, tile in enumerate(row):
							world_data[x][y] = int(tile)
				world = World()
				player, health_bar = world.process_data(world_data)

			# Кнопка "Все игры"
			all_games_button.rect.centerx = panel_rect.centerx
			all_games_button.rect.top = restart_panel_y + 220
			if all_games_button.draw(screen):
				viewing_all_games = True
				table_animation_progress = 0  # сбрасываем прогресс анимации

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 4:  # колесо мыши вверх
				scroll_offset = max(scroll_offset - scroll_speed, 0)  # не уходить выше верхнего края
			elif event.button == 5:  # колесо мыши вниз
				# допустим, max_scroll — максимальный сдвиг, чтобы не уйти ниже таблицы
				max_scroll = max(0, len(table_data) * 30 - visible_table_height)
				scroll_offset = min(scroll_offset + scroll_speed, max_scroll)

		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_q:
				grenade = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
				jump_fx.play()
			if event.key == pygame.K_ESCAPE:
				run = False

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False


	pygame.display.update()

pygame.quit()