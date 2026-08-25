# DASF_TRON2A 平地速度任务

该目录仅包含 DASF_TRON2A 的 MDP 配置，避免修改 SF_TRON2A/WF_TRON2A 的环境行为。

## 隔离边界

- DASF_TRON2A 自带 scene、observation、event、curriculum 和 reward 实现，不继承
  SF_TRON2A/WF_TRON2A 的环境配置。
- DASF_TRON2A Task ID 使用字符串 entry point 延迟加载；导入 SF/WF task 时不会
  提前导入 DASF_TRON2A asset、agent 或环境配置。
- 观测归一化由 DASF_TRON2A 专用的 `EmpiricalNormalizedActorCritic` 和
  `NormalizedPPO` 实现。SF/WF 继续使用原 `ActorCritic`、`PPO` 和原
  checkpoint state 结构。
- SF/WF 的配置、共享 MDP、原 actor-critic、原 PPO 和通用导出函数均保持
  仓库原实现。

## 文件边界

### DASF_TRON2A 独占文件

下列文件当前只由 DASF_TRON2A 任务加载，SF_TRON2A/WF_TRON2A 不导入或
实例化这些实现。

| 路径 | 职责 |
|---|---|
| `assets/config/dasf_tron2a_cfg.py` | 定义 `DASF_TRON2A_CFG`、初始姿态、关节默认位置及 6 组执行器参数，并指向 DASF_TRON2A USD。 |
| `assets/usd/DASF_TRON2A/` | DASF_TRON2A 独立机器人资产目录。训练直接加载 `usd/robot.usd`；URDF、XML、Xacro 和 meshes 是该形态的模型源与配套资产。 |
| `tasks/locomotion/cfg/DASF_TRON2A/limx_base_env_cfg.py` | DASF_TRON2A 核心环境：scene、commands、20 维 actions、observations、events、rewards、terminations、curriculum 和仿真频率。 |
| `tasks/locomotion/cfg/DASF_TRON2A/mdp.py` | DASF_TRON2A 专用 observation/event/curriculum 辅助函数，包括 phase、编码器偏置、足底材质及质量/惯量随机化。 |
| `tasks/locomotion/cfg/DASF_TRON2A/rewards.py` | DASF_TRON2A 专用奖励计算，包括速度跟踪、步态、摆臂、脚臂协调、clearance、slip、landing、posture 和全身角动量。 |
| `tasks/locomotion/robots/limx_dasf_tron2a_env_cfg.py` | 将 DASF_TRON2A asset 装配到独立环境，并定义训练与 Play 的 BlindFlat 变体。 |
| `tasks/locomotion/agents/dasf_rsl_rl_ppo_cfg.py` | DASF_TRON2A 的 PPO、actor/critic、history encoder、归一化和训练迭代配置。 |
| `rsl_rl/rsl_rl/modules/normalized_actor_critic.py` | DASF_TRON2A 使用的 actor/critic 独立 running mean/std 归一化，以及包含 actor normalizer 的 JIT 导出。 |
| `rsl_rl/rsl_rl/algorithm/normalized_ppo.py` | DASF_TRON2A 使用的 PPO rollout 路径，在采样时更新 actor/critic 归一化统计量。 |

`tasks/locomotion/cfg/DASF_TRON2A/__init__.py` 只负责导出该配置包；本
`README.md` 只是说明文档，二者不包含额外训练逻辑。

### 共享文件中的 DASF_TRON2A 接入点

以下文件仍由 SF/WF/DASF_TRON2A 共用，不能视为 DASF_TRON2A 独占文件；
其中仅增加了按任务或配置触发的 DASF_TRON2A 分支。

