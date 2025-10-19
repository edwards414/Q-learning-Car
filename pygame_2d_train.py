import pygame
import math
# import speed_control  # 匯入 speed_control.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time

screen_width = 1500
screen_height = 800
# check_point = ((1200, 660), (1250, 120), (190, 200), (1030, 270), (250, 475), (650, 690))
# check_point=((868,623),(1040,418),(919,117),(548,249),(418,373),(637,616))
        
# start_point= [637,616]
# (1152,301),(964,76),(537,94),(403,312),(585,618),(910,644),(1045,489)
# check_point = ((1332,659),(1088,396),(1162,132),(950,269),(708,161),(636,400),(205,154),(200,339),(282,576),(570,675))


class Car:
    def __init__(self, car_file, map_file, pos):
        self.surface = pygame.image.load(car_file)
        self.map = pygame.image.load(map_file)
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotate_surface = self.surface
        self.pos =[pos[0] , pos[1] ]
        self.angle = 0
        self.speed = 0
        self.center = [self.pos[0] , self.pos[1] ]
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.current_check = 0
        self.prev_distance = 0
        self.cur_distance = 0
        self.goal = False
        self.check_flag = False
        self.distance = 0
        self.time_spent = 0
        
        for d in range(-90, 120, 45):
            self.check_radar(d)
        for d in range(-90, 120, 45):
            self.check_radar_for_draw(d)

    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)

    def draw_collision(self, screen):
        for i in range(4):
            x = int(self.four_points[i][0])
            y = int(self.four_points[i][1])
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 5)   #只要新地圖的白色區域 (RGB: (255, 255, 255, 255)) 仍然代表牆壁或障礙物 

    def draw_radar(self, screen):
        for r in self.radars_for_draw:
            pos, dist = r
            pygame.draw.line(screen, (0, 255, 0), self.center, pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), pos, 3)

    def check_collision(self):
        self.is_alive = True
        for p in self.four_points:
            if self.map.get_at((int(p[0]), int(p[1]))) == (255, 255, 255, 255):
                self.is_alive = False

                break

    # Car 類內新增方法來計算速度（以 km/h 顯示）
    def get_speed_kmh(self):
        # 1 像素 = 5 cm，將速度從像素/s 轉換為 km/h
        speed_kmh = self.speed * 8 * 3600 / 100000
        return speed_kmh
    

    def check_radar(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        # 雷達最大距離len < 300
        while not self.map.get_at((x, y)) == (255, 255, 255, 255) and len < 200:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])


    def check_radar_for_draw(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while not self.map.get_at((x, y)) == (255, 255, 255, 255) and len < 2000:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars_for_draw.append([(x, y), dist])

    def check_checkpoint(self):
        p = check_point[self.current_check]
        self.prev_distance = self.cur_distance
        dist = get_distance(p, self.center)
        # print(f"    當前檢查點索引: {self.current_check}, 目標座標: {p}, 車輛中心: {self.center}, 距離: {dist}") # 新增 print 語句

        if dist < 70:
            # print(f"    通過檢查點 {self.current_check + 1}!") # 新增 print 語句
            self.current_check += 1
            self.prev_distance = 9999
            self.check_flag = True
            if self.current_check >= len(check_point):
                self.current_check = 0
                self.goal = True
            else:
                self.goal = False


        self.cur_distance = dist


    def update(self):
        import main
        #check speed
        self.speed -= 0.5
        if self.speed > 10:
            self.speed = main.adjust_speed(self.speed)  # 呼叫 speed_control 的函式
        if self.speed < 1:
            self.speed = main.adjust_speed(self.speed)  # 呼叫 speed_control 的函式

        #check position
        self.rotate_surface = rot_center(self.surface, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        if self.pos[0] < 20:
            self.pos[0] = 20
        elif self.pos[0] > screen_width - 120:
            self.pos[0] = screen_width - 120

        self.distance += self.speed
        self.time_spent += 1
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        if self.pos[1] < 20:
            self.pos[1] = 20
        elif self.pos[1] > screen_height - 120:
            self.pos[1] = screen_height - 120

        # caculate 4 collision points
        self.center = [int(self.pos[0]) +50, int(self.pos[1])+50]
        len = 40
        # 計算車輛四個角的位置
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * len]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * len]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * len]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * len]
        self.four_points = [left_top, right_top, left_bottom, right_bottom]

