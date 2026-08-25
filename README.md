<!--
  SPDX-FileCopyrightText: 2024-2026 LimX Dynamics Technology Co., Ltd.
  SPDX-License-Identifier: Apache-2.0
-->

# tron2_rl_lab

[English](README.md) | [中文](README_zh-CN.md)

> **Distribution:** the primary open-source copy of this repository is
> hosted at
> [`github.com/limx-tron2/tron2_rl_lab`](https://github.com/limx-tron2/tron2_rl_lab).

Reinforcement learning training stack for the LimX **TRON2A** bipedal
robot, built on top of
[Isaac Lab](https://isaac-sim.github.io/IsaacLab/) and using PPO to
train locomotion policies. This repository focuses on flat-terrain
training and supports the **SF** (sole-foot), **WF** (wheel-foot), and
**DASF_TRON2A** full-body variants. DASF_TRON2A combines the sole-foot
lower body with two arms and a head.

## License & attribution

This project is distributed under the **Apache License, Version 2.0**
(January 2004). The full text is in [`LICENSE`](LICENSE) at the root
of the repository. SPDX identifier: `Apache-2.0`.

- [`NOTICE`](NOTICE) — required attribution notice.
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) — per-component
  provenance: the Isaac Lab-derived extension, the vendored
  `rsl_rl/` fork (BSD-3-Clause), dev-tool license texts (including
  a GPL entry that must be classified before release), bundled
  STL / USD assets, and doc media.
- [`SECURITY.md`](SECURITY.md) — how to report a vulnerability or a
  safety-adjacent RL / reward / termination issue.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — dev setup, vendored-fork
  update policy, PR checklist, DCO sign-off.
- [`CHANGELOG.md`](CHANGELOG.md) — release notes and the currently
  outstanding **`⚠ TO CONFIRM`** items that block the first public
  tag.

Note on subtrees:

- `exts/bipedal_locomotion/setup.py` declares
  `license="Apache-2.0"`, aligned with the top-level LICENSE. The
  per-file Isaac-Lab-derivation audit is tracked separately as
  `⚠ TO CONFIRM` in `THIRD_PARTY_NOTICES.md` §1.
- `rsl_rl/` is a **vendored fork** of
  [`leggedrobotics/rsl_rl`](https://github.com/leggedrobotics/rsl_rl)
  under **BSD-3-Clause**; upstream copyright notices are retained
  (see `THIRD_PARTY_NOTICES.md` §2 and
  `CONTRIBUTING.md#vendored-rsl_rl-update-policy`).

For a summary of local modifications relative to upstream, see
[`CHANGES_VS_UPSTREAM.md`](CHANGES_VS_UPSTREAM.md) and
[`licenses/dependencies/README.md`](licenses/dependencies/README.md).

## Scope / not included

**Included** in this repository:

- Isaac Lab extension `exts/bipedal_locomotion/` with env / MDP /
  actuator / robot cfg for TRON2A.
- Vendored `rsl_rl/` PPO trainer and on-policy runner.
- Entry scripts `scripts/rsl_rl/{train,play}.py`, including ONNX /
  JIT policy export
  (`scripts/rsl_rl/play.py:108-118`).
- Bundled USD / STL assets for the `SF_TRON2A`, `WF_TRON2A`, and
  `DASF_TRON2A` variants under
  `exts/bipedal_locomotion/bipedal_locomotion/assets/usd/`.
- Simulator playback GIFs under `doc/` (MuJoCo, Gazebo, real robot).

**Not included** — by design:

- **No trained policies** (`*.pt`, `*.pth`, `*.ckpt`, `*.onnx`,
  `*.jit`). Train them yourself, or fetch from LimX's internal
  artifact store / a GitHub Release.
- **No training logs, TensorBoard events, or Weights & Biases runs.**
  `logs/`, `wandb/`, `events.out.tfevents.*` are `.gitignore`'d and
  CI-blocked.
- **No test suite yet.** CI covers `python -m py_compile`, `ruff`,
  forbidden-artifact scans, and license scans only. Adding a smoke
  training-step check on a headless GPU worker is tracked as
  follow-up work.
- **No Isaac Sim redistribution.** You must obtain NVIDIA Isaac Sim
  5.1 independently and accept the NVIDIA proprietary EULA before
  installing this stack. Nothing here grants an Isaac Sim license.
- **No GPU / driver bundling.** A CUDA-capable GPU (≥ 12 GB VRAM
  recommended) is required to run 4096-env training. This repo does
  not ship drivers, CUDA, or PyTorch wheels.
- **No SDK binaries, firmware, calibration values, customer
  configuration, or vendor CAD.**

For deployment code (real-robot bring-up, ROS drivers, MuJoCo /
Gazebo integration), see the sibling repositories referenced in
[MuJoCo simulation and real-hardware deployment](#mujoco-simulation-and-real-hardware-deployment)
and
[Gazebo simulation and real-hardware deployment](#gazebo-simulation-and-real-hardware-deployment)
below.

## Repository layout

```
.
├── exts/bipedal_locomotion/   # Isaac Lab extension: env / asset / MDP / robot cfg
├── rsl_rl/                    # vendored rsl_rl fork (PPO + on-policy runner)
├── scripts/rsl_rl/            # training / play entry points (train.py / play.py / cli_args.py)
└── logs/                      # training logs and model weights
```

## Requirements

- **Isaac Sim 5.1** + **Isaac Lab 2.3.1**
- Python 3.10
- GPU (≥ 12 GB VRAM recommended for 4096-env training)

## Installation

```bash
# 1. Clone the repository
git clone <repo-url> tron1_rl_lab
cd tron1_rl_lab

# 2. Editable install of the extension and the vendored rsl_rl
pip install -e exts/bipedal_locomotion
pip install -e rsl_rl
```

## Training in Isaac Sim

Task IDs are registered in
[exts/bipedal_locomotion/bipedal_locomotion/tasks/locomotion/robots/__init__.py](exts/bipedal_locomotion/bipedal_locomotion/tasks/locomotion/robots/__init__.py).

### 1. Training a model

```bash
# === Solefoot (SF) ===
python scripts/rsl_rl/train.py --task Isaac-Limx-SF-TRON2A-Blind-Flat-v0 --num_envs 4096 --headless

# === Wheelfoot (WF) ===
python scripts/rsl_rl/train.py --task Isaac-Limx-WF-TRON2A-Blind-Flat-v0 --num_envs 4096 --headless

# === Dual-arm Solefoot (DASF_TRON2A) ===
python scripts/rsl_rl/train.py --task Isaac-Limx-DASF-TRON2A-Blind-Flat-v0 --num_envs 4096 --headless
```

*Common options:*
- `--checkpoint_path <path>`: resume from a specific `.pt` checkpoint.
- `--video`: enable video recording.
- `--max_iterations N`: override the maximum number of iterations.

Log path: `logs/rsl_rl/<experiment_name>/<timestamp>_<run_name>/`

### 2. Running inference (play)

Use the task ID with the `-Play-v0` suffix. The play cfg uses fewer
envs, disables domain randomization, and simplifies the terrain.

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

*Note:* by default the latest checkpoint is loaded; pass
`--checkpoint_path` to select a specific one.

### 3. Resuming a training run

`--resume True` must be passed explicitly for a checkpoint to be
loaded.

```bash
# Option A: point directly at a .pt file (recommended)
python scripts/rsl_rl/train.py --task Isaac-Limx-SF-TRON2A-Blind-Flat-v0 --resume True --checkpoint_path <path_to_model>

# Option B: look up a run by name
python scripts/rsl_rl/train.py --task Isaac-Limx-SF-TRON2A-Blind-Flat-v0 --resume True --load_run <run_name>

# Resume DASF_TRON2A
python scripts/rsl_rl/train.py \
  --task Isaac-Limx-DASF-TRON2A-Blind-Flat-v0 \
  --resume True \
  --checkpoint_path <path_to_model.pt>
```

## Robot morphology

| Morphology | Structure | Policy actions | Task ID prefix |
|---|---|---:|---|
| SF_TRON2A | Biped with sole feet (ankle pitch) | 10 | `Isaac-Limx-SF-TRON2A-...` |
| WF_TRON2A | Biped with wheel feet | 10 | `Isaac-Limx-WF-TRON2A-...` |
| DASF_TRON2A | SF lower body + two arms + head; 26 movable joints | 20 | `Isaac-Limx-DASF-TRON2A-...` |

- [DASF_TRON2A task details](exts/bipedal_locomotion/bipedal_locomotion/tasks/locomotion/cfg/DASF_TRON2A/README.md)

## Architecture overview

The project is organized into three main parts:

1. **`exts/bipedal_locomotion/`** — Isaac Lab extension. Contains
   env / asset / MDP / robot cfg.
2. **`rsl_rl/`** — vendored fork. `scripts/rsl_rl/train.py` prefers
   the algorithm library from this path.
3. **`scripts/rsl_rl/`** — entry-point scripts for training and
   inference.

### Task wiring flow

Common task wiring:

1. **Gym registration**: in `tasks/locomotion/robots/__init__.py`,
   the environment configuration and PPO configuration are bound to
   the task ID.
2. **Env cfg**: SF/WF use `tasks/locomotion/robots/limx_solefoot_tron2a_env_cfg.py`
   and `tasks/locomotion/robots/limx_wheelfoot_tron2a_env_cfg.py`
   respectively; DASF_TRON2A is assembled by
   `tasks/locomotion/robots/limx_dasf_tron2a_env_cfg.py`.
3. **Asset cfg**: SF/WF use `assets/config/solefoot_tron2a_cfg.py` /
   `assets/config/wheelfoot_tron2a_cfg.py`; DASF_TRON2A uses
   `assets/config/dasf_tron2a_cfg.py` for its independent USD and
   actuator parameters.
4. **DASF_TRON2A MDP**: scene, observation, event, curriculum, and
   reward implementations live under `tasks/locomotion/cfg/DASF_TRON2A/`.
5. **DASF_TRON2A agent**:
   `tasks/locomotion/agents/dasf_rsl_rl_ppo_cfg.py` selects
   `NormalizedPPO`, a history encoder, and independent actor/critic
   observation normalization.

## MuJoCo simulation and real-hardware deployment

- [MuJoCo simulation repository](https://github.com/example/tron1-mujoco-sim)
- [Python real-hardware deployment code](https://github.com/example/tron1-deploy-python)

### MuJoCo deployment result (SF / WF / DASF_TRON2A)

<p align="center">
  <img src="doc/mujoco_sf.gif" alt="MuJoCo SF" width="48%" />
  <img src="doc/mujoco_wf.gif" alt="MuJoCo WF" width="48%" />
</p>

<p align="center">
  <img src="doc/mujoco_dasf.GIF" alt="MuJoCo DASF_TRON2A" width="48%" />
</p>

- If the previews above do not render, download them directly:
  - [mujoco_sf.gif](doc/mujoco_sf.gif)
  - [mujoco_wf.gif](doc/mujoco_wf.gif)
  - [mujoco_dasf.GIF](doc/mujoco_dasf.GIF)

## Gazebo simulation and real-hardware deployment

- [Gazebo simulation repository](https://github.com/example/tron1-gazebo-sim)
- [ROS real-hardware deployment code](https://github.com/example/tron1-deploy-cpp)

### Gazebo deployment result (SF / WF)

<p align="center">
  <img src="doc/gazebo_sf.gif" alt="Gazebo SF" width="48%" />
  <img src="doc/gazebo_wf.gif" alt="Gazebo WF" width="48%" />
</p>

- If the previews above do not render, download them directly:
  - [gazebo_sf.gif](doc/gazebo_sf.gif)
  - [gazebo_wf.gif](doc/gazebo_wf.gif)

## Real-hardware deployment results (SF / WF / DASF_TRON2A, office scene)

<p align="center">
  <img src="doc/real_wf.GIF" alt="TRON2A WF real-hardware deployment" width="48%" />
  <img src="doc/real_sf.GIF" alt="TRON2A SF real-hardware deployment" width="48%" />
</p>

<p align="center">
  <img src="doc/real_dasf.GIF" alt="DASF_TRON2A real-hardware deployment" width="48%" />
</p>

## Real-hardware operating notes (strongly recommended)

Follow this fixed start-up and landing sequence to avoid impact
transients when switching policies:

1. **Suspend the robot** so that neither foot is loaded; check joint
   state, e-stop, and communication.
2. **Enter IK mode first** and confirm inverse-kinematics control is
   stable and the pose matches what you commanded.
3. **Slowly lower the robot to the ground**, watching for smooth
   contact and any abnormal shaking.
4. **Only then switch to the walk policy**, verifying at low speed
   and small stride before ramping up.

If anything abnormal happens (sudden shaking, pose divergence, hard
impact on landing), trigger the emergency stop immediately, return
to the suspended state, and re-check.

## Verification

The commands below match what CI runs (see
[`.github/workflows/ci.yml`](.github/workflows/ci.yml)); running them
locally before opening a PR saves review round-trips.

```bash
# 1. Byte-compile every first-party Python file.
python -m py_compile $(git ls-files '*.py')

# 2. Lint (first-party subtrees; the vendored rsl_rl fork is not
#    style-gated).
pip install ruff
ruff check --select F exts scripts

# 3. Editable-install dry run. Isaac Sim / Isaac Lab are not on
#    PyPI, so the transitive resolution may fail; the goal is to
#    validate setup.py / pyproject.toml metadata.
pip install --dry-run -e exts/bipedal_locomotion
pip install --dry-run -e rsl_rl

# 4. Optional import smoke on a machine WITH Isaac Sim / Isaac Lab:
python -c "import bipedal_locomotion; print(bipedal_locomotion.__file__)"

# 5. Ensure no training artifacts / SDK binaries are staged.
git ls-files | grep -iE \
  '(^|/)logs/|(^|/)wandb/|\.pt$|\.pth$|\.ckpt$|\.onnx$|events\.out\.tfevents\.' \
  && echo "!! training artifacts staged" && exit 1 || echo "ok"
```

On a machine with Isaac Sim 5.1 / Isaac Lab 2.3.1 installed, a short
end-to-end smoke run is:

```bash
python scripts/rsl_rl/train.py --task Isaac-Limx-SF-TRON2A-Blind-Flat-v0 \
  --num_envs 16 --headless --max_iterations 2
```

## Reference

- [Isaac Lab](https://github.com/isaac-sim/IsaacLab)
- [RSL-RL](https://github.com/leggedrobotics/rsl_rl) — upstream of
  the vendored fork under [`rsl_rl/`](rsl_rl).

## Cite & support

If you use this training stack in academic or public work, please
cite the repository:

```
@misc{limx_tron2_rl_lab_2026,
  title  = {tron2_rl_lab: RL training stack for the LimX TRON2A bipedal robot},
  author = {LimX Dynamics},
  year   = {2026},
  howpublished = {\url{https://github.com/limx-tron2/tron2_rl_lab}}
}
```

- **Bug reports / feature requests:** [GitHub Issues](https://github.com/limx-tron2/tron2_rl_lab/issues).
- **Questions / integration help:** [GitHub Discussions](https://github.com/limx-tron2/tron2_rl_lab/discussions).
- **Security reports:** email `contact@limxdynamics.com`; see
  [`SECURITY.md`](SECURITY.md).
- **Hardware / real-robot safety incidents:** email
  `contact@limxdynamics.com` with subject prefix
  `[tron2_rl_lab hardware]`. Do not open a public issue.
- **Company / commercial contact:** <https://www.limxdynamics.com>.
