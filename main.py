import os
import random
import pygame
from pygame import *

pygame.init()

display = (width_screen, height_screen) = (650, 200)
fps = 60
gravitation = 0.6

black_color = (0, 0, 0)
white_color = (255, 255, 255)
bg_color = (235, 235, 235)

highest_scores = 0

screen_display = pygame.display.set_mode(display)
time_clock = pygame.time.Clock()
pygame.display.set_caption("Senku-zavr")

jump_sound = pygame.mixer.Sound('senku_laboratory/jump.wav')
die_sound = pygame.mixer.Sound('senku_laboratory/die.wav')
checkPoint_sound = pygame.mixer.Sound('senku_laboratory/checkPoint.wav')


def load_image(name, x=-1, y=-1, color_key=None):
    fullname = os.path.join('senku_laboratory', name)
    img = pygame.image.load(fullname)
    img = img.convert()
    if color_key is not None:
        if color_key == -1:
            color_key = img.get_at((0, 0))
        img.set_colorkey(color_key, RLEACCEL)

    if x != -1 or y != -1:
        img = pygame.transform.scale(img, (x, y))

    return img, img.get_rect()


def load_sprite_sheet(s_name, name_x, name_y, sca_x=-1, sca_y=-1, c_key=None):
    fullname = os.path.join('senku_laboratory', s_name)
    sh = pygame.image.load(fullname)
    sh = sh.convert()

    sh_rect = sh.get_rect()

    sprites = []

    sx = sh_rect.width / name_x
    sy = sh_rect.height / name_y

    for i in range(0, name_y):
        for j in range(0, name_x):
            rect = pygame.Rect((j*sx, i*sy, sx, sy))
            img = pygame.Surface(rect.size)
            img = img.convert()
            img.blit(sh, (0, 0), rect)

            if c_key is not None:
                if c_key == -1:
                    c_key = img.get_at((0, 0))
                img.set_colorkey(c_key, RLEACCEL)

            if sca_x != -1 or sca_y != -1:
                img = pygame.transform.scale(img, (sca_x, sca_y))

            sprites.append(img)

    sprite_rect = sprites[0].get_rect()

    return sprites, sprite_rect


def gameover_display_message(image1, gmo_image):
    rbtn_rect = image1.get_rect()
    rbtn_rect.centerx = width_screen / 2
    rbtn_rect.top = height_screen * 0.52

    gmo_rect = gmo_image.get_rect()
    gmo_rect.centerx = width_screen / 2
    gmo_rect.centery = height_screen * 0.35

    screen_display.blit(image1, rbtn_rect)
    screen_display.blit(gmo_image, gmo_rect)


def extra_digits(num):
    if num > -1:
        d = []
        while num / 10 != 0:
            d.append(num % 10)
            num = int(num / 10)

        d.append(num % 10)
        for i in range(len(d), 5):
            d.append(0)
        d.reverse()
        return d


class Senkuzavr:
    def __init__(self, sx=-1, sy=-1):
        self.image1, self.rect = load_sprite_sheet('dino.png', 5, 1, sx, sy, -1)
        self.image2, self.rect1 = load_sprite_sheet('dino_ducking.png', 2, 1, 59, sy, -1)
        self.rect.bottom = int(0.98 * height_screen)
        self.rect.left = width_screen / 15
        self.image = self.image1[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.jumping = False
        self.dead = False
        self.ducking = False
        self.blinking = False
        self.movement = [0, 0]
        self.jump_speed = 11.5

        self.positionstand_width = self.rect.width
        self.positionduck_width = self.rect1.width

    def draw(self):
        screen_display.blit(self.image, self.rect)

    def checkpoint(self):
        if self.rect.bottom > int(0.98 * height_screen):
            self.rect.bottom = int(0.98 * height_screen)
            self.jumping = False

    def update(self):
        if self.jumping:
            self.movement[1] = self.movement[1] + gravitation

        if self.jumping:
            self.index = 0
        elif self.blinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1) % 2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1) % 2

        elif self.ducking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2 + 2

        if self.dead:
            self.index = 4

        if not self.ducking:
            self.image = self.image1[self.index]
            self.rect.width = self.positionstand_width
        else:
            self.image = self.image2[self.index % 2]
            self.rect.width = self.positionduck_width

        self.rect = self.rect.move(self.movement)
        self.checkpoint()

        if not self.dead and self.counter % 7 == 6 and self.blinking is False:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() is not None:
                    checkPoint_sound.play()

        self.counter = (self.counter + 1)


