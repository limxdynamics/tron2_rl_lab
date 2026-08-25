from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

import torch

import isaaclab.utils.math as math_utils
from isaaclab.assets import Articulation
from isaaclab.envs import ManagerBasedEnv, ManagerBasedRLEnv
from isaaclab.managers import SceneEntityCfg

from .rewards import (
    SpeedDependentPostureReward,
    arm_leg_coordination_l2,
    arm_swing_phase_l2,
    body_angular_velocity_l2,
    body_orientation_l2,
    feet_clearance,
    feet_gait,
    feet_slip,
    soft_landing,
    stand_still,
    torso_pitch_l2,
    track_angular_velocity,
    track_linear_velocity,
    whole_body_angular_momentum_l2,
)
from bipedal_locomotion.tasks.locomotion.mdp.events import _randomize_prop_by_op


def commands_vel(
    env: ManagerBasedRLEnv,
    env_ids: Sequence[int],
    command_name: str,
    velocity_stages: list[dict],
) -> torch.Tensor:
    """Apply the staged velocity-command ranges."""
    del env_ids
    command_term = env.command_manager.get_term(command_name)
    for stage in velocity_stages:
        if env.common_step_counter > stage["step"]:
            for range_name in ("lin_vel_x", "lin_vel_y", "ang_vel_z"):
                if range_name in stage:
                    setattr(command_term.cfg.ranges, range_name, stage[range_name])
    return torch.tensor(command_term.cfg.ranges.lin_vel_x[1], device=env.device)


def joint_pos_rel_with_encoder_bias(
    env: ManagerBasedEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Return DASF_TRON2A joint positions relative to default with persistent bias."""
    asset: Articulation = env.scene[asset_cfg.name]
    joint_pos = asset.data.joint_pos[:, asset_cfg.joint_ids]
    default_joint_pos = asset.data.default_joint_pos[:, asset_cfg.joint_ids]
    if hasattr(env, "_dasf_joint_encoder_bias"):
        bias = env._dasf_joint_encoder_bias[:, asset_cfg.joint_ids]
    else:
        bias = torch.zeros_like(joint_pos)
    return joint_pos - default_joint_pos + bias


def robot_mass(
    env: ManagerBasedEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Return the live DASF_TRON2A body masses used by the privileged critic."""
    asset: Articulation = env.scene[asset_cfg.name]
    masses = getattr(
        env, "_dasf_randomized_body_masses", asset.data.default_mass
    )
    return masses.to(env.device)


def gait_phase(
    env: ManagerBasedRLEnv,
    period: float,
    command_name: str,
) -> torch.Tensor:
    """Return the fixed-period gait phase, disabled for standing commands."""
    global_phase = (env.episode_length_buf * env.step_dt) % period / period
    phase = torch.stack(
        (
            torch.sin(global_phase * 2.0 * torch.pi),
            torch.cos(global_phase * 2.0 * torch.pi),
        ),
        dim=1,
    )
    command = env.command_manager.get_command(command_name)
    standing = torch.linalg.vector_norm(command, dim=1) < 0.1
    return torch.where(standing.unsqueeze(1), torch.zeros_like(phase), phase)


def randomize_joint_encoder_bias(
    env: ManagerBasedEnv,
    env_ids: torch.Tensor | None,
    bias_range: tuple[float, float],
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
):
    """Sample one persistent DASF_TRON2A joint encoder bias per environment."""
    asset: Articulation = env.scene[asset_cfg.name]
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device=asset.device)
    if isinstance(asset_cfg.joint_ids, slice):
        joint_ids = torch.arange(asset.num_joints, device=asset.device)
    else:
        joint_ids = torch.as_tensor(asset_cfg.joint_ids, device=asset.device)
    if not hasattr(env, "_dasf_joint_encoder_bias"):
        env._dasf_joint_encoder_bias = torch.zeros(
            env.scene.num_envs,
            asset.num_joints,
            device=asset.device,
            dtype=asset.data.joint_pos.dtype,
        )
    sampled_bias = math_utils.sample_uniform(
        bias_range[0],
        bias_range[1],
        (len(env_ids), len(joint_ids)),
        asset.device,
    )
    env._dasf_joint_encoder_bias[env_ids[:, None], joint_ids] = sampled_bias


