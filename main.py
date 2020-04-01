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

meteor_images = []
meteor_list =['meteorBrown_big1.png','meteorBrown_med1.png',
              'meteorBrown_med1.png','meteorBrown_med3.png',
              'meteorBrown_small1.png','meteorBrown_small2.png',
              'meteorBrown_tiny1.png']

score = 0

for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_folder, img)).convert())

background = pygame.image.load(path.join(img_folder, 'background.png'))
background_rect = background.get_rect()

player_img = pygame.image.load(path.join(img_folder, 'ship.png'))
meteor_img = pygame.image.load(path.join(img_folder, 'meteor.png'))
bullet_img = pygame.image.load(path.join(img_folder, 'laser.png'))

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

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 8
        self.rect.x += self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullet_sprites.add(bullet)

font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

all_sprites = pygame.sprite.Group()
mob_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(8):
    m = Mob()
    all_sprites.add(m)
    mob_sprites.add(m)



running = True
while running:                                      # Цикл игры
    clock.tick(FPS)                                 # Держим цикл на правильной скорости

    # ОБРАБОТКА ВВОДА

    for event in pygame.event.get():                # Проходим по списку событий
        if event.type == pygame.QUIT:               # Если тип события == ВЫХОД
            running = False                         # Останавливаем выполнение цикла игры
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # ОБРАБОТКА ИЗМЕНеНИЙ

    all_sprites.update()
    hits = pygame.sprite.groupcollide(mob_sprites, bullet_sprites, True, True)
    for hit in hits:
        score += 50 - hit.radius
        m = Mob()
        all_sprites.add(m)
        mob_sprites.add(m)

    hits = pygame.sprite.spritecollide(player, mob_sprites, False, pygame.sprite.collide_circle)
    if hits:
        running = False

    #ПРОРИСОВКА

    screen.fill(BLACK)                              # Заполнить экран черным цветом
    screen.blit(background, background_rect)
    all_sprites.draw(screen)    
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    pygame.display.flip()                           # Отобразить изменения

pygame.quit()                                       # Закрываем окно игры