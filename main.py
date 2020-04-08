import pygame                                       # Подключение библиотеки PyGame
from os import path
import random

WIDTH = 480                                         # Ширина экрана
HEIGHT = 600                                        # Высота экрана
FPS = 60                                            # Частота кадров в секунду

BLACK = (0, 0, 0)                                   # Черный цвет
WHITE = (255, 255, 255)                             # Белый цвет
RED = (255, 0, 0)                                   # Красный цвет
GREEN = (0, 255, 0)                                 # Зеленый цвет
BLUE = (0, 0, 255)                                  # Синий цвет

pygame.init()                                       # Создаем игру
pygame.mixer.init()                                 # Подключаем звуки
screen = pygame.display.set_mode((WIDTH, HEIGHT))   # Настраиваем ширину и высоту экрана
pygame.display.set_caption("Моя игра")              # Определяем название игры
clock = pygame.time.Clock()                         # Переменная, которая поможет убедиться, что игра работает с нужным FPS

game_folder = path.dirname(__file__)             # Настройка папки ассетов
assets_folder = path.join(game_folder, 'assets')
img_folder = path.join(assets_folder, 'img')
snd_folder = path.join(assets_folder, 'snd')

pygame.mixer.music.load(path.join(snd_folder, 'back.ogg'))
pygame.mixer.music.set_volume(0.01)

shoot_sound = pygame.mixer.Sound(path.join(snd_folder, 'pew.wav'))

expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_folder, snd)))

meteor_images = []
meteor_list =['meteorBrown_big1.png','meteorBrown_med1.png',
              'meteorBrown_med1.png','meteorBrown_med3.png',
              'meteorBrown_small1.png','meteorBrown_small2.png',
              'meteorBrown_tiny1.png']

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = "regularExplosion0{}.png".format(i)
    img = pygame.image.load(path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['lg'].append(img_lg)
    explosion_anim['sm'].append(img_sm)
    # взрывы игрока
    filename = "sonicExplosion0{}.png".format(i)
    img = pygame.image.load(path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

score = 0

for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_folder, img)).convert())

background = pygame.image.load(path.join(img_folder, 'background.png'))
background_rect = background.get_rect()

player_img = pygame.image.load(path.join(img_folder, 'ship.png'))
meteor_img = pygame.image.load(path.join(img_folder, 'meteor.png'))
bullet_img = pygame.image.load(path.join(img_folder, 'laser.png'))

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size): # size это "lg" или "sm", или "player"
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        global score
        self.rect.y += self.speedy
        if self.rect.bottom < 0:    # проверка выхода за верхнюю границу экрана
            score -= 10
            if score < 0:
                score = 0
            self.kill()             # удаление спрайта

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)
    
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.image_orig, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = old_center

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.rect = self.image.get_rect()
        self.radius = 22
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()

        self.rect.x += self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullet_sprites.add(bullet)
            shoot_sound.play()

def draw_shield_bar(surf, x, y, pt):
    if pt < 0:
        pt = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pt / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def newMob():
    m = Mob()
    all_sprites.add(m)
    mob_sprites.add(m)


all_sprites = pygame.sprite.Group()
mob_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(8):
    newMob()

pygame.mixer.music.play(loops=-1)
running = True
while running:                                      # Цикл игры
    clock.tick(FPS)                                 # Держим цикл на правильной скорости

    # ОБРАБОТКА ВВОДА

    for event in pygame.event.get():                # Проходим по списку событий
        if event.type == pygame.QUIT:               # Если тип события == ВЫХОД
            running = False                         # Останавливаем выполнение цикла игры

    # ОБРАБОТКА ИЗМЕНEНИЙ

    all_sprites.update()
    hits = pygame.sprite.groupcollide(mob_sprites, bullet_sprites, True, True)
    for hit in hits:
        score += 50 - hit.radius
        newMob()
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)

    hits = pygame.sprite.spritecollide(player, mob_sprites, True, pygame.sprite.collide_circle)
    for hit in hits:
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newMob()
        player.shield -= hit.radius * 2
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.kill()

    if not player.alive() and not death_explosion.alive():
        running = False

    #ПРОРИСОВКА

    screen.fill(BLACK)                              # Заполнить экран черным цветом
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    pygame.display.flip()                           # Отобразить изменения

pygame.quit()                                       # Закрываем окно игры