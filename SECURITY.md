# Security Policy

## Scope

`tron2_rl_lab` ships **reinforcement-learning training and playback
code** for the LimX TRON2A bipedal robot on NVIDIA Isaac Sim / Isaac
Lab: an Isaac Lab extension (`exts/bipedal_locomotion/`), a vendored
`rsl_rl/` PPO trainer, and Python entry scripts under `scripts/rsl_rl/`
plus bundled STL / USD robot assets for the SF_TRON2A, WF_TRON2A, and
DASF_TRON2A morphologies. DASF_TRON2A adds a 20-action full-body policy
over a sole-foot lower body, two arms, and a head.

It contains **no network services, no SDK binaries, no shipped model
weights, and no calibration secrets**. Its security surface is
therefore limited, but not zero:

- **Safety-adjacent code paths.** The reward, termination, and action
  configuration in
  `exts/bipedal_locomotion/.../limx_base_env_cfg.py:431-552` and
  neighbouring MDP modules shapes policies that may later be
  deployed on real hardware. A change here that trains an unsafe gait
  is a safety issue even though it is not a classical CVE.
- **DASF_TRON2A whole-body control.** Its independent environment and
  MDP modules under `tasks/locomotion/cfg/DASF_TRON2A/` additionally
  shape arm swing, foot/arm coordination, body posture, encoder bias,
  material properties, and mass/inertia randomization. Incorrect joint
  order or reward/randomization changes can affect both balance and arm
  motion on hardware.
- **Policy export.** `scripts/rsl_rl/play.py:108-118` exports policies
  to ONNX / JIT. A tampered export path could ship an untrusted
  policy to a real robot; treat export code as a trust boundary.
- **Normalized DASF policy export.** DASF_TRON2A exports the actor with
  its running observation normalizer and exports the history encoder
  separately. Dropping, replacing, or applying the wrong normalizer
  can produce unsafe actions even when the model weights are valid.
- **Malicious asset payload.** STL / USD files are parsed by third-
  party libraries (Isaac Sim, USD, `trimesh`, etc.). A crafted asset
  in a PR could exploit a downstream parser. Assets are reviewed on
  every PR (see `CONTRIBUTING.md`).
- **Metadata disclosure.** STL headers, USD `customLayerData`, GIF
  metadata, and Python file headers must not leak internal paths,
  usernames, serial numbers, or office locations.
- **Vendored `rsl_rl/` supply chain.** Any silent rebase of the
  vendored fork could pull in unaudited upstream changes; the
  vendored-fork policy in `CONTRIBUTING.md` requires an explicit,
  auditable update trail.

**Runtime / hardware safety** — the physical procedure for bringing a
policy onto a real robot (hoist the robot, verify IK, lower to the
ground, then switch to `walk`; see `README.md:142-151`) is a product-
safety concern, not a software CVE. Report hardware / operational
safety issues to LimX product support, not through this channel.

## Supported versions

Only the tip of the `main` branch and the most recent tagged release
receive security fixes. Older tags are provided as-is.

| Version    | Supported |
|------------|-----------|
| `main`     | ✅        |
| Latest tag | ✅        |
| Older tags | ❌        |

## Reporting a vulnerability

**Do not** open a public issue for security reports.

Email: **contact@limxdynamics.com**
Subject prefix: `[tron2_rl_lab]`

Please include:

- Affected file(s) and commit / tag (e.g.
  `exts/bipedal_locomotion/.../limx_base_env_cfg.py`,
  `scripts/rsl_rl/play.py`, `rsl_rl/rsl_rl/algorithms/ppo.py`, …).
- A minimal reproducer or proof of concept — for RL / safety issues,
  a task ID plus the config or seed that reproduces the behaviour.
  For DASF_TRON2A, also include the 20-joint action order and whether
  the actor normalizer/history encoder came from the same checkpoint.
- Impact assessment (e.g., "policy export writes outside `logs/`",
  "malformed USD crashes Isaac Sim", "reward term X trains a gait
  that violates a documented safety envelope").
- Your preferred disclosure timeline and contact.

We aim to acknowledge reports within **3 business days** and provide
a remediation plan or an initial mitigation within **14 calendar
days**. We support coordinated disclosure; please do not publish
details until a fix or advisory is available.

## Out of scope

- Bugs in third-party runtimes (Isaac Sim, Isaac Lab, PyTorch,
  `gymnasium`, USD, `trimesh`) — report those upstream.
- Physical safety of the robot itself (real-hardware fall, actuator
  overheat, cabling) — report to the deployment repositories or to
  LimX product support.
- Requests to publish trained weights, checkpoints, calibration data,
  or Weights & Biases artifacts — this repository intentionally
  excludes those (see `THIRD_PARTY_NOTICES.md` §8).

## Safe harbor

Good-faith security research that follows this policy will not be
pursued legally by LimX Dynamics. Please respect user privacy, avoid
service disruption, and do not access data beyond what is necessary
to demonstrate the issue. Do not run experiments on a physical
TRON2A that could damage the robot or endanger operators.