| 路径 | DASF_TRON2A 接入方式 |
|---|---|
| `tasks/locomotion/robots/__init__.py` | 共享 Gym 注册表。DASF_TRON2A 的两个 Task ID 使用字符串 entry point 延迟加载独占 env 和 agent。 |
| `rsl_rl/rsl_rl/runner/on_policy_runner.py` | 共享 runner。仅当 `empirical_normalization=True` 时选择 `EmpiricalNormalizedActorCritic`，仅当 `class_name="NormalizedPPO"` 时选择 `NormalizedPPO`；SF/WF 继续选择原实现。 |
| `scripts/rsl_rl/play.py` | 共享 Play/导出入口。只有 actor-critic 提供 `get_inference_actor()` 时，才导出包含 normalizer 的 DASF_TRON2A actor。 |

以下基础能力明确与 SF/WF 共用：

- `actuators/` 下的 `DelayedImplicitActuatorCfg` 和延迟 actuator 实现；
- `utils/wrappers/rsl_rl/rl_mlp_cfg.py` 中的 `EncoderCfg`、PPO 配置和导出工具；
- `rsl_rl/rsl_rl/modules/mlp_encoder.py`、基础 `ActorCritic`、基础 `PPO`、
  storage 和通用训练入口 `scripts/rsl_rl/train.py`。

### 加载链

```text
DASF_TRON2A Task ID
├── tasks/locomotion/robots/__init__.py                 # 共享注册表
├── tasks/locomotion/robots/limx_dasf_tron2a_env_cfg.py # DASF 独占
│   ├── tasks/locomotion/cfg/DASF_TRON2A/               # DASF 独占环境/MDP/reward
│   └── assets/config/dasf_tron2a_cfg.py                # DASF 独占 asset cfg
│       └── assets/usd/DASF_TRON2A/usd/robot.usd        # DASF 独占 USD 入口
└── tasks/locomotion/agents/dasf_rsl_rl_ppo_cfg.py      # DASF 独占 agent cfg
    └── rsl_rl/rsl_rl/runner/on_policy_runner.py        # 共享 runner
        ├── modules/normalized_actor_critic.py           # DASF 独占归一化
        └── algorithm/normalized_ppo.py                  # DASF 独占 PPO 路径
```

## Task ID

- 训练：`Isaac-Limx-DASF-TRON2A-Blind-Flat-v0`
- 推理：`Isaac-Limx-DASF-TRON2A-Blind-Flat-Play-v0`

## 20 维动作顺序

动作由两个 position action term 顺序拼接而成。

下半身 10 维：

1. `proximal_pitch_L_Joint`
2. `proximal_roll_L_Joint`
3. `proximal_yaw_L_Joint`
4. `knee_L_Joint`
5. `ankle_pitch_L_Joint`
6. `proximal_pitch_R_Joint`
7. `proximal_roll_R_Joint`
8. `proximal_yaw_R_Joint`
9. `knee_R_Joint`
10. `ankle_pitch_R_Joint`

上半身 10 维：

1. `proximal_pitch_L_U_Joint`
2. `proximal_roll_L_U_Joint`
3. `proximal_yaw_L_U_Joint`
4. `elbow_L_U_Joint`
5. `wrist_roll_L_U_Joint`
6. `proximal_pitch_R_U_Joint`
7. `proximal_roll_R_U_Joint`
8. `proximal_yaw_R_U_Joint`
9. `elbow_R_U_Joint`
10. `wrist_roll_R_U_Joint`

以下 6 个关节不进入策略动作，由 position PD 保持默认位置：

- `wrist_yaw_[LR]_U_Joint`
- `wrist_pitch_[LR]_U_Joint`
- `head_yaw_Joint`
- `head_pitch_Joint`

## 启动命令

```bash
python scripts/rsl_rl/train.py \
  --task Isaac-Limx-DASF-TRON2A-Blind-Flat-v0 \
  --num_envs 4096 \
  --headless

python scripts/rsl_rl/play.py \
  --task Isaac-Limx-DASF-TRON2A-Blind-Flat-Play-v0 \
  --num_envs 32
```

实机部署时必须沿用本页记录的动作顺序，并另行对齐观测顺序、关节零点、关节符号、坐标系、
控制频率、PD 参数和安全限幅。
