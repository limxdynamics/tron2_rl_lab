from __future__ import annotations

import math

import torch

import isaaclab.utils.math as math_utils
from isaaclab.assets import Articulation
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab.managers import ManagerTermBase, RewardTermCfg, SceneEntityCfg
from isaaclab.sensors import ContactSensor
from isaaclab.utils.string import resolve_matching_names_values


def track_linear_velocity(
    env: ManagerBasedRLEnv,
    std: float,
    command_name: str,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Track commanded planar velocity and suppress vertical root velocity."""
    asset: Articulation = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    xy_error = torch.sum(
        torch.square(command[:, :2] - asset.data.root_link_lin_vel_b[:, :2]),
        dim=1,
    )
    z_error = torch.square(asset.data.root_link_lin_vel_b[:, 2])
    return torch.exp(-(xy_error + 2.0 * z_error) / std**2)


def track_angular_velocity(
    env: ManagerBasedRLEnv,
    std: float,
    command_name: str,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Track commanded yaw rate while suppressing root roll and pitch rates."""
    asset: Articulation = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    angular_velocity = asset.data.root_link_ang_vel_b
    z_error = torch.square(command[:, 2] - angular_velocity[:, 2])
    xy_error = torch.sum(torch.square(angular_velocity[:, :2]), dim=1)
    return torch.exp(-(z_error + 0.05 * xy_error) / std**2)


def body_orientation_l2(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize torso tilt using gravity projected into the torso frame."""
    asset: Articulation = env.scene[asset_cfg.name]
    body_quat_w = asset.data.body_link_quat_w[:, asset_cfg.body_ids]
    gravity_w = torch.zeros(
        (*body_quat_w.shape[:-1], 3),
        device=body_quat_w.device,
        dtype=body_quat_w.dtype,
    )
    gravity_w[..., 2] = -1.0
    projected_gravity = math_utils.quat_apply_inverse(
        body_quat_w.reshape(-1, 4), gravity_w.reshape(-1, 3)
    ).reshape_as(gravity_w)
    return torch.sum(torch.square(projected_gravity[..., :2]), dim=(1, 2))


def torso_pitch_l2(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg,
    deadband_deg: float,
) -> torch.Tensor:
    """Penalize torso pitch outside a small upright deadband."""
    asset: Articulation = env.scene[asset_cfg.name]
    body_quat_w = asset.data.body_link_quat_w[:, asset_cfg.body_ids]
    gravity_w = torch.zeros(
        (*body_quat_w.shape[:-1], 3),
        device=body_quat_w.device,
        dtype=body_quat_w.dtype,
    )
    gravity_w[..., 2] = -1.0
    projected_gravity = math_utils.quat_apply_inverse(
        body_quat_w.reshape(-1, 4), gravity_w.reshape(-1, 3)
    ).reshape_as(gravity_w)
    pitch = torch.asin(torch.clamp(projected_gravity[..., 0], -1.0, 1.0))
    pitch_error = torch.clamp(
        torch.abs(pitch) - math.radians(deadband_deg), min=0.0
    )
    return torch.sum(torch.square(pitch_error), dim=1)


def body_angular_velocity_l2(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize torso roll and pitch angular velocity."""
    asset: Articulation = env.scene[asset_cfg.name]
    angular_velocity = asset.data.body_link_ang_vel_w[:, asset_cfg.body_ids, :2]
    return torch.sum(torch.square(angular_velocity), dim=(1, 2))


def feet_gait(
    env: ManagerBasedRLEnv,
    period: float,
    offset: list[float],
    threshold: float,
    command_threshold: float,
    command_name: str,
    sensor_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Reward agreement between measured contacts and the configured phase schedule."""
    sensor: ContactSensor = env.scene.sensors[sensor_cfg.name]
    is_contact = sensor.data.current_contact_time[:, sensor_cfg.body_ids] > 0.0
    global_phase = ((env.episode_length_buf * env.step_dt) / period).unsqueeze(1)
    offsets = torch.as_tensor(
        offset, device=env.device, dtype=global_phase.dtype
    ).view(1, -1)
    is_stance = ((global_phase + offsets) % 1.0) < threshold
    command = env.command_manager.get_command(command_name)
    command_magnitude = torch.linalg.vector_norm(command[:, :2], dim=1) + torch.abs(
        command[:, 2]
    )
    return (is_stance == is_contact).float().mean(dim=1) * (
        command_magnitude > command_threshold
    )


def arm_swing_phase_l2(
    env: ManagerBasedRLEnv,
    period: float,
    shoulder_amplitude: float,
    elbow_flexion: float,
    elbow_weight: float,
    max_forward_speed: float,
    command_name: str,
    command_threshold: float,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Track symmetric shoulder swing and forward-arm elbow flexion at gait frequency."""
    asset: Articulation = env.scene[asset_cfg.name]
    command_x = env.command_manager.get_command(command_name)[:, 0]
    speed_ratio = torch.clamp(command_x / max_forward_speed, -1.0, 1.0)
    speed_scale = torch.abs(speed_ratio)
    phase = env.episode_length_buf * env.step_dt / period
    leg_order = torch.cos(phase * 2.0 * torch.pi) * torch.sign(speed_ratio)

    # In the imported Isaac USD, negative shoulder pitch moves that hand backward.
    shoulder_targets = shoulder_amplitude * speed_scale.unsqueeze(1) * torch.stack(
        (-leg_order, leg_order), dim=1
    )
    elbow_targets = -elbow_flexion * speed_scale.unsqueeze(1) * torch.stack(
        (0.5 * (1.0 - leg_order), 0.5 * (1.0 + leg_order)), dim=1
    )
    targets = torch.cat((shoulder_targets, elbow_targets), dim=1)

    joint_pos_rel = (
        asset.data.joint_pos[:, asset_cfg.joint_ids]
        - asset.data.default_joint_pos[:, asset_cfg.joint_ids]
    )
    shoulder_cost = torch.mean(torch.square(joint_pos_rel[:, :2] - targets[:, :2]), dim=1)
    elbow_cost = torch.mean(torch.square(joint_pos_rel[:, 2:] - targets[:, 2:]), dim=1)
    return (shoulder_cost + elbow_weight * elbow_cost) * (
        torch.abs(command_x) > command_threshold
    )


def arm_leg_coordination_l2(
    env: ManagerBasedRLEnv,
    command_name: str,
    command_threshold: float,
    foot_position_scale: float,
    hand_position_scale: float,
    hand_asset_cfg: SceneEntityCfg,
    foot_asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize ipsilateral swing using measured hand and foot positions."""
    asset: Articulation = env.scene[hand_asset_cfg.name]
    foot_positions_w = asset.data.body_link_pos_w[:, foot_asset_cfg.body_ids]
    hand_positions_w = asset.data.body_link_pos_w[:, hand_asset_cfg.body_ids]
    root_positions_w = asset.data.root_link_pos_w.unsqueeze(1)
    root_quaternions_w = asset.data.root_link_quat_w.unsqueeze(1).expand(-1, 2, -1)
    foot_positions_b = math_utils.quat_apply_inverse(
        root_quaternions_w.reshape(-1, 4),
        (foot_positions_w - root_positions_w).reshape(-1, 3),
    ).reshape_as(foot_positions_w)
    hand_positions_b = math_utils.quat_apply_inverse(
        root_quaternions_w.reshape(-1, 4),
        (hand_positions_w - root_positions_w).reshape(-1, 3),
    ).reshape_as(hand_positions_w)

    foot_order = torch.tanh(
        (foot_positions_b[:, 0, 0] - foot_positions_b[:, 1, 0])
        / foot_position_scale
    )
    hand_order = torch.tanh(
        (hand_positions_b[:, 0, 0] - hand_positions_b[:, 1, 0])
        / hand_position_scale
    )
    command_x = env.command_manager.get_command(command_name)[:, 0]
    return torch.square(hand_order + foot_order) * (
        torch.abs(command_x) > command_threshold
    )


def _sole_kinematics(
    asset: Articulation,
    body_ids: list[int],
    sole_offsets: list[tuple[float, float, float]],
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return world positions and velocities of DASF_TRON2A sole points."""
    body_quat_w = asset.data.body_link_quat_w[:, body_ids]
    offsets = torch.as_tensor(
        sole_offsets, device=body_quat_w.device, dtype=body_quat_w.dtype
    ).unsqueeze(0).expand(body_quat_w.shape[0], -1, -1)
    offsets_w = math_utils.quat_apply(
        body_quat_w.reshape(-1, 4), offsets.reshape(-1, 3)
    ).reshape_as(offsets)
    positions = asset.data.body_link_pos_w[:, body_ids] + offsets_w
    velocities = asset.data.body_link_lin_vel_w[:, body_ids] + torch.cross(
        asset.data.body_link_ang_vel_w[:, body_ids], offsets_w, dim=-1
    )
    return positions, velocities


def feet_clearance(
    env: ManagerBasedRLEnv,
    target_height: float,
    command_name: str,
    command_threshold: float,
    sole_offsets: list[tuple[float, float, float]],
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize sole clearance error, weighted by planar sole velocity."""
    asset: Articulation = env.scene[asset_cfg.name]
    sole_positions, sole_velocities = _sole_kinematics(
        asset, asset_cfg.body_ids, sole_offsets
    )
    cost = torch.sum(
        torch.abs(sole_positions[..., 2] - target_height)
        * torch.linalg.vector_norm(sole_velocities[..., :2], dim=-1),
        dim=1,
    )
    command = env.command_manager.get_command(command_name)
    command_magnitude = torch.linalg.vector_norm(command[:, :2], dim=1) + torch.abs(
        command[:, 2]
    )
    return cost * (command_magnitude > command_threshold)


def feet_slip(
    env: ManagerBasedRLEnv,
    command_name: str,
    command_threshold: float,
    sole_offsets: list[tuple[float, float, float]],
    sensor_cfg: SceneEntityCfg,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize squared planar sole velocity while a foot is in contact."""
    asset: Articulation = env.scene[asset_cfg.name]
    sensor: ContactSensor = env.scene.sensors[sensor_cfg.name]
    _, sole_velocities = _sole_kinematics(asset, asset_cfg.body_ids, sole_offsets)
    in_contact = (
        sensor.data.current_contact_time[:, sensor_cfg.body_ids] > 0.0
    ).float()
    cost = torch.sum(
        torch.sum(torch.square(sole_velocities[..., :2]), dim=-1) * in_contact,
        dim=1,
    )
    command = env.command_manager.get_command(command_name)
    command_magnitude = torch.linalg.vector_norm(command[:, :2], dim=1) + torch.abs(
        command[:, 2]
    )
    return cost * (command_magnitude > command_threshold)


def soft_landing(
    env: ManagerBasedRLEnv,
    command_name: str,
    command_threshold: float,
    sensor_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize contact force only on a foot's first landing step."""
    sensor: ContactSensor = env.scene.sensors[sensor_cfg.name]
    forces = sensor.data.net_forces_w[:, sensor_cfg.body_ids]
    first_contact = sensor.compute_first_contact(env.step_dt)[:, sensor_cfg.body_ids]
    cost = torch.sum(torch.linalg.vector_norm(forces, dim=-1) * first_contact, dim=1)
    command = env.command_manager.get_command(command_name)
    command_magnitude = torch.linalg.vector_norm(command[:, :2], dim=1) + torch.abs(
        command[:, 2]
    )
    return cost * (command_magnitude > command_threshold)


def stand_still(
    env: ManagerBasedRLEnv,
    command_name: str,
    command_threshold: float,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize joint displacement from the default pose for near-zero commands."""
    asset: Articulation = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    command_magnitude = torch.linalg.vector_norm(command[:, :2], dim=1) + torch.abs(
        command[:, 2]
    )
    joint_error = asset.data.joint_pos[:, asset_cfg.joint_ids] - asset.data.default_joint_pos[
        :, asset_cfg.joint_ids
    ]
    return torch.sum(torch.abs(joint_error), dim=1) * (
        command_magnitude < command_threshold
    )


class SpeedDependentPostureReward(ManagerTermBase):
    """Posture reward with command-dependent per-joint tolerance.

    Standing environments stay close to the configured default pose. Walking
    environments are allowed to move the legs and arms, which gives the policy
    room to discover whole-body balance and arm swing.
    """

    def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRLEnv):
        super().__init__(cfg, env)

        asset_cfg: SceneEntityCfg = cfg.params["asset_cfg"]
        asset: Articulation = env.scene[asset_cfg.name]
        if isinstance(asset_cfg.joint_ids, slice):
            joint_ids = list(range(asset.num_joints))
        else:
            joint_ids = asset_cfg.joint_ids
        joint_names = [asset.joint_names[index] for index in joint_ids]

        self._joint_ids = joint_ids
        self._default_joint_pos = asset.data.default_joint_pos[:, joint_ids]
        self._std_standing = self._resolve_std(
            cfg.params["std_standing"], joint_names, env.device
        )
        self._std_walking = self._resolve_std(
            cfg.params["std_walking"], joint_names, env.device
        )
        self._std_running = self._resolve_std(
            cfg.params["std_running"], joint_names, env.device
        )

    @staticmethod
    def _resolve_std(
        values: dict[str, float], joint_names: list[str], device: str
    ) -> torch.Tensor:
        _, _, resolved_values = resolve_matching_names_values(values, joint_names)
        return torch.tensor(resolved_values, device=device, dtype=torch.float32)

    def __call__(
        self,
        env: ManagerBasedRLEnv,
        command_name: str,
        asset_cfg: SceneEntityCfg,
        std_standing: dict[str, float],
        std_walking: dict[str, float],
        std_running: dict[str, float],
        walking_threshold: float,
        running_threshold: float,
    ) -> torch.Tensor:
        del std_standing, std_walking, std_running

        asset: Articulation = env.scene[asset_cfg.name]
        command = env.command_manager.get_command(command_name)
        command_speed = torch.linalg.vector_norm(command[:, :2], dim=1) + torch.abs(
            command[:, 2]
        )

        standing = command_speed < walking_threshold
        running = command_speed >= running_threshold
        walking = ~(standing | running)
        std = (
            self._std_standing * standing.unsqueeze(1)
            + self._std_walking * walking.unsqueeze(1)
            + self._std_running * running.unsqueeze(1)
        )

        joint_error = (
            asset.data.joint_pos[:, self._joint_ids] - self._default_joint_pos
        )
        return torch.exp(-torch.mean(torch.square(joint_error / std), dim=1))


def whole_body_angular_momentum_l2(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    normalize_by_mass: bool = True,
) -> torch.Tensor:
    """Penalize whole-body angular momentum about the system center of mass.

    The term includes both each body's spin angular momentum and the orbital
    component induced by body translation. Mass normalization keeps the scale
    stable across DASF_TRON2A body-mass configurations.
    """

    asset: Articulation = env.scene[asset_cfg.name]
    body_ids = asset_cfg.body_ids

    body_pos = asset.data.body_com_pos_w[:, body_ids]
    body_lin_vel = asset.data.body_com_lin_vel_w[:, body_ids]
    body_ang_vel = asset.data.body_com_ang_vel_w[:, body_ids]
    # Isaac Lab keeps default physical properties in a CPU-side cache, while
    # live articulation state follows the environment device.
    body_masses = getattr(
        env, "_dasf_randomized_body_masses", asset.data.default_mass
    )
    body_inertias = getattr(
        env, "_dasf_randomized_body_inertias", asset.data.default_inertia
    )
    masses = body_masses[:, body_ids].to(
        device=body_pos.device, dtype=body_pos.dtype
    ).unsqueeze(-1)

    total_mass = torch.sum(masses, dim=1)
    system_com = torch.sum(masses * body_pos, dim=1) / total_mass
    linear_momentum = masses * body_lin_vel
    orbital_momentum = torch.cross(
        body_pos - system_com.unsqueeze(1), linear_momentum, dim=-1
    )

    inertia_body = (
        body_inertias[:, body_ids]
        .to(device=body_ang_vel.device, dtype=body_ang_vel.dtype)
        .reshape(*body_ang_vel.shape[:-1], 3, 3)
    )
    body_rotation = math_utils.matrix_from_quat(
        asset.data.body_link_quat_w[:, body_ids]
    )
    inertia_world = (
        body_rotation @ inertia_body @ body_rotation.transpose(-1, -2)
    )
    spin_momentum = torch.matmul(
        inertia_world, body_ang_vel.unsqueeze(-1)
    ).squeeze(-1)

    angular_momentum = torch.sum(orbital_momentum + spin_momentum, dim=1)
    if normalize_by_mass:
        angular_momentum = angular_momentum / total_mass
    return torch.sum(torch.square(angular_momentum), dim=1)