def randomize_shared_body_material(
    env: ManagerBasedEnv,
    env_ids: torch.Tensor | None,
    friction_range: tuple[float, float],
    restitution: float,
    asset_cfg: SceneEntityCfg,
):
    """Apply one shared friction sample to all selected DASF_TRON2A foot shapes."""
    asset: Articulation = env.scene[asset_cfg.name]
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device="cpu")
    else:
        env_ids = env_ids.cpu()

    num_shapes_per_body = []
    for link_path in asset.root_physx_view.link_paths[0]:
        link_view = asset._physics_sim_view.create_rigid_body_view(link_path)
        num_shapes_per_body.append(link_view.max_shapes)

    materials = asset.root_physx_view.get_material_properties()
    friction = math_utils.sample_uniform(
        friction_range[0], friction_range[1], (len(env_ids), 1), device="cpu"
    )
    for body_id in asset_cfg.body_ids:
        start_idx = sum(num_shapes_per_body[:body_id])
        end_idx = start_idx + num_shapes_per_body[body_id]
        materials[env_ids, start_idx:end_idx, 0] = friction
        materials[env_ids, start_idx:end_idx, 1] = friction
        materials[env_ids, start_idx:end_idx, 2] = restitution
    asset.root_physx_view.set_material_properties(materials, env_ids)


def randomize_rigid_body_mass_inertia(
    env: ManagerBasedEnv,
    env_ids: torch.Tensor | None,
    asset_cfg: SceneEntityCfg,
    mass_inertia_distribution_params: tuple[float, float],
    operation: Literal["add", "scale", "abs"],
    distribution: Literal["uniform", "log_uniform", "gaussian"] = "uniform",
):
    """Randomize DASF_TRON2A body masses and inertias from nominal properties."""
    asset: Articulation = env.scene[asset_cfg.name]

    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device="cpu")
    else:
        env_ids = env_ids.cpu()

    if asset_cfg.body_ids == slice(None):
        body_ids = torch.arange(asset.num_bodies, dtype=torch.int, device="cpu")
    else:
        body_ids = torch.tensor(asset_cfg.body_ids, dtype=torch.int, device="cpu")

    inertias = asset.root_physx_view.get_inertias().clone()
    masses = asset.root_physx_view.get_masses().clone()
    nominal_masses = asset.data.default_mass.cpu()
    nominal_inertias = asset.data.default_inertia.cpu()
    masses[env_ids[:, None], body_ids] = nominal_masses[
        env_ids[:, None], body_ids
    ]
    inertias[env_ids[:, None], body_ids] = nominal_inertias[
        env_ids[:, None], body_ids
    ]

    masses = _randomize_prop_by_op(
        masses,
        mass_inertia_distribution_params,
        env_ids,
        body_ids,
        operation=operation,
        distribution=distribution,
    )
    scale = masses[env_ids[:, None], body_ids] / nominal_masses[
        env_ids[:, None], body_ids
    ]
    inertias[env_ids[:, None], body_ids] *= scale.unsqueeze(-1)

    asset.root_physx_view.set_masses(masses, env_ids)
    asset.root_physx_view.set_inertias(inertias, env_ids)

    if not hasattr(env, "_dasf_randomized_body_masses"):
        env._dasf_randomized_body_masses = masses.clone()
        env._dasf_randomized_body_inertias = inertias.clone()
    else:
        env._dasf_randomized_body_masses[env_ids] = masses[env_ids]
        env._dasf_randomized_body_inertias[env_ids] = inertias[env_ids]