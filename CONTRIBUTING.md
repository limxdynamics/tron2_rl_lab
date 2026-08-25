# Contributing to `tron2_rl_lab`

Thanks for helping improve the LimX TRON2A RL training stack. This
repository holds an Isaac Lab extension (`exts/bipedal_locomotion/`),
a vendored `rsl_rl/` fork, and Python entry scripts under
`scripts/rsl_rl/`. The guidelines below aim to keep the training stack
reproducible, keep the vendored fork auditable, and keep training
artifacts (checkpoints, logs, wandb runs) out of the repository.

## Table of contents

- [Ways to contribute](#ways-to-contribute)
- [Development setup](#development-setup)
- [Repository layout](#repository-layout)
- [Vendored `rsl_rl` update policy](#vendored-rsl_rl-update-policy)
- [Adding a new environment or robot variant](#adding-a-new-environment-or-robot-variant)
- [Reward / termination changes (safety-adjacent)](#reward--termination-changes-safety-adjacent)
- [Do not commit training artifacts](#do-not-commit-training-artifacts)
- [Assets (STL / USD / docs media)](#assets-stl--usd--docs-media)
- [Verification before opening a PR](#verification-before-opening-a-pr)
- [Commit messages](#commit-messages)
- [Pull request checklist](#pull-request-checklist)
- [Sign-off (DCO)](#sign-off-dco)
- [Code of conduct](#code-of-conduct)

## Ways to contribute

- Bug reports for env / MDP / actuator / robot cfg inconsistencies.
- New task registrations (Gym IDs) under
  `exts/bipedal_locomotion/bipedal_locomotion/tasks/locomotion/robots/`.
- Reward, termination, curriculum, and observation improvements — see
  [safety-adjacent section](#reward--termination-changes-safety-adjacent).
- Documentation, verification snippets, English translation of
  `README.md`.
- Vendored `rsl_rl` upstream sync PRs following the policy below.

We do **not** accept:

- Trained checkpoints (`*.pt`, `*.pth`, `*.ckpt`), ONNX / JIT policies
  (`*.onnx`), or any binary release artifact.
- Training logs (`logs/`, TensorBoard `events.out.tfevents.*`), Weights
  & Biases runs (`wandb/`, `.wandb/`), or video captures under
  `videos/` / `recordings/`.
- SDK binaries (`.so`, `.dll`, `.dylib`, `.lib`) or wheels.
- Vendor CAD, calibration values, firmware, or customer-specific
  configuration.
- Real-robot recordings that show identifiable individuals, office
  interiors that disclose site information, or non-public products.

## Development setup

Prerequisites:

- **NVIDIA Isaac Sim 5.1** and **Isaac Lab 2.3.1** (see the Isaac Lab
  install guide for the supported Python + driver matrix).
- Python 3.10.
- A CUDA-capable GPU (≥ 12 GB VRAM recommended for 4096-env training).

```bash
git clone https://github.com/limx-tron2/tron2_rl_lab.git
cd tron2_rl_lab

# Editable install of the extension and the vendored rsl_rl fork.
# Do this inside the Python environment that has Isaac Sim / Isaac Lab
# on the import path.
pip install -e exts/bipedal_locomotion
pip install -e rsl_rl
```

Verify the setup:

```bash
# Byte-compile every first-party Python file.
python -m py_compile $(git ls-files '*.py')

# Import the extension package (does not require Isaac Sim to import
# top-level; sub-modules that touch Isaac Sim will fail on machines
# without it — that is expected and is checked by CI only up to
# py_compile).
python -c "import bipedal_locomotion; print(bipedal_locomotion.__file__)"
```

Optional smoke test on a machine with Isaac Sim:

```bash
python scripts/rsl_rl/train.py --task Isaac-Limx-SF-TRON2A-Blind-Flat-v0 \
  --num_envs 16 --headless --max_iterations 2

python scripts/rsl_rl/train.py --task Isaac-Limx-DASF-TRON2A-Blind-Flat-v0 \
  --num_envs 1 --headless --max_iterations 1
```

## Repository layout

```
.
├── exts/bipedal_locomotion/       # Isaac Lab extension
│   └── bipedal_locomotion/
│       ├── actuators/             # Actuator models
│       ├── assets/                # Robot cfg + bundled USD / STL
│       ├── tasks/                 # Env cfg + Gym registrations
│       └── utils/                 # Shared helpers
├── rsl_rl/                        # Vendored fork of leggedrobotics/rsl_rl
├── scripts/rsl_rl/                # train.py / play.py entry scripts
├── doc/                           # Simulator + real-robot GIFs
├── LICENSE                        # Apache-2.0
├── NOTICE                         # Attribution
├── THIRD_PARTY_NOTICES.md         # Per-component provenance
├── SECURITY.md
├── CONTRIBUTING.md                # this file
└── CHANGELOG.md
```

- `logs/`, `outputs/`, `runs/`, `wandb/`, `videos/`, `recordings/` are
  runtime output directories; they must not appear in git. CI enforces
  this — see [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Vendored `rsl_rl` update policy

`rsl_rl/` is a **vendored fork** of
[leggedrobotics/rsl_rl](https://github.com/leggedrobotics/rsl_rl)
(BSD-3-Clause). It is edited in-tree and imported ahead of any
pip-installed `rsl_rl`.

Rules:

1. **Never silently rebase.** Every update to `rsl_rl/` lands in an
   explicit PR titled `chore(rsl_rl): sync <upstream-ref>` or
   `fix(rsl_rl): <summary>`.
2. **Record the diff.** Maintain `rsl_rl/CHANGES_VS_UPSTREAM.md` (to
   be created on the first sync PR after the initial public release).
   Every sync PR appends a section:
   - Upstream ref (commit SHA or tag) before the sync.
   - Upstream ref after the sync.
   - Summary of LimX-side diff carried across the sync.
   - Any files where LimX-side edits were dropped or resolved.
3. **Preserve BSD-3-Clause attribution.** Every source file must keep
   its `Copyright ... ETH Zurich, NVIDIA CORPORATION` header and the
   SPDX identifier. Do not delete or overwrite these headers.
4. **Do not vendor a rebased branch as a merge commit.** Use a
   flat replay (`git format-patch` / cherry-pick) so the PR diff is
   reviewable.
5. **Third-party notices.** Update `THIRD_PARTY_NOTICES.md` §2 if the
   upstream URL, license, or fork commit changes.
6. **License-text directory.** Do not add new files to
   `rsl_rl/licenses/dependencies/` without also updating
   `THIRD_PARTY_NOTICES.md` §3 and (if the text is copyleft) the CI
   GPL whitelist entry.

Bug fixes and reward-shape / config changes that are **specific to
TRON2A training** belong in `exts/bipedal_locomotion/`, not in
`rsl_rl/`, unless the underlying algorithm is genuinely broken.

DASF_TRON2A intentionally carries two RSL-RL extensions:
`rsl_rl/rsl_rl/modules/normalized_actor_critic.py` and
`rsl_rl/rsl_rl/algorithm/normalized_ppo.py`. The shared runner selects
them only when the DASF agent requests empirical normalization and
`class_name="NormalizedPPO"`. Changes to these files or to that
selection logic must preserve the original ActorCritic/PPO path used
by SF_TRON2A and WF_TRON2A and must update
`rsl_rl/CHANGES_VS_UPSTREAM.md`.

## Adding a new environment or robot variant

Follow the existing Gym-registration pattern:

1. **Env cfg.** Add
   `exts/bipedal_locomotion/bipedal_locomotion/tasks/locomotion/robots/<name>_env_cfg.py`.
   Extend the shared base cfg
   (`exts/bipedal_locomotion/.../limx_base_env_cfg.py`) instead of
   duplicating reward / termination logic.
2. **Asset cfg.** Add
   `exts/bipedal_locomotion/bipedal_locomotion/assets/config/<name>_cfg.py`
   pointing at a USD path under `bipedal_locomotion/assets/usd/<VARIANT>/`.
3. **PPO / runner cfg.** Add or reuse an
   `agents/rsl_rl_ppo_cfg.py` entry for the task.
4. **Gym registration.** Register both a training task (`-v0`) and a
   play task (`-Play-v0`) in
   `tasks/locomotion/robots/__init__.py`.
5. **README entry.** Add a row to the "机器人形态 / robot variants"
   table with the new task-ID prefix.
6. **Third-party notices.** If the new variant ships bundled USD /
   STL that is not already covered, add a row to
   `THIRD_PARTY_NOTICES.md` §5.
7. **CI matrix.** Add the new task ID to the `py_compile` and
   Gym-registration smoke checks in
   `.github/workflows/ci.yml` if a per-task check is added.

DASF_TRON2A is an intentional exception to step 1: because its
20-action whole-body policy, privileged observations, randomization,
and reward topology differ from the 10-action SF/WF tasks, it owns
independent files under `tasks/locomotion/cfg/DASF_TRON2A/` instead of
inheriting the SF/WF environment. Its asset, env wiring, and agent
entry points are `assets/config/dasf_tron2a_cfg.py`,
`tasks/locomotion/robots/limx_dasf_tron2a_env_cfg.py`, and
`tasks/locomotion/agents/dasf_rsl_rl_ppo_cfg.py`. Do not move DASF
reward or randomization terms into shared SF/WF modules unless the
behavior is genuinely common to all three morphologies.

## Reward / termination changes (safety-adjacent)

Files under
`exts/bipedal_locomotion/.../limx_base_env_cfg.py:431-552` and the
sibling `mdp/` modules define reward, termination, action, and event
managers that shape any resulting policy. A policy trained here may
later be deployed on real hardware — see
`README.md:142-151` (吊起 → IK → 落地 → walk) for the on-hardware
bring-up sequence.

Every PR that touches these modules must:

- State the training and play task IDs whose behaviour changes.
- Show a `play.py` run of the affected task, or a plot of the
  reward-term curve, demonstrating the intended effect.
- Confirm the change does not remove or weaken a termination that
  guards the hoist / IK / landing sequence in `README.md:142-151`.
- Add a `CHANGELOG.md` entry under `## [Unreleased]`.

For DASF_TRON2A, this policy also applies to
`tasks/locomotion/cfg/DASF_TRON2A/{limx_base_env_cfg,mdp,rewards}.py`,
the normalized actor-critic/PPO path, and the conditional selection in
`rsl_rl/rsl_rl/runner/on_policy_runner.py`.

## Do not commit training artifacts

The following patterns are hard-blocked in `.gitignore` and
double-checked by CI:

```
logs/            outputs/        runs/           wandb/          .wandb/
videos/          recordings/     .tensorboard/
*.pt   *.pth   *.ckpt   *.onnx   *.jit
events.out.tfevents.*
```

If you need to share a trained policy for evaluation, use an external
storage location (Gradmotion, internal artifact store, or a release
tarball attached to a GitHub Release) and link to it from the PR
description or from `README.md`. **Never** commit the file itself.

## Assets (STL / USD / docs media)

- STL must be binary; do not commit ASCII STL.
- STL header bytes 0–79 and USD `customLayerData` / `comment` /
  `author` fields must not disclose internal paths, usernames, or
  serial numbers.
- GIFs under `doc/` must have metadata stripped and must not contain
  identifiable individuals, non-public products, or office locations
  that disclose site information.
- CI runs the header / metadata / EXIF scans on every PR.

## Verification before opening a PR

Run all of the following and paste the summary into the PR description:

```bash
# 1. Byte-compile every first-party Python file.
python -m py_compile $(git ls-files '*.py')

# 2. Editable install dry run (does not require Isaac Sim).
pip install --dry-run -e exts/bipedal_locomotion
pip install --dry-run -e rsl_rl

# 3. Lint (optional but recommended).
pip install ruff
ruff check exts scripts

# 4. Ensure no training artifacts have snuck in.
git ls-files | grep -iE '(^|/)logs/|^wandb/|\.pt$|\.pth$|\.ckpt$|\.onnx$|events\.out\.tfevents\.' \
  && echo "!! training artifacts staged" && exit 1 || echo "ok"

# 5. Ensure no unresolved license / TODO markers in the top-level docs.
grep -rniE 'proprietary|confidential|todo: license|unknown license' \
  README.md THIRD_PARTY_NOTICES.md CHANGELOG.md CONTRIBUTING.md SECURITY.md NOTICE || true
```

CI runs equivalent checks; local pre-checks save review round-trips.

## Commit messages

Follow Conventional Commits:

```
type(scope): short imperative summary

Longer explanation if needed.

Signed-off-by: Your Name <you@example.com>
```

`type` ∈ `feat | fix | docs | refactor | chore | ci | test | asset | rsl_rl`.
`scope` is typically a subsystem (`env`, `mdp`, `actuator`, `assets`,
`train`, `play`) or `meta` for repo-wide changes. Use the dedicated
`rsl_rl` type for any change under `rsl_rl/` — this makes upstream
sync history easy to filter.

## Pull request checklist

- [ ] `python -m py_compile` clean on every changed `.py`.
- [ ] No training artifacts staged (`*.pt`, `*.pth`, `*.ckpt`,
      `*.onnx`, `logs/`, `wandb/`, `events.out.tfevents.*`).
- [ ] If touching `rsl_rl/`, `rsl_rl/CHANGES_VS_UPSTREAM.md` is
      updated with the diff versus upstream.
- [ ] If adding a new task, both `-v0` and `-Play-v0` are registered.
- [ ] If touching DASF_TRON2A, its 20-action order and independent
  normalization/export path are verified, and SF/WF still resolve
  to the original ActorCritic/PPO implementation.
- [ ] If touching reward / termination, the PR body includes a play
      run or reward-curve evidence.
- [ ] `THIRD_PARTY_NOTICES.md` updated if any bundled asset or
      dependency changed.
- [ ] `CHANGELOG.md` has an entry under `## [Unreleased]`.
- [ ] DCO sign-off on every commit.

## Sign-off (DCO)

We use the [Developer Certificate of Origin](https://developercertificate.org/).
Every commit must be signed off:

```bash
git commit -s -m "your message"
```

Signing off certifies that you have the right to submit the change
under the repository's license.

## Code of conduct

Be respectful and constructive. Reports to
`contact@limxdynamics.com`.
