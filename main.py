import pygame, random, sys
pygame.init()

#set window
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("The Mars Journey")

#game variables
BLUE = (75,130,176)
SHIP_WIDTH, SHIP_HEIGHT = 150, 150
bg_y_position = 0
score = 0

#import images
BG = pygame.image.load("python/space_invaders/game_data/bg.png")
STARSHIP_IMAGE = pygame.image.load("python/space_invaders/game_data/starship_base.png")
BLUE_ORIGIN_IMAGE = pygame.image.load("python/space_invaders/game_data/blueorigin_base.png")
BLUE_LASER = pygame.image.load("python/space_invaders/game_data/blue_laser.png")
RED_LASER = pygame.image.load("python/space_invaders/game_data/red_laser.png")

#scale images
STARSHIP_IMAGE = pygame.transform.scale2x(STARSHIP_IMAGE)
BLUE_LASER = pygame.transform.scale2x(BLUE_LASER)
BLUE_ORIGIN_IMAGE = pygame.transform.scale2x(BLUE_ORIGIN_IMAGE)
BLUE_ORIGIN_IMAGE = pygame.transform.rotate(BLUE_ORIGIN_IMAGE,180)
RED_LASER = pygame.transform.scale2x(RED_LASER)
RED_LASER = pygame.transform.rotate(RED_LASER,180)

#sound
BLUE_LASER_SOUND = pygame.mixer.Sound("python/space_invaders/game_data/blue_laser_audio.wav")
BLUE_LASER_SOUND.set_volume(0.5)

RED_LASER_SOUND = pygame.mixer.Sound("python/space_invaders/game_data/red_laser_audio.wav")
RED_LASER_SOUND.set_volume(0.5)

BLUE_ORIGIN_DESTROY_SOUND = pygame.mixer.Sound("python/space_invaders/game_data/blue_origin_destroy_audio.wav")
BLUE_ORIGIN_DESTROY_SOUND.set_volume(0.5)

#create class for the ships 
class Ship:
    COOLDOWN = 120   
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down = 0

    #draw ship method
    def draw(self, window):
        window.blit(self.ship_img,(self.x, self.y))
        for laser in self.lasers:
            laser.draw(WIN)
    #get widht and height functions
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    # function move laser that was shooted
    def move_laser(self, vel, obj):
        for laser in self.lasers:
            laser.move(vel)
            if laser.is_off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                sys.exit()
                self.lasers.remove(laser)
    # laser cooldawn 
    def cool_down_f(self):
        if self.cool_down >= self.COOLDOWN:
            self.cool_down = 0
        elif self.cool_down > 0:
            self.cool_down += 1

    # shoot laser method
    def shoot(self):
        if self.cool_down == 0:
            laser = Laser(self.x - int(self.laser_img.get_width()/2) + int(self.get_width()/2), self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down = 1

# class for the starship player
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = STARSHIP_IMAGE
        self.laser_img = BLUE_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    #move laser method for the player and run collision event
    def move_laser(self, vel, objs):
        for laser in self.lasers:
            laser.move(vel)
            if laser.is_off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)    
                        BLUE_ORIGIN_DESTROY_SOUND.play()
                        global score
                        score += 1  

    #collision with the enemy ship
    def enemy_collision(self, objs):
        for obj in objs:
            if collide(self, obj):
                sys.exit()

    #shoot method for the player
    def shoot(self):
        if self.cool_down == 0:
            laser = Laser(self.x - int(self.laser_img.get_width()/2) + int(self.get_width()/2), self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down = 1
            BLUE_LASER_SOUND.play()

#class for the enemy ships
class Enemy(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = BLUE_ORIGIN_IMAGE
        self.laser_img = RED_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)

    #move enemies
    def move_ship(self, vel):
        self.y += vel

    #enmies shoot method
    def shoot(self):
        if self.cool_down == 0:
            laser = Laser(self.x - int(self.laser_img.get_width()/2) + int(self.get_width()/2), self.y, self.laser_img)
            
            self.lasers.append(laser)
            self.cool_down = 1
            RED_LASER_SOUND.play()

    

#laser class
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    #draw the laser
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    #move the laser
    def move(self, vel):
        self.y += vel
    #check if it is off screen
    def is_off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    #check collition
    def collision(self, obj):
        return collide(self, obj)

# check collide and offset function
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
      


#main function
def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()

    laser_velocity = 4
    player_velocity = 5
    enemy_velocity = 1

    enemies = []
    wave_lenght = 10

    #draw text
    main_font = pygame.font.SysFont("arial", 40)
    

    #set player position
    player_ship = Player(int(WIDTH/2 - STARSHIP_IMAGE.get_width()/2) ,HEIGHT-150) 
    
    #re-draw windown function
    def draw_window():
        pygame.display.update()
        #animate bg
        global bg_y_position
        WIN.blit(BG,(0,bg_y_position))
        WIN.blit(BG,(0,bg_y_position-HEIGHT))
        
        #update score on screen
        score_label = main_font.render(f"Score: {score}", 1, (255,255,255))
        WIN.blit(score_label, (20,20))

        if bg_y_position >= HEIGHT:
            bg_y_position = 0
        
        bg_y_position += 5

        # draw enemies
        for enemy in enemies:
            enemy.draw(WIN)

        player_ship.draw(WIN)


    #game loop
    while run:
        #set FPS
        clock.tick(FPS)

        draw_window()
        
        #create random enemies
        if len(enemies) == 0:
            #wave_lenght = 5
            for i in range(wave_lenght):
                enemy_ship = Enemy(random.randrange(30,WIDTH-60), random.randrange(-1500,-300))
                enemies.append(enemy_ship)
        #events
        for event in pygame.event.get():
            #quit event
            if event.type == pygame.QUIT:
                run = False

        #move feature if 

        keys = pygame.key.get_pressed() 
        if keys[pygame.K_a] and player_ship.x - player_velocity > 0: #left
            player_ship.x -= player_velocity
        if keys[pygame.K_d] and player_ship.x + player_ship.get_width() - player_velocity < WIDTH: #right
            player_ship.x += player_velocity
        if keys[pygame.K_s] and player_ship.y + player_ship.get_height() - player_velocity < HEIGHT: #down
            player_ship.y += player_velocity    
        if keys[pygame.K_w] and player_ship.y - player_velocity > 0: #up
            player_ship.y -= player_velocity 
        
        #shoot feature
        if keys[pygame.K_SPACE]:
            player_ship.shoot()

        #move enemies
        for e in enemies[:]:
            e.move_laser(laser_velocity, player_ship)
            e.move_ship(enemy_velocity)
            e.cool_down_f()

            if e.y >= 0:
                if random.randrange(0,2+FPS) == 1:
                    e.shoot()

            if e.y > HEIGHT:
                sys.exit()
                enemies.remove(e)
        

        #player ship methods needed
        player_ship.move_laser(-laser_velocity, enemies)
        player_ship.cool_down_f()
        player_ship.enemy_collision(enemies)

    pygame.quit()

#make sure the game only opens through the main file

if __name__ == "__main__": 
    main()