from stable_baselines3 import PPO
from GuiltyGearEnv import GuiltyGearEnv

env = GuiltyGearEnv()

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)  # short run just to test

obs, _ = env.reset()
for _ in range(10):
    action, _ = model.predict(obs)
    obs, reward, done, _, _ = env.step(action)
    print(f"Action: {action}, Reward: {reward}, State: {obs}")
    if done:
        obs, _ = env.reset()