class PyGame2D:
    def __init__(self,image_map,start_point,check_point_all):
        pygame.init()
        # self.screen = None    # 
        self.screen = pygame.display.set_mode((screen_width, screen_height))     #要顯示的話打開
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 30)
        self.fiest_start_point=start_point
        self.image_path = image_map  # 儲存傳入的圖片路徑
        
        self.check_point_all=check_point_all
        global check_point
        check_point= self.check_point_all
        # self.car = Car('car.png', 'map.png', [700, 650])
        
        self.car = Car('car.png', self.image_path,self.fiest_start_point.copy())
        self.start_time = time.time()  # 新增：開始計時

        # self.game_speed = 60
        self.mode = 0
        self.out_of_bounds_count = 0  # 初始化出界次數

        #  self.speed = speed_control.adjust_speed(self.speed)  # 呼叫 speed_control 的函式


    def action(self, action):
        import main
        # print(action)
        if action == 0:
            self.car.speed += main.angle_speed(action)      #表示車輛加速 # self.car.speed += 2      #表示車輛加速
        if action == 1: 
            self.car.angle += main.angle_speed(action)    #表示向左轉 5 度
        elif action == 2:
            self.car.angle -= main.angle_speed(action)    #表示向右轉 5 度
        self.car.update()
        self.car.check_collision()
        self.car.check_checkpoint()

        if not self.car.is_alive:
            return
        self.car.radars.clear()
        for d in range(-90, 120, 45):
            self.car.check_radar(d)

    def evaluate(self):
        import main
        reward = 0
        if self.car.check_flag:                                         # 如果車輛觸發了 check_flag（可能是經過某個檢查點）
            self.car.check_flag = False                                 # 重置 check_flag，避免重複觸發
            reward = main.flag_reward() - self.car.time_spent
            # print("獎勵時間",self.car.time_spent)           # 根據時間給獎勵，時間越少獎勵越高
            self.car.time_spent = 0                                     # 重置計時器
        if not self.car.is_alive:
             reward = main.punish_reward(self.car.distance) # 讓距離仍有部分獎勵
        elif self.car.goal:
            reward = main.goal_distance_reward(self.car.distance)       # 否則，根據行駛距離給予獎勵，鼓勵探索

                  # 根據時間給獎勵，時間越少獎勵越高

            
        return reward
    


    # 減少負獎勵的影響，避免 agent 害怕探索

    # 保持獎勵平衡 (1000 vs. -500)，讓學習更穩定

    # 加入中間獎勵，根據距離給予持續回饋，鼓勵積極行動



    # def evaluate(self):
    #     reward = 0
        
    #     if self.car.check_flag:                          # 如果車輛觸發了 check_flag（可能是經過某個檢查點）
    #         self.car.check_flag = False                  # 重置 check_flag，避免重複觸發

    #         reward = 2000 - self.car.time_spent          # 根據時間給獎勵，時間越少獎勵越高
    #         self.car.time_spent = 0                      # 重置計時器
        
    #     if not self.car.is_alive:
    #          reward = -500 + self.car.distance * 0.1  # 讓距離仍有部分獎勵

    #     elif self.car.goal:
    #         reward = self.car.distance * 0.1
            
    #     return reward
    # def is_done(self):
    #     if not self.car.is_alive or self.car.goal:
    #         self.car.current_check = 0
    #         self.car.distance = 0
    #         return True
    #     return False

    def is_done(self):
        if self.car.goal:
            total_time = time.time() - self.start_time
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            print("全部檢查點已經通過")
            # print(f"總耗時：{minutes} 分 {seconds} 秒")
            sys.exit()
        if not self.car.is_alive or self.car.goal:
            new_pos = self.fiest_start_point.copy()
            # print(f"    重置到起始位置: {new_pos}")
            self.car.pos = new_pos
            self.car.center = [new_pos[0] + 50, new_pos[1] + 50]
            self.car.angle = 0
            self.car.speed = 0
            self.car.distance = 0
            return False
        else:
            return False

    
        # 要回傳的   這裡!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def observe(self):
        # return state
        radars = [int(r[1] / 30) for r in self.car.radars]
        speed = int(self.car.get_speed_kmh() / 10)
        angle = int(self.car.angle / 10) % 36
        radars = self.car.radars
        ret = [0, 0, 0, 0, 0]
        for i, r in enumerate(radars):
            ret[i] = int(r[1] / 30)
        return tuple(ret)
# KeyError: (1, 2, 6, 3, 2)  雷達的值



    def view(self):
        # draw game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.mode += 1
                    self.mode = self.mode % 3
    
        self.screen.blit(self.car.map, (0, 0))
        # 繪製檢查點
        for i, point in enumerate(check_point):
            color = (0, 255, 0) if i == self.car.current_check else (255, 0, 0)
            pygame.draw.circle(self.screen, color, point, 10)
        
            self.car.draw(self.screen)

        if self.mode == 1:
            self.screen.fill((0, 0, 0))

        self.car.radars_for_draw.clear()
        for d in range(-90, 120, 45):
            self.car.check_radar_for_draw(d)

        pygame.draw.circle(self.screen, (255, 255, 0), check_point[self.car.current_check], 70, 1)
        self.car.draw_collision(self.screen)
        self.car.draw_radar(self.screen)
        self.car.draw(self.screen)

        # 獲取速度並顯示
        speed_kmh = self.car.get_speed_kmh()
        speed_text = self.font.render(f"Speed: {speed_kmh:.1f} km/h", True, (0, 0, 0))
        self.screen.blit(speed_text, (10, 10))  # 顯示速度在畫面左上角

        # text = self.font.render("Press "m" , True, (255, 255, 0))
        # text_rect = text.get_rect()
        # text_rect.center = (screen_width/2, 100)
        # self.screen.blit(text, text_rect)

        pygame.display.flip()
        # self.clock.tick(self.game_speed)

def get_distance(p1, p2):
	return math.sqrt(math.pow((p1[0] - p2[0]), 2) + math.pow((p1[1] - p2[1]), 2))

def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image
