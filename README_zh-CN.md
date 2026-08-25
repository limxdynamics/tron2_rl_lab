<!--
  SPDX-FileCopyrightText: 2024-2026 LimX Dynamics Technology Co., Ltd.
  SPDX-License-Identifier: Apache-2.0
-->

# tron2_rl_lab

[English](README.md) | [中文](README_zh-CN.md)

> **发布渠道：** 本仓库的开源主副本托管于
> [`github.com/limx-tron2/tron2_rl_lab`](https://github.com/limx-tron2/tron2_rl_lab)。

基于 [Isaac Lab](https://isaac-sim.github.io/IsaacLab/) 的 LimX **TRON2A**
强化学习训练栈，使用 PPO 训练 locomotion 策略。本仓库专注于平地
（Flat）训练，支持 SF（sole-foot）、WF（wheel-foot），以及由双足、
双臂和头部组成的 DASF_TRON2A 全身机器人。

## 许可与归属

本项目遵循 **Apache License, Version 2.0**（2004 年 1 月）发布。完整
许可文本位于仓库根目录 [`LICENSE`](LICENSE)。SPDX 标识符：`Apache-2.0`。

- [`NOTICE`](NOTICE) — 必需的归属声明。
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) — 各组件来源
  说明：源自 Isaac Lab 的扩展、内嵌的 `rsl_rl/` fork（BSD-3-Clause）、
  开发工具的许可文本（包含一项在发布前必须分类的 GPL 条目）、
  随附的 STL / USD 资产以及文档媒体。
- [`SECURITY.md`](SECURITY.md) — 报告安全漏洞或与安全相关的
  RL / 奖励 / 终止问题的方法。
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — 开发环境搭建、内嵌
  fork 的更新策略、PR 检查清单、DCO 签署。
- [`CHANGELOG.md`](CHANGELOG.md) — 发布说明及当前未解决的
  **`⚠ TO CONFIRM`** 项（首个公开 tag 的阻塞项）。

关于子目录的说明：

- `exts/bipedal_locomotion/setup.py` 声明
  `license="Apache-2.0"`，与顶层 LICENSE 保持一致。
  基于 Isaac Lab 派生的逐文件归属审计仍标记为
  `⚠ TO CONFIRM`（见 `THIRD_PARTY_NOTICES.md` §1）。
- `rsl_rl/` 是
  [`leggedrobotics/rsl_rl`](https://github.com/leggedrobotics/rsl_rl)
  的 **内嵌 fork**，遵循 **BSD-3-Clause**；保留了上游的版权声明
  （见 `THIRD_PARTY_NOTICES.md` §2 及
  `CONTRIBUTING.md#vendored-rsl_rl-update-policy`）。

对上游的本地修改摘要见
[`CHANGES_VS_UPSTREAM.md`](CHANGES_VS_UPSTREAM.md) 与
[`licenses/dependencies/README.md`](licenses/dependencies/README.md)。

## 适用范围与除外

本仓库 **包含**：

- Isaac Lab 扩展 `exts/bipedal_locomotion/`，含 TRON2A 的 env /
  MDP / actuator / robot cfg。
- 内嵌的 `rsl_rl/` PPO 训练器与 on-policy runner。
- 入口脚本 `scripts/rsl_rl/{train,play}.py`，含 ONNX / JIT 策略
  导出（`scripts/rsl_rl/play.py:108-118`）。
- `SF_TRON2A`、`WF_TRON2A` 与 `DASF_TRON2A` 变体的 USD / STL 资产，位于
  `exts/bipedal_locomotion/bipedal_locomotion/assets/usd/`。
- 位于 `doc/` 的仿真回放 GIF（MuJoCo、Gazebo、实机）。

**不包含** — 有意为之：

- **不含训练后的策略**（`*.pt`、`*.pth`、`*.ckpt`、`*.onnx`、
  `*.jit`）。请自行训练，或从 LimX 内部制品库 / GitHub Release
  获取。
- **不含训练日志、TensorBoard events 或 Weights & Biases 记录。**
  `logs/`、`wandb/`、`events.out.tfevents.*` 均被 `.gitignore`
  屏蔽并在 CI 中拦截。
- **暂无测试套件。** CI 仅覆盖 `python -m py_compile`、`ruff`、
  违禁产物扫描与许可扫描。在无头 GPU worker 上跑一次冒烟训练
  作为后续工作跟踪。
- **不含 Isaac Sim 的再分发。** 必须自行从 NVIDIA 获取 Isaac Sim
  5.1 并接受 NVIDIA 专有 EULA，才可安装本训练栈。本仓库不授予
  Isaac Sim 的任何许可。
- **不含 GPU / 驱动。** 4096-env 训练需要 CUDA 兼容 GPU
  （推荐显存 ≥ 12 GB）。本仓库不附带驱动、CUDA 或 PyTorch wheel。
- **不含 SDK 二进制、固件、标定值、客户配置或厂商 CAD。**

实机部署代码（实机上电、ROS 驱动、MuJoCo / Gazebo 集成）请参考
下文
[MuJoCo 仿真与实机部署](#mujoco-仿真与实机部署) 与
[Gazebo 仿真与实机部署](#gazebo-仿真与实机部署) 中引用的姊妹仓库。

## 仓库结构

```
.
├── exts/bipedal_locomotion/   # Isaac Lab extension：env/asset/MDP/robot cfg
├── rsl_rl/                    # 项目内 vendored 的 rsl_rl fork（PPO + on-policy runner）
├── scripts/rsl_rl/            # 训练 / play 入口（train.py / play.py / cli_args.py）
└── logs/                      # 训练日志与模型权重
```

## 环境要求

- **Isaac Sim 5.1** + **Isaac Lab 2.3.1**
- Python 3.10
- GPU（推荐 ≥ 12 GB 显存，4096 envs 训练）

## 安装

```bash
# 1. clone 仓库
git clone <repo-url> tron1_rl_lab
cd tron1_rl_lab

# 2. editable install extension 与 vendored rsl_rl
pip install -e exts/bipedal_locomotion
pip install -e rsl_rl
```

## IsaacSim 训练

任务 ID 均在 [exts/bipedal_locomotion/bipedal_locomotion/tasks/locomotion/robots/__init__.py](exts/bipedal_locomotion/bipedal_locomotion/tasks/locomotion/robots/__init__.py) 中注册。

### 1. 训练模型

```bash
# === Solefoot (SF) ===
python scripts/rsl_rl/train.py --task Isaac-Limx-SF-TRON2A-Blind-Flat-v0 --num_envs 4096 --headless

# === Wheelfoot (WF) ===
python scripts/rsl_rl/train.py --task Isaac-Limx-WF-TRON2A-Blind-Flat-v0 --num_envs 4096 --headless

# === Dual-arm Solefoot (DASF_TRON2A) ===
python scripts/rsl_rl/train.py --task Isaac-Limx-DASF-TRON2A-Blind-Flat-v0 --num_envs 4096 --headless
```

*常用选项：*
- `--checkpoint_path <path>`: 从某 .pt 恢复。
- `--video`: 开启录像。
- `--max_iterations N`: 覆盖最大迭代数。

日志路径：`logs/rsl_rl/<experiment_name>/<timestamp>_<run_name>/`

### 2. 运行推理 (Play)

用 `-Play-v0` 后缀的任务 ID。Play cfg 使用更少 env、关闭域随机化、简化地形。

```bash
# Solefoot (SF)
python scripts/rsl_rl/play.py --task Isaac-Limx-SF-TRON2A-Blind-Flat-Play-v0 --num_envs 32

# Wheelfoot (WF)
python scripts/rsl_rl/play.py --task Isaac-Limx-WF-TRON2A-Blind-Flat-Play-v0 --num_envs 32

# Dual-arm Solefoot (DASF_TRON2A)
python scripts/rsl_rl/play.py \
  --task Isaac-Limx-DASF-TRON2A-Blind-Flat-Play-v0 \
  --num_envs 32 \
  --checkpoint_path <path_to_model.pt>
```

*注意：* 默认加载最新 checkpoint，指定路径可用 `--checkpoint_path`。

### 3. Resume 续训

必须显式带 `--resume True` 才会加载 checkpoint。

```bash
# 方式 A：直接给 .pt 路径（推荐）
python scripts/rsl_rl/train.py --task Isaac-Limx-SF-TRON2A-Blind-Flat-v0 --resume True --checkpoint_path <path_to_model>

# 方式 B：按 run 名查找
python scripts/rsl_rl/train.py --task Isaac-Limx-SF-TRON2A-Blind-Flat-v0 --resume True --load_run <run_name>

# DASF_TRON2A 续训
python scripts/rsl_rl/train.py \
  --task Isaac-Limx-DASF-TRON2A-Blind-Flat-v0 \
  --resume True \
  --checkpoint_path <path_to_model.pt>
```

## 机器人形态

| 形态 | 结构 | 策略动作 | Task ID 前缀 |
|---|---|---:|---|
| SF_TRON2A | 双足 sole foot（ankle pitch） | 10 | `Isaac-Limx-SF-TRON2A-...` |
| WF_TRON2A | 双足 wheel foot | 10 | `Isaac-Limx-WF-TRON2A-...` |
| DASF_TRON2A | SF 双足 + 双臂 + 头部，26 个可动关节 | 20 | `Isaac-Limx-DASF-TRON2A-...` |

- [DASF_TRON2A 任务说明](exts/bipedal_locomotion/bipedal_locomotion/tasks/locomotion/cfg/DASF_TRON2A/README.md)

## 架构概览

项目分为三个主要部分：

1. **`exts/bipedal_locomotion/`** — Isaac Lab extension。包含 env / asset / MDP / robot cfg。
2. **`rsl_rl/`** — vendored fork。`scripts/rsl_rl/train.py` 会优先加载此路径下的算法库。
3. **`scripts/rsl_rl/`** — 训练与推理的入口脚本。

### 任务 Wiring 流程

通用任务 wiring：

1. **Gym 注册**：在 `tasks/locomotion/robots/__init__.py` 中将环境配置与 PPO 配置绑定到任务 ID。
2. **环境配置 (Env cfg)**：SF/WF 分别使用
   `tasks/locomotion/robots/limx_solefoot_tron2a_env_cfg.py` 和
   `tasks/locomotion/robots/limx_wheelfoot_tron2a_env_cfg.py`；
   DASF_TRON2A 使用
   `tasks/locomotion/robots/limx_dasf_tron2a_env_cfg.py` 装配独立环境。
3. **资产配置 (Asset cfg)**：SF/WF 使用
   `assets/config/solefoot_tron2a_cfg.py` /
   `assets/config/wheelfoot_tron2a_cfg.py`；DASF_TRON2A 通过
   `assets/config/dasf_tron2a_cfg.py` 加载独立 USD 和执行器参数。
4. **DASF_TRON2A MDP**：scene、observation、event、curriculum 和 reward 位于
   `tasks/locomotion/cfg/DASF_TRON2A/`。
5. **DASF_TRON2A agent**：`tasks/locomotion/agents/dasf_rsl_rl_ppo_cfg.py` 使用
   `NormalizedPPO`、history encoder 和独立 actor/critic normalization。

## MuJoCo 仿真与实机部署

- [MuJoCo 仿真仓库](https://github.com/example/tron1-mujoco-sim)
- [Python实机部署代码](https://github.com/example/tron1-deploy-python)

### MuJoCo 部署效果（SF / WF / DASF_TRON2A）

<p align="center">
  <img src="doc/mujoco_sf.gif" alt="MuJoCo SF" width="48%" />
  <img src="doc/mujoco_wf.gif" alt="MuJoCo WF" width="48%" />
</p>

<p align="center">
  <img src="doc/mujoco_dasf.GIF" alt="MuJoCo DASF_TRON2A" width="48%" />
</p>

- 无法直接预览时可下载查看：
  - [mujoco_sf.gif](doc/mujoco_sf.gif)
  - [mujoco_wf.gif](doc/mujoco_wf.gif)
  - [mujoco_dasf.GIF](doc/mujoco_dasf.GIF)

## Gazebo 仿真与实机部署

- [Gazebo 仿真仓库](https://github.com/example/tron1-gazebo-sim)
- [ROS实机部署代码](https://github.com/example/tron1-deploy-cpp)

### Gazebo 部署效果（SF / WF）

<p align="center">
  <img src="doc/gazebo_sf.gif" alt="Gazebo SF" width="48%" />
  <img src="doc/gazebo_wf.gif" alt="Gazebo WF" width="48%" />
</p>

- 无法直接预览时可下载查看：
  - [gazebo_sf.gif](doc/gazebo_sf.gif)
  - [gazebo_wf.gif](doc/gazebo_wf.gif)

## 实机部署效果（SF / WF / DASF_TRON2A，办公室场景）

<p align="center">
  <img src="doc/real_wf.GIF" alt="TRON2A WF 实机部署效果" width="48%" />
  <img src="doc/real_sf.GIF" alt="TRON2A SF 实机部署效果" width="48%" />
</p>

<p align="center">
  <img src="doc/real_dasf.GIF" alt="DASF_TRON2A 实机部署效果" width="48%" />
</p>

## 实机运行注意事项（强烈建议）

启动与落地流程建议固定为以下顺序，避免切策略瞬间冲击：

1. **将机器人吊起**，确保双脚不承重，先检查关节状态、急停和通信是否正常。
2. **先进入 IK 模式**，确认逆解控制稳定、姿态与期望一致。
3. **再缓慢将机器人放到地面**，观察接触是否平稳、是否出现异常抖动。
4. **最后切换到 walk 策略**，先低速小步验证，再逐步提升速度与动作幅度。

如出现异常（突发抖动、姿态发散、落地后冲击过大），请立即急停并回到吊起状态重新检查。

## 验证

下列命令与 CI 运行的内容一致（详见
[`.github/workflows/ci.yml`](.github/workflows/ci.yml)），在提交 PR
前本地跑一遍可减少来回沟通。

```bash
# 1. 对全部一方 Python 文件做字节码编译。
python -m py_compile $(git ls-files '*.py')

# 2. Lint（仅一方子目录；内嵌的 rsl_rl fork 不做风格约束）。
pip install ruff
ruff check --select F exts scripts

# 3. Editable-install dry run。Isaac Sim / Isaac Lab 不在 PyPI，
#    传递依赖解析可能失败；此步目的是校验 setup.py / pyproject.toml
#    的元数据。
pip install --dry-run -e exts/bipedal_locomotion
pip install --dry-run -e rsl_rl

# 4. 在装有 Isaac Sim / Isaac Lab 的机器上做可选的 import 冒烟：
python -c "import bipedal_locomotion; print(bipedal_locomotion.__file__)"

# 5. 确认没有训练产物 / SDK 二进制被暂存。
git ls-files | grep -iE \
  '(^|/)logs/|(^|/)wandb/|\.pt$|\.pth$|\.ckpt$|\.onnx$|events\.out\.tfevents\.' \
  && echo "!! training artifacts staged" && exit 1 || echo "ok"
```

在装有 Isaac Sim 5.1 / Isaac Lab 2.3.1 的机器上，可以跑一次简短的
端到端冒烟：

```bash
python scripts/rsl_rl/train.py --task Isaac-Limx-SF-TRON2A-Blind-Flat-v0 \
  --num_envs 16 --headless --max_iterations 2
```

## 参考资料

- [Isaac Lab](https://github.com/isaac-sim/IsaacLab)
- [RSL-RL](https://github.com/leggedrobotics/rsl_rl) — 内嵌 fork
  [`rsl_rl/`](rsl_rl) 的上游。

## 引用与支持

如在学术工作或公开成果中使用本训练栈，请引用本仓库：

```
@misc{limx_tron2_rl_lab_2026,
  title  = {tron2_rl_lab: RL training stack for the LimX TRON2A bipedal robot},
  author = {LimX Dynamics},
  year   = {2026},
  howpublished = {\url{https://github.com/limx-tron2/tron2_rl_lab}}
}
```

- **Bug 反馈 / 功能建议：** [GitHub Issues](https://github.com/limx-tron2/tron2_rl_lab/issues)。
- **问题咨询 / 集成协助：** [GitHub Discussions](https://github.com/limx-tron2/tron2_rl_lab/discussions)。
- **安全漏洞报告：** 邮件 `contact@limxdynamics.com`，另见
  [`SECURITY.md`](SECURITY.md)。
- **硬件 / 实机安全事件：** 邮件 `contact@limxdynamics.com`，
  主题前缀 `[tron2_rl_lab hardware]`，请勿在公开 Issue 中提交。
- **公司 / 商务联系：** <https://www.limxdynamics.com>。
