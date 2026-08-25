# Third-Party Notices

`tron2_rl_lab` is the LimX Dynamics reinforcement-learning training stack
for the TRON2A bipedal robot on NVIDIA Isaac Sim / Isaac Lab.

First-party LimX code and assets in this repository are distributed
under the **Apache License, Version 2.0** (see the top-level `LICENSE`
file and [`NOTICE`](NOTICE)), except where a narrower license is
declared in a subdirectory's own `setup.py` or file header — see §1
and §2 below.

This file lists the third-party components, vendored forks, bundled
assets, and reference / doc media so downstream users can comply with
all applicable licenses and re-distribution terms.

> **Status:** items marked `⚠ TO CONFIRM` are pending sign-off from the
> OSPO / legal / hardware / RL / robotics / safety owners. Do not cut
> a public release while any `⚠ TO CONFIRM` entry remains.

---

## 1. `exts/bipedal_locomotion/` — Isaac Lab extension (LimX-authored)

- **Path:** `exts/bipedal_locomotion/`
- **Declared license:** **Apache-2.0**, self-declared at
  `exts/bipedal_locomotion/setup.py:61` (`license="Apache-2.0"`).
  ✅ resolved 2026-07-16 — was `MIT` before; changed per owner
  decision to align with the top-level `LICENSE`.
- **Isaac Lab derivation:** the extension is built against the Isaac
  Lab task / manager / env framework and reproduces Isaac-Lab-style
  configuration patterns (`ManagerBasedRLEnvCfg`, MDP term dataclasses,
  event / reward / termination managers, `RSL_RL*Cfg` shapes, etc.).
  Individual files may be templated on, or derived from, Isaac Lab
  examples. `⚠ TO CONFIRM` — an Isaac-Lab-derivation audit is
  required per file; every derived file must carry an Apache-2.0
  header attributing "The Isaac Lab Project Developers" alongside the
  LimX copyright, or be rewritten. Cross-reference to the top-level
  `LICENSE` attribution paragraph is in §4.

Owner action required (RL owner + legal):
1. Enumerate every file that is derived from Isaac Lab and add the
   required upstream attribution header.
2. Update this section from `⚠ TO CONFIRM` to a definitive per-file
   statement.

## 2. `rsl_rl/` — vendored fork of leggedrobotics/rsl_rl

- **Path:** `rsl_rl/`
- **Declared license:** **BSD-3-Clause**, per `rsl_rl/setup.py:1-2`:

  ```
  #  Copyright 2021 ETH Zurich, NVIDIA CORPORATION
  #  SPDX-License-Identifier: BSD-3-Clause
  ```

- **Upstream:** <https://github.com/leggedrobotics/rsl_rl>
- **Nature:** vendored fork (see `README.md:10`). The tree here is
  edited and shipped in-tree; `scripts/rsl_rl/*.py` imports the local
  copy in preference to any pip-installed `rsl_rl`.
- **Upstream tag / commit:** **`v2.0.1`** — commit
  `73fd7c621bf63104a8a7eb0c168df16c0ee65908` — as recorded in
  [`rsl_rl/CHANGES_VS_UPSTREAM.md`](rsl_rl/CHANGES_VS_UPSTREAM.md).
- **Diff versus upstream:** ✅ recorded in
  [`rsl_rl/CHANGES_VS_UPSTREAM.md`](rsl_rl/CHANGES_VS_UPSTREAM.md).
  Summary: directory renames (`algorithms/` → `algorithm/`, `runners/`
  → `runner/`); files removed (`utils/`, `actor_critic_recurrent.py`,
  `normalizer.py`); one file added by LimX (`mlp_encoder.py`); the
  `ppo.py` and `on_policy_runner.py` edits are the largest content
  changes. The DASF_TRON2A integration additionally adds
  `modules/normalized_actor_critic.py` and
  `algorithm/normalized_ppo.py`, and extends `on_policy_runner.py` to
  select those implementations only when requested by the DASF agent
  configuration. These local deltas must be included the next time
  `CHANGES_VS_UPSTREAM.md` is regenerated.
- **Attribution requirement (BSD-3-Clause):** the top-level `NOTICE`
  file, this section, and each source file's header must retain the
  ETH Zurich / NVIDIA copyright notice, the license text, and the
  no-endorsement clause.
