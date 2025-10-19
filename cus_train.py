import gym
from gym import spaces
import numpy 
from pygame_2d_train import PyGame2D    #記得改pygame_2d_model
import pygame
import numpy as np

class CustomEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}
    def __init__(self,image_path,start_point,check_point,render_mode=None):
        self.render_mode = render_mode
        self.image_path = image_path  # 儲存傳入的圖片路徑
        self.start_point = start_point  # 儲存傳入的圖片路徑
        self.check_point=check_point
        self.pygame = PyGame2D(self.image_path,self.start_point,self.check_point)
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(numpy.array([0, 0, 0, 0, 0]), numpy.array([10, 10, 10, 10, 10]), dtype=numpy.int32)

    def reset(self, seed=None, options=None):
        del self.pygame
        self.pygame = PyGame2D(self.image_path,self.start_point,self.check_point)
        obs = self.pygame.observe()
        return obs
#   每一步做的事情
    def step(self, action):
        self.pygame.action(action)
        obs = self.pygame.observe()
        reward = self.pygame.evaluate()
        done = self.pygame.is_done()
        return obs, reward, done, {}
# mode="human"
    def render(self, mode="rgb_array", close=False, out_of_bounds_count=0,speed=0):
        self.screen = None  # 不在初始化時建立畫面

        # 繪製遊戲畫面
        self.pygame.view()      #不顯示記得註解

        # 顯示出界次數
        out_of_bounds_text = self.pygame.font.render(
            f"Out-of-Bounds Count: {out_of_bounds_count}", True, (0, 0, 0)
        )
        self.pygame.screen.blit(out_of_bounds_text, (10, 50))  # 左上角
        if mode == "human":
            self.pygame.view()  # 在視窗中顯示畫面
            return None
        elif mode == "rgb_array":
            return self._get_frame()  # ✅ 回傳 NumPy 陣列
        
        pygame.display.update()   #不顯示記得註解

    def _get_frame(self):
        frame = pygame.surfarray.array3d(self.pygame.screen)  # 取得畫面
        frame = np.transpose(frame, (1, 0, 2))  # 轉換維度 (Pygame 預設維度不同)
        return frame  # 回傳 NumPy 陣列



