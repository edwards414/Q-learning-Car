import sys
import numpy as np
import random
import gym
# import gym_game
import os
from cus_train import CustomEnv
out_of_bounds_count= 0 
# 儲存 Q 表格到檔案
def save_model(q_table, filename):
    """Save the Q-table to a file."""
    np.save(filename, q_table)

# 從檔案載入 Q 表格
def load_model(filename):
    """Load the Q-table from a file."""
    if os.path.exists(filename):
        return np.load(filename)
    return None

def angle_speed(action):
    if action == 0:
        return 2         #表示車輛加速
    if action == 1: 
        return 5        #表示向左轉 5 度
    elif action == 2:
        return 5        #表示向右轉 5 度
    
def adjust_speed(speed):   #限制speed的函式
        if speed > 10:
            return 10
        elif speed < 1:
            return 1
        

def flag_reward():   #如果觸發了checkpoint再根據時間給獎勵，時間越少獎勵越高
    return 2000

def punish_reward(distance):    # 懲罰:讓距離仍有部分獎勵
    return -1500+(distance*0.1)

def goal_distance_reward(goal_distance):   # 否則，根據行駛距離給予獎勵，鼓勵探索
    return goal_distance*0.1
    

        
# 使用 epsilon-greedy 方法選擇動作
def choose_action(state, q_table, action_size, epsilon):      #兩個Q-learning（Double Q-learning）  上置信界限（UCB, Upper Confidence Bound）  Softmax Action Selection
    """Epsilon-greedy action selection."""
    if np.random.rand() < epsilon:
        return np.random.choice(action_size)
    return np.argmax(q_table[state])

# 更新 Q 表格，根據 Q-learning 更新公式
def update_q_table(q_table, state, action, reward, next_state, learning_rate, gamma):
    """Q-learning update rule."""
    q_value = q_table[state][action]
    best_next_q = np.max(q_table[next_state])
    q_table[state][action] = (1 - learning_rate) * q_value + learning_rate * (reward + gamma * best_next_q)

# 訓練 Q-learning 代理人
def train_q_learning(env, total_episodes, max_steps, learning_rate, gamma, epsilon_start, epsilon_end, epsilon_decay):
    global out_of_bounds_count
    action_size = env.action_space.n  # 取得可用的動作數量
    state_size = tuple((env.observation_space.high + np.ones(env.observation_space.shape)).astype(int))
    q_table = np.zeros(state_size + (action_size,))  # 初始化 Q 表格
    best_reward = -float('inf')  # 記錄最佳獎勵
    model_filename = "best_q_table.npy"
    loaded_q_table = load_model(model_filename)  # 嘗試載入現有的最佳模型
    if loaded_q_table is not None:
        q_table = loaded_q_table
        print("Loaded best model from file.")
    
    epsilon = epsilon_start  # 初始化探索率
    
    for episode in range(total_episodes):
        state = env.reset()
        total_reward = 0
        out_of_bounds_count += 1
        
        for step in range(max_steps):
            action = choose_action(state, q_table, action_size, epsilon)   # 選擇動作
            next_state, reward, done, _ = env.step(action)   # 執行動作並獲取回饋
            
            update_q_table(q_table, state, action, reward, next_state, learning_rate, gamma)  # 更新 Q 表格
            
            total_reward += reward
            state = next_state
            # env.render(out_of_bounds_count=out_of_bounds_count)   # 渲染畫面
            
            if done:
                break
        
        epsilon = max(epsilon_end, epsilon * epsilon_decay)
        
        if total_reward > best_reward:
            best_reward = total_reward
            save_model(q_table, model_filename)  # 儲存最佳模型
            print(f"New best model saved with total reward: {best_reward}")
        
        print(f"Episode: {episode + 1}, Total Reward: {total_reward}, Epsilon: {epsilon}")
        # Epsilon = 0.976，表示 agent 有 97.6% 的機率 隨機選擇動作，2.4% 的機率選擇已知的最佳動作。
    print(f"Total Out of Bounds Count: {out_of_bounds_count}") #出界次數
    env.close()


def start_point_first(txt_path):
    f = open(txt_path)
    lines = f.readlines() 
    text = []
    start_line = lines[0].strip()  
    if start_line: 
        text.append(start_line.split(','))


    position = [int(num) for sublist in text for num in sublist]  
    print("測",position)  
    return position


def all_checkpoint(txt_path):
    f = open(txt_path)
    lines = f.readlines()  
    checkpoint_line = lines[1].strip()  
    # 去除字符串中的括號和拆開
    checkpoints = [
        (int(checkpoint.split(',')[0]), int(checkpoint.split(',')[1]))
        for checkpoint in checkpoint_line.strip('()').split('),(')
    ]

    print("測", checkpoints)  
    return checkpoints


if __name__ == "__main__":
    image_path="test_map.png"
    start_point=start_point_first("checkpoint_te.txt")
    check_point=all_checkpoint("checkpoint_te.txt")
    env = CustomEnv(image_path,start_point,check_point)
    MAX_EPISODES = 7300
    MAX_TRY = 600
    epsilon = 1
    epsilon_decay = 0.999
    learning_rate = 0.1
    gamma = 0.9
    
    train_q_learning(env, MAX_EPISODES, MAX_TRY, learning_rate, gamma, epsilon, 0.01, epsilon_decay)