- **Update policy:** see [`CONTRIBUTING.md`](CONTRIBUTING.md#vendored-rsl_rl-update-policy)
  and the "Update policy" section of `CHANGES_VS_UPSTREAM.md`. Do
  **not** silently rebase; every update lands as an explicit PR that
  refreshes `CHANGES_VS_UPSTREAM.md`.

## 3. `rsl_rl/licenses/dependencies/` — dev-tooling license texts

The `rsl_rl/licenses/dependencies/` directory carries the license text
of upstream `rsl_rl` development / lint tooling. These are **not
executable dependencies** of the training runtime; they are dev tools
invoked at commit time. A per-file classification with an update
procedure lives at
[`rsl_rl/licenses/dependencies/README.md`](rsl_rl/licenses/dependencies/README.md).

| File | Tool | License text kind | Status |
|------|------|-------------------|--------|
| `black-license.txt` | Black formatter | MIT | ✅ compatible |
| `codespell-license.txt` | codespell | **GPL-2.0** text | ✅ classified as **dev-only** — see below |
| `flake8-license.txt` | flake8 | MIT | ✅ compatible |
| `isort-license.txt` | isort | MIT | ✅ compatible |
| `numpy_license.txt` | NumPy | BSD-3-Clause | ✅ compatible (runtime) |
| `onnx-license.txt` | ONNX | Apache-2.0 | ✅ compatible (runtime) |
| `pre-commit-hooks-license.txt` | pre-commit-hooks | MIT | ✅ compatible |
| `pre-commit-license.txt` | pre-commit | MIT | ✅ compatible |
| `pyright-license.txt` | Pyright | MIT | ✅ compatible |
| `pyupgrade-license.txt` | pyupgrade | MIT | ✅ compatible |
| `torch_license.txt` | PyTorch | BSD-style | ✅ compatible (runtime) |

**`codespell-license.txt` (GPL-2.0) — classified dev-only (2026-07-14).**
`codespell` is a pre-commit spell checker; nothing under `rsl_rl/` or
`exts/bipedal_locomotion/` imports it, and no release artifact re-ships
it. Its GPL-2.0 terms therefore do not propagate to `rsl_rl`
(BSD-3-Clause) or to the outer `tron2_rl_lab` repository (Apache-2.0).
The GPL-2.0 text is retained here only as an audit-time NOTICE.

CI (`.github/workflows/ci.yml`) fails on any newly introduced GPL text
outside the single allow-list entry
`rsl_rl/licenses/dependencies/codespell-license.txt`, with a message
pointing back to this section and to
`rsl_rl/licenses/dependencies/README.md`.

## 4. Isaac Lab — attribution in the top-level LICENSE

- **Path:** top-level `LICENSE`, lines `189-201`.
- **Status:** ✅ resolved (2026-07-14). The copyright line now reads:

  ```
  Copyright 2024-2026 LimX Dynamics Technology Co., Ltd.
  ```

  and is followed by an attribution paragraph pointing at Isaac Lab
  (<https://github.com/isaac-sim/IsaacLab>, distributed upstream under
  a combination of Apache-2.0 and BSD-3-Clause) with a cross-reference
  to this file. The rest of the Apache-2.0 boilerplate is untouched.
- **Follow-up (still `⚠ TO CONFIRM` — tracked in §1):** the per-file
  Isaac-Lab-derivation audit inside `exts/bipedal_locomotion/` is
  independent of this LICENSE-level fix and remains pending.

## 5. Bundled robot assets — STL / USD

The following LimX-authored robot assets are shipped in-tree so the
extension is self-contained (no external asset repository required at
`pip install` time). Provenance is asserted first-party; re-distribution
under Apache-2.0 is `⚠ TO CONFIRM` pending a hardware / mechanical
owner sign-off equivalent to what the sibling `robot-description` repo
records in its `ASSETS.md`.

| Variant path | STL meshes | USD assets |
|--------------|:----------:|:----------:|
| `exts/bipedal_locomotion/bipedal_locomotion/assets/usd/WF_TRON2A/meshes/*.STL` | 11 | — |
| `exts/bipedal_locomotion/bipedal_locomotion/assets/usd/WF_TRON2A/usd/*.usd` (incl. `configuration/`) | — | 5 |
| `exts/bipedal_locomotion/bipedal_locomotion/assets/usd/SF_TRON2A/meshes/*.STL` | 11 | — |
| `exts/bipedal_locomotion/bipedal_locomotion/assets/usd/SF_TRON2A/usd/*.usd` (incl. `configuration/`) | — | 5 |
| `exts/bipedal_locomotion/bipedal_locomotion/assets/usd/DASF_TRON2A/meshes/*.STL` | 36 | — |
| `exts/bipedal_locomotion/bipedal_locomotion/assets/usd/DASF_TRON2A/usd/*.usd` (incl. `configuration/`) | — | 5 |
| **Total** | **58** | **15** |

The DASF_TRON2A asset directory also contains two URDF files, two
Xacro files, and one MuJoCo XML model. They are model sources and
companion representations for the same morphology and are subject to
the same first-party provenance and metadata review as the STL/USD
files above.

> The open-source review that seeded this scaffolding referenced the
> lower figure of "10 STL / USD assets" because it was performed
> against a sparse checkout. The counts above reflect the full working
> tree.

Owner sign-off required (hardware / mechanical lead):

1. Confirm every STL / USD in the table above is LimX-authored (no
   vendor CAD embedded, no third-party USD payload composed in via
   `references` / `payload`).
2. Confirm STL header bytes 0–79 and USD `customLayerData` /
   `comment` / `author` fields do not disclose internal paths,
   usernames, serial numbers, or office locations.
3. Verification commands:

   ```bash
   # STL header scan
   find exts -iname '*.STL' | while read f; do
     head -c 80 "$f" | strings | grep -iE '(users|home|desktop|\.step|\.sldprt|serial|internal)' \
       && echo "  <- in $f"
   done

   # USD metadata scan (ASCII USDs only; skip .usdc)
   grep -rE '(customLayerData|comment = "|"author"|"owner"|"copyright")' \
     exts/bipedal_locomotion/bipedal_locomotion/assets/usd/**/*.usd 2>/dev/null || true
   ```

4. Cross-reference the sibling `robot-description` repository — the
  `WF_TRON2A`, `SF_TRON2A`, and `DASF_TRON2A` variants may ship
  same-named meshes or model sources there. If the files here are
  copies of the same LimX-owned exports, note that in the sign-off so
  both repositories share one provenance decision.

## 6. Isaac Sim / Isaac Lab / PyTorch / other runtime dependencies

The following are **runtime dependencies only** — they are neither
vendored nor packaged in this repository, but downstream users need
them at install / run time.

| Tool | Purpose | License | Where obtained |
|------|---------|---------|----------------|
| NVIDIA Isaac Sim (5.1) | Physics + rendering runtime | NVIDIA proprietary EULA | <https://developer.nvidia.com/isaac-sim> |
| NVIDIA Isaac Lab (2.3.1) | Task / manager / env framework | BSD-3-Clause | <https://github.com/isaac-sim/IsaacLab> |
| PyTorch (`torch`, `torchvision`) | Tensor + autograd runtime | BSD-style | <https://pytorch.org> |
| NumPy | Numerical arrays | BSD-3-Clause | PyPI |
| Gymnasium / gym | RL env API | MIT | PyPI |
| tensorboard | Training logs | Apache-2.0 | PyPI |
| ONNX / onnxruntime | Policy export (`scripts/rsl_rl/play.py:108-118`) | Apache-2.0 / MIT | PyPI |
| Weights & Biases (`wandb`) | Optional experiment tracking | MIT | PyPI |

None of the above are bundled here. Users must obtain and accept the
NVIDIA Isaac Sim EULA independently before installing this training
stack; nothing in this repository grants a license to Isaac Sim.

## 7. Documentation media

`doc/` contains simulator recordings and real-robot recordings that
appear in `README.md:105-140`:

| Path | Kind | Provenance | Content review |
|------|------|------------|----------------|
| `doc/mujoco_sf.gif` | MuJoCo playback | LimX-generated | ✅ synthetic — no people / site |
| `doc/mujoco_wf.gif` | MuJoCo playback | LimX-generated | ✅ synthetic — no people / site |
| `doc/gazebo_sf.gif` | Gazebo playback | LimX-generated | ✅ synthetic — no people / site |
| `doc/gazebo_wf.gif` | Gazebo playback | LimX-generated | ✅ synthetic — no people / site |
| `doc/real_sf.GIF` | Real-robot recording (office scene) | LimX lab footage | `⚠ TO CONFIRM` |
| `doc/real_wf.GIF` | Real-robot recording (office scene) | LimX lab footage | `⚠ TO CONFIRM` |

`README.md:135-139` calls the real-robot clips out as "办公室场景"
(office scene) footage. Owner review required:

- No identifiable individuals (faces, badges, name plates) are visible.
- No customer or non-public product is visible.
- No whiteboard / monitor / screen discloses internal information.
- EXIF / GIF metadata carries no author / serial / GPS data:

  ```bash
  exiftool doc/*.gif doc/*.GIF \
    | grep -iE '(gps|serial|make|model|software|author|artist|copyright)'
  ```

Owner: content / marketing lead + robotics lead.

## 8. What this repository does **not** include

- No trained policy weights (`.pt`, `.pth`, `.ckpt`, `.onnx`).
- No training logs, TensorBoard events, or Weights & Biases runs.
- No customer-specific configuration or deployment secrets.
- No SDK binaries (`.so`, `.dll`, `.dylib`, `.lib`) or firmware.
- No calibration values.

For deployment code, see the sibling repositories referenced in
`README.md`.

## 9. Update procedure

Whenever a source file, USD / STL asset, image, or upstream reference
is added or changed:

1. Update the corresponding row in this file.
2. If a new third-party dependency is vendored or bundled, add its
   attribution here and to `NOTICE`.
3. If `rsl_rl/` is updated, refresh `rsl_rl/CHANGES_VS_UPSTREAM.md`
   in the same PR (§2, and see `CONTRIBUTING.md`).
4. If a change touches an `⚠ TO CONFIRM` row, block the merge on
   written sign-off from the responsible owner.
