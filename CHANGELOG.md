# Changelog

All notable changes to `tron2_rl_lab` will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Open-source scaffolding: `NOTICE`, `THIRD_PARTY_NOTICES.md`,
  `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`.
- GitHub CI workflow (`.github/workflows/ci.yml`): Python lint
  (`ruff`), `python -m py_compile` on every first-party `.py`, deny-
  list scan for training artifacts (`logs/`, `*.pt`, `*.pth`,
  `*.ckpt`, `*.onnx`, `wandb/`, `.wandb/`, `events.out.tfevents.*`),
  EXIF sanity on `doc/*.gif`, and a GPL-text scan that fails with a
  pointer to `THIRD_PARTY_NOTICES.md` §3.
- Issue templates and PR template under `.github/`.
- `.github/CODEOWNERS` with placeholder teams (`maintainers`, `legal`,
  `rl`, `robotics`, `safety`).
- `README.md`: SPDX header, "License & attribution" links, "Scope /
  not included" section, "Verification" section, "Cite & support"
  section, and a note that English translation is planned.
- `DASF_TRON2A` full-body morphology with a sole-foot lower body, two
  arms, and a head. The task exposes 20 policy actions over 26 movable
  joints and registers training and Play task IDs.
- Independent DASF_TRON2A asset, environment, MDP, reward, and agent
  configurations, including whole-body gait and arm-swing rewards,
  encoder-bias/material/mass randomization, and speed-dependent
  posture tolerances.
- `EmpiricalNormalizedActorCritic` and `NormalizedPPO` for the
  DASF_TRON2A path, with separate actor/critic running normalizers and
  normalized JIT/ONNX policy export.

### Changed
- `.gitignore`: added an explicit deny-list for training artifacts
  (`logs/`, `outputs/`, `wandb/`, `.wandb/`, `*.pt`, `*.pth`,
  `*.ckpt`, `*.onnx`, `events.out.tfevents.*`, `.tensorboard/`) and
  standard Python cache dirs, on top of the existing rules. The
  existing rules (Omniverse, IDE, Isaac Sim packman, outputs
  globbing) are retained unchanged.
- Shared task registration, runner selection, and Play export now
  select the DASF_TRON2A-specific environment and normalization path
  only when its task/configuration requests them; SF/WF retain their
  existing behavior.

### Pending owner sign-off (blocks first public tag)

Every item below is currently `⚠ TO CONFIRM` in the scaffolding docs
and must be resolved before cutting the first public tag.

### Resolved (2026-07-16)
- **`LICENSE` filename (was British-spelled `LICENCE`).** Renamed
  `LICENCE` → `LICENSE` via `git mv` per owner decision 2026-07-16.
  All internal references in `README.md`, `README_zh-CN.md`,
  `CHANGELOG.md`, `CONTRIBUTING.md`, `NOTICE`, `THIRD_PARTY_NOTICES.md`,
  and `.github/CODEOWNERS` updated to match.
- **MIT declaration in `exts/bipedal_locomotion/setup.py:61`.** Changed
  from `license="MIT"` to `license="Apache-2.0"` per owner decision
  2026-07-16, aligning the extension with the top-level Apache-2.0
  LICENSE. THIRD_PARTY_NOTICES.md §1 will be updated separately by the
  RL lead + legal per the Isaac-Lab-derivation audit still pending
  below.

### Resolved (2026-07-14)
- **Isaac Lab boilerplate at `LICENSE:189-201`** — the copyright line
  now reads `Copyright 2024-2026 LimX Dynamics Technology Co., Ltd.`
  and is followed by an attribution paragraph pointing at the
  Isaac Lab upstream (`https://github.com/isaac-sim/IsaacLab`,
  Apache-2.0 + BSD-3-Clause) with a cross-reference to
  `THIRD_PARTY_NOTICES.md`. The rest of the Apache-2.0 boilerplate is
  untouched.
- **`rsl_rl/` fork diff versus upstream** — created
  [`rsl_rl/CHANGES_VS_UPSTREAM.md`](rsl_rl/CHANGES_VS_UPSTREAM.md).
  Fork base is `leggedrobotics/rsl_rl` **`v2.0.1`** (commit
  `73fd7c621bf63104a8a7eb0c168df16c0ee65908`). The file records the
  directory renames (`algorithms/` → `algorithm/`, `runners/` →
  `runner/`), files removed (`utils/`, `actor_critic_recurrent.py`,
  `normalizer.py`), the LimX-added `mlp_encoder.py`, and per-file diff
  sizes, plus a `diff -ru` reproduce recipe and an update policy. The
  DASF_TRON2A branch additionally adds `normalized_actor_critic.py`,
  `normalized_ppo.py`, and conditional runner selection; these deltas
  must remain listed when the fork-diff report is refreshed.
- **GPL text in `rsl_rl/licenses/dependencies/codespell-license.txt`**
  — classified as **dev-only** in a new
  [`rsl_rl/licenses/dependencies/README.md`](rsl_rl/licenses/dependencies/README.md).
  The GPL-2.0 text is retained verbatim as an audit-time NOTICE
  (`codespell` is a pre-commit spell checker; `rsl_rl` does not import
  or bundle it, so GPL terms do not propagate). CI's GPL-text scan
  allow-lists exactly this one file.

### Still pending owner sign-off (blocks first public tag)

- **Isaac-Lab-derived files audit.** Enumerate every file in
  `exts/bipedal_locomotion/` that is templated on or derived from
  Isaac Lab and add the required upstream attribution header, or
  rewrite (`THIRD_PARTY_NOTICES.md` §1). Owners: RL lead + legal.
- **Bundled STL / USD asset provenance.** 58 STL and 15 USD files
  under `exts/bipedal_locomotion/bipedal_locomotion/assets/usd/{WF,SF,DASF}_TRON2A/`
  need hardware / mechanical sign-off equivalent to what the sibling
  `robot-description` repository records in its `ASSETS.md`
  (`THIRD_PARTY_NOTICES.md` §5). Owners: hardware / mechanical lead.
- **"Office scene" real-robot media (`doc/real_sf.GIF`,
  `doc/real_wf.GIF`).** Content review + metadata strip
  (`THIRD_PARTY_NOTICES.md` §7). Owners: content / marketing lead +
  robotics lead.
- **English translation of `README.md`.** The current `README.md` is
  largely Chinese. Add an English translation, or split into
  `README.md` (English) + `README.zh-CN.md`. Owners: docs lead.
- **No test suite.** There is no automated test coverage today; CI
  currently covers `py_compile`, lint, and forbidden-artifact scans
  only. Adding a smoke test that runs one training step on a
  headless GPU worker is tracked as follow-up work. Owners:
  maintainers + RL lead.
- **Isaac Sim / GPU dependency.** Downstream users must independently
  obtain Isaac Sim 5.1 and accept the NVIDIA EULA — this repository
  does not redistribute it. `README.md` calls this out explicitly.
  Owners: maintainers.

## [0.1.0] — TBD

First public release. Contents (planned):

- Isaac Lab extension `exts/bipedal_locomotion/` providing env / MDP /
  actuator / robot cfg for TRON2A locomotion.
- Vendored fork `rsl_rl/` with PPO trainer and on-policy runner.
- Entry scripts `scripts/rsl_rl/{train,play}.py` including ONNX / JIT
  policy export.
- Bundled USD / STL assets for the SF_TRON2A, WF_TRON2A, and
  DASF_TRON2A variants.

[Unreleased]: https://github.com/limx-tron2/tron2_rl_lab/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/limx-tron2/tron2_rl_lab/releases/tag/v0.1.0