class Birds(pygame.sprite.Sprite):
    def __init__(self, speed=5, sx=-1, sy=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet('birds.png', 2, 1, sx, sy, -1)
        self.birds_height = [height_screen * 0.82, height_screen * 0.75, height_screen * 0.60]
        self.rect.centery = self.birds_height[random.randrange(0, 3)]
        self.rect.left = width_screen + self.rect.width
        self.image = self.images[0]
        self.movement = [-1 * speed, 0]
        self.index = 0
        self.counter = 0

    def draw(self):
        screen_display.blit(self.image, self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index+1) % 2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            self.kill()


class Cactus(pygame.sprite.Sprite):
    def __init__(self, speed=5, sx=-1, sy=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet('cactus-small.png', 3, 1, sx, sy, -1)
        self.rect.bottom = int(0.98 * height_screen)
        self.rect.left = width_screen + self.rect.width
        self.image = self.images[random.randrange(0, 3)]
        self.movement = [-1 * speed, 0]

    def draw(self):
        screen_display.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)

        if self.rect.right < 0:
            self.kill()


class Ground:
    def __init__(self, speed=-5):
        self.image, self.rect = load_image('ground.png', -1, -1, -1)
        self.image1, self.rect1 = load_image('ground.png', -1, -1, -1)
        self.rect.bottom = height_screen
        self.rect1.bottom = height_screen
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        screen_display.blit(self.image, self.rect)
        screen_display.blit(self.image1, self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right


class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image('cloud.png', int(90 * 30 / 42), 30, -1)
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1*self.speed, 0]

    def draw(self):
        screen_display.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()


class Scoreboard:
    def __init__(self, x=-1, y=-1):
        self.score = 0
        self.scre_img, self.screrect = load_sprite_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
        self.image = pygame.Surface((55, int(11 * 6 / 5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width_screen * 0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height_screen * 0.1
        else:
            self.rect.top = y

    def draw(self):
        screen_display.blit(self.image, self.rect)

    def update(self, score):
        score_digits = extra_digits(score)
        self.image.fill(bg_color)
        for s in score_digits:
            self.image.blit(self.scre_img[s], self.screrect)
            self.screrect.left += self.screrect.width
        self.screrect.left = 0


def introduction_screen():
    ado_dino = Senkuzavr(44, 47)
    ado_dino.blinking = True
    starting_game = False

    t_ground, t_ground_rect = load_sprite_sheet('ground.png', 15, 1, -1, -1, -1)
    t_ground_rect.left = width_screen / 20
    t_ground_rect.bottom = height_screen

    logo, l_rect = load_image('logo.png', 300, 140, -1)
    l_rect.centerx = width_screen * 0.6
    l_rect.centery = height_screen * 0.6
    while not starting_game:
        if pygame.display.get_surface() is None:
            print("Ничего не работает. ггвп.")
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        ado_dino.jumping = True
                        ado_dino.blinking = False
                        ado_dino.movement[1] = -1 * ado_dino.jump_speed
        ado_dino.update()
        if pygame.display.get_surface() is not None:
            screen_display.fill(bg_color)
            screen_display.blit(t_ground[0], t_ground_rect)
            if ado_dino.blinking:
                screen_display.blit(logo, l_rect)
            ado_dino.draw()

            pygame.display.update()

        time_clock.tick(fps)
        if ado_dino.jumping is False and ado_dino.blinking is False:
            starting_game = True


def gameplay():
    global highest_scores
    gp = 4
    s_menu = False
    g_over = False
    g_exit = False
    gamer_dino = Senkuzavr(44, 47)
    new_grnd = Ground(-1 * gp)
    score_boards = Scoreboard()
    high_score = Scoreboard(width_screen * 0.78)
    counter = 0

    cactusan = pygame.sprite.Group()
    small_bird = pygame.sprite.Group()
    sky_clouds = pygame.sprite.Group()
    last_end_obs = pygame.sprite.Group()

    Cactus.containers = cactusan
    Birds.containers = small_bird
    Cloud.containers = sky_clouds

    rbtn_image, rbtn_rect = load_image('replay_button.png', 35, 31, -1)
    gmo_image, gmo_rect = load_image('game_over.png', 190, 11, -1)

    t_images, t_rect = load_sprite_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
    ado_image = pygame.Surface((22, int(11 * 6 / 5)))
    ado_rect = ado_image.get_rect()
    ado_image.fill(bg_color)
    ado_image.blit(t_images[10], t_rect)
    t_rect.left += t_rect.width
    ado_image.blit(t_images[11], t_rect)
    ado_rect.top = height_screen * 0.1
    ado_rect.left = width_screen * 0.73

    while not g_exit:
        while s_menu:
            pass
        while not g_over:
            if pygame.display.get_surface() is None:
                print("Невозможно загрузить интерфейс.")
                g_exit = True
                g_over = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        g_exit = True
                        g_over = True

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if gamer_dino.rect.bottom == int(0.98 * height_screen):
                                gamer_dino.jumping = True
                                if pygame.mixer.get_init() is not None:
                                    jump_sound.play()
                                gamer_dino.movement[1] = -1*gamer_dino.jump_speed

                        if event.key == pygame.K_DOWN:
                            if not (gamer_dino.jumping and gamer_dino.dead):
                                gamer_dino.ducking = True

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_DOWN:
                            gamer_dino.ducking = False
            for c in cactusan:
                c.movement[0] = -1 * gp
                if pygame.sprite.collide_mask(gamer_dino, c):
                    gamer_dino.dead = True
                    if pygame.mixer.get_init() is not None:
                        die_sound.play()

            for p in small_bird:
                p.movement[0] = -1 * gp
                if pygame.sprite.collide_mask(gamer_dino, p):
                    gamer_dino.dead = True
                    if pygame.mixer.get_init() is not None:
                        die_sound.play()

            if len(cactusan) < 2:
                if len(cactusan) == 0:
                    last_end_obs.empty()
                    last_end_obs.add(Cactus(gp, 40, 40))
                else:
                    for L in last_end_obs:
                        if L.rect.right < width_screen*0.7 and random.randrange(0, 50) == 10:
                            last_end_obs.empty()
                            last_end_obs.add(Cactus(gp, 40, 40))

            if len(small_bird) == 0 and random.randrange(0, 200) == 10 and counter > 500:
                for L in last_end_obs:
                    if L.rect.right < width_screen*0.8:
                        last_end_obs.empty()
                        last_end_obs.add(Birds(gp, 46, 40))

            if len(sky_clouds) < 5 and random.randrange(0, 300) == 10:
                Cloud(width_screen, random.randrange(height_screen / 5, height_screen / 2))

            new_grnd.update()
            gamer_dino.update()
            cactusan.update()
            small_bird.update()
            sky_clouds.update()
            score_boards.update(gamer_dino.score)
            high_score.update(highest_scores)

            if pygame.display.get_surface() is not None:
                screen_display.fill(bg_color)
                new_grnd.draw()
                sky_clouds.draw(screen_display)
                score_boards.draw()
                if highest_scores != 0:
                    high_score.draw()
                    screen_display.blit(ado_image, ado_rect)
                cactusan.draw(screen_display)
                small_bird.draw(screen_display)
                gamer_dino.draw()

                pygame.display.update()
            time_clock.tick(fps)

            if gamer_dino.dead:
                g_over = True
                if gamer_dino.score > highest_scores:
                    highest_scores = gamer_dino.score

            if counter % 700 == 699:
                new_grnd.speed -= 1
                gp += 1

            counter = (counter + 1)

        if g_exit:
            break

        while g_over:
            if pygame.display.get_surface() is None:
                print("Все еще не робит")
                g_exit = True
                g_over = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        g_exit = True
                        g_over = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            g_exit = True
                            g_over = False

                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            g_over = False
                            gameplay()
            high_score.update(highest_scores)
            if pygame.display.get_surface() is not None:
                gameover_display_message(rbtn_image, gmo_image)
                if highest_scores != 0:
                    high_score.draw()
                    screen_display.blit(ado_image, ado_rect)
                pygame.display.update()
            time_clock.tick(fps)

    pygame.quit()
    quit()


def main():
    is_game_quit = introduction_screen()
    if not is_game_quit:
        gameplay()


main()
