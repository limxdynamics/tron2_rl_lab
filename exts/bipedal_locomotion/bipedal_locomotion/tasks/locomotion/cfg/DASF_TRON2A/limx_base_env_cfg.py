import math
from dataclasses import MISSING

from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg, RayCasterCfg
from isaaclab.sim import DomeLightCfg, MdlFileCfg, RigidBodyMaterialCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR, ISAACLAB_NUCLEUS_DIR
from isaaclab.utils.noise import UniformNoiseCfg as Unoise

from bipedal_locomotion.tasks.locomotion import mdp

from . import mdp as dasf_mdp


# Policy ordering is explicit because this ordering must also be used by the
# eventual deployment adapter.
LOWER_JOINT_NAMES = [
    "proximal_pitch_L_Joint",
    "proximal_roll_L_Joint",
    "proximal_yaw_L_Joint",
    "knee_L_Joint",
    "ankle_pitch_L_Joint",
    "proximal_pitch_R_Joint",
    "proximal_roll_R_Joint",
    "proximal_yaw_R_Joint",
    "knee_R_Joint",
    "ankle_pitch_R_Joint",
]

UPPER_POLICY_JOINT_NAMES = [
    "proximal_pitch_L_U_Joint",
    "proximal_roll_L_U_Joint",
    "proximal_yaw_L_U_Joint",
    "elbow_L_U_Joint",
    "wrist_roll_L_U_Joint",
    "proximal_pitch_R_U_Joint",
    "proximal_roll_R_U_Joint",
    "proximal_yaw_R_U_Joint",
    "elbow_R_U_Joint",
    "wrist_roll_R_U_Joint",
]

# Physical order after the upper module's flipped installation.
ARM_SHOULDER_JOINT_NAMES = [
    "proximal_pitch_R_U_Joint",
    "proximal_pitch_L_U_Joint",
]
ARM_SWING_JOINT_NAMES = ARM_SHOULDER_JOINT_NAMES + [
    "elbow_R_U_Joint",
    "elbow_L_U_Joint",
]
HAND_BODY_NAMES = [
    "grasper_R_U_Link",
    "grasper_L_U_Link",
]

POLICY_JOINT_NAMES = LOWER_JOINT_NAMES + UPPER_POLICY_JOINT_NAMES

LOCKED_JOINT_NAMES = [
    "wrist_yaw_L_U_Joint",
    "wrist_pitch_L_U_Joint",
    "wrist_yaw_R_U_Joint",
    "wrist_pitch_R_U_Joint",
    "head_yaw_Joint",
    "head_pitch_Joint",
]
ALL_JOINT_NAMES = POLICY_JOINT_NAMES + LOCKED_JOINT_NAMES

FOOT_BODY_PATTERN = "ankle_pitch_[LR]_Link"
FOOT_BODY_NAMES = ["ankle_pitch_L_Link", "ankle_pitch_R_Link"]
TORSO_BODY_NAME = "upper_base_Link"
GAIT_PERIOD = 1.0

# Lowest sole contact points from the DASF_TRON2A URDF collision spheres.
SOLE_OFFSETS = [
    (0.014425, -0.0355, -0.07374),
    (0.014425, 0.0355, -0.07374),
]


@configclass
class DASF_TRON2A_SceneCfg(InteractiveSceneCfg):
    """Self-contained DASF_TRON2A scene configuration."""

    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        terrain_generator=None,
        max_init_terrain_level=0,
        collision_group=-1,
        physics_material=RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=1.0,
        ),
        visual_material=MdlFileCfg(
            mdl_path=(
                f"{ISAACLAB_NUCLEUS_DIR}/Materials/"
                "TilesMarbleSpiderWhiteBrickBondHoned/"
                "TilesMarbleSpiderWhiteBrickBondHoned.mdl"
            ),
            project_uvw=True,
            texture_scale=(0.25, 0.25),
        ),
        debug_vis=False,
    )

    light = AssetBaseCfg(
        prim_path="/World/skyLight",
        spawn=DomeLightCfg(
            intensity=750.0,
            color=(0.9, 0.9, 0.9),
            texture_file=(
                f"{ISAAC_NUCLEUS_DIR}/Materials/Textures/Skies/PolyHaven/"
                "kloofendal_43d_clear_puresky_4k.hdr"
            ),
        ),
    )

    robot: ArticulationCfg = MISSING
    height_scanner: RayCasterCfg = MISSING
    contact_forces = ContactSensorCfg(
        prim_path="{ENV_REGEX_NS}/Robot/.*",
        history_length=4,
        track_air_time=True,
        update_period=0.0,
    )


@configclass
class CommandsCfg:
    """Velocity and gait commands for flat-ground DASF_TRON2A locomotion."""

    base_velocity = mdp.UniformVelocityCommandCfg(
        asset_name="robot",
        heading_command=True,
        heading_control_stiffness=0.5,
        rel_standing_envs=0.05,
        rel_heading_envs=1.0,
        debug_vis=True,
        resampling_time_range=(3.0, 8.0),
        ranges=mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(-0.5, 0.6),
            lin_vel_y=(-0.5, 0.5),
            ang_vel_z=(-1.0, 1.0),
            heading=(-math.pi, math.pi),
        ),
    )


@configclass
class ActionsCfg:
    """20-DoF position actions: 10 lower-body and 10 upper-body joints."""

    lower_joint_pos = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=LOWER_JOINT_NAMES,
        scale={
            "proximal_(pitch|roll)_[LR]_Joint": 0.25,
            "knee_[LR]_Joint": 0.25,
            "proximal_yaw_[LR]_Joint": 0.25,
            "ankle_pitch_[LR]_Joint": 0.25,
        },
        use_default_offset=True,
        preserve_order=True,
    )
    upper_joint_pos = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=UPPER_POLICY_JOINT_NAMES,
        scale={
            "proximal_pitch_[LR]_U_Joint": 0.25,
            "proximal_roll_[LR]_U_Joint": 0.25,
            "proximal_yaw_[LR]_U_Joint": 0.25,
            "elbow_[LR]_U_Joint": 0.25,
            "wrist_roll_[LR]_U_Joint": 0.25,
        },
        use_default_offset=True,
        preserve_order=True,
    )


@configclass
class ObservationsCfg:
    """DASF_TRON2A observations with an explicit 20-joint policy order."""

    @configclass
    class PolicyCfg(ObsGroup):
        base_ang_vel = ObsTerm(
            func=mdp.base_ang_vel,
            noise=Unoise(n_min=-0.2, n_max=0.2),
            scale=0.25,
        )
        proj_gravity = ObsTerm(
            func=mdp.projected_gravity,
            noise=Unoise(n_min=-0.05, n_max=0.05),
            scale=1.0,
        )
        joint_pos = ObsTerm(
            func=dasf_mdp.joint_pos_rel_with_encoder_bias,
            params={
                "asset_cfg": SceneEntityCfg(
                    "robot", joint_names=POLICY_JOINT_NAMES, preserve_order=True
                )
            },
            noise=Unoise(n_min=-0.01, n_max=0.01),
            scale=1.0,
        )
        joint_vel = ObsTerm(
            func=mdp.joint_vel_rel,
            params={
                "asset_cfg": SceneEntityCfg(
                    "robot", joint_names=POLICY_JOINT_NAMES, preserve_order=True
                )
            },
            noise=Unoise(n_min=-1.5, n_max=1.5),
            scale=0.05,
        )
        last_action = ObsTerm(func=mdp.last_action)
        phase = ObsTerm(
            func=dasf_mdp.gait_phase,
            params={"period": GAIT_PERIOD, "command_name": "base_velocity"},
        )

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    @configclass
    class HistoryObsCfg(PolicyCfg):
        def __post_init__(self):
            super().__post_init__()
            self.history_length = 10
            self.flatten_history_dim = False

    @configclass
    class CriticCfg(ObsGroup):
        base_lin_vel = ObsTerm(func=mdp.base_lin_vel, scale=1.0)
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel, scale=0.25)
        proj_gravity = ObsTerm(func=mdp.projected_gravity, scale=1.0)
        joint_pos = ObsTerm(
            func=dasf_mdp.joint_pos_rel_with_encoder_bias,
            params={
                "asset_cfg": SceneEntityCfg(
                    "robot", joint_names=POLICY_JOINT_NAMES, preserve_order=True
                )
            },
            scale=1.0,
        )
        joint_vel = ObsTerm(
            func=mdp.joint_vel_rel,
            params={
                "asset_cfg": SceneEntityCfg(
                    "robot", joint_names=POLICY_JOINT_NAMES, preserve_order=True
                )
            },
            scale=0.05,
        )
        last_action = ObsTerm(func=mdp.last_action)
        phase = ObsTerm(
            func=dasf_mdp.gait_phase,
            params={"period": GAIT_PERIOD, "command_name": "base_velocity"},
        )
        height_scan = ObsTerm(
            func=mdp.height_scan,
            params={"sensor_cfg": SceneEntityCfg("height_scanner"), "offset": 0.72},
            clip=(-1.0, 1.0),
            scale=5.0,
        )

        # Privileged critic observations retain all articulation dynamics.
        robot_joint_torque = ObsTerm(func=mdp.robot_joint_torque, scale=0.05)
        robot_joint_acc = ObsTerm(func=mdp.robot_joint_acc, scale=0.0025)
        feet_lin_vel = ObsTerm(
            func=mdp.feet_lin_vel,
            params={
                "asset_cfg": SceneEntityCfg(
                    "robot", body_names=FOOT_BODY_PATTERN
                )
            },
        )
        robot_mass = ObsTerm(func=dasf_mdp.robot_mass)
        feet_contact_force = ObsTerm(
            func=mdp.robot_contact_force,
            params={
                "sensor_cfg": SceneEntityCfg(
                    "contact_forces", body_names=FOOT_BODY_PATTERN
                )
            },
            scale=0.01,
        )

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    @configclass
    class CommandsObsCfg(ObsGroup):
        velocity_commands = ObsTerm(
            func=mdp.generated_commands,
            params={"command_name": "base_velocity"},
        )

    policy: PolicyCfg = PolicyCfg()
    critic: CriticCfg = CriticCfg()
    commands: CommandsObsCfg = CommandsObsCfg()
    obsHistory: HistoryObsCfg = HistoryObsCfg()


@configclass
class EventsCfg:
    """DASF_TRON2A domain randomization with one combined mass/inertia event."""

    mass_inertia = EventTerm(
        func=dasf_mdp.randomize_rigid_body_mass_inertia,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg(
                "robot",
                body_names=[
                    "base_Link",
                    TORSO_BODY_NAME,
                    ".*_[LR](_U)?_Link",
                ],
            ),
            "mass_inertia_distribution_params": (0.8, 1.2),
            "operation": "scale",
        },
    )
    body_physics_material = EventTerm(
        func=mdp.randomize_rigid_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg(
                "robot", body_names="(?!ankle_pitch_[LR]_Link).*"
            ),
            "static_friction_range": (0.4, 1.2),
            "dynamic_friction_range": (0.7, 0.9),
            "restitution_range": (0.0, 0.5),
            "num_buckets": 48,
        },
    )
    foot_friction = EventTerm(
        func=dasf_mdp.randomize_shared_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=FOOT_BODY_NAMES),
            "friction_range": (0.3, 1.6),
            "restitution": 0.0,
        },
    )
    encoder_bias = EventTerm(
        func=dasf_mdp.randomize_joint_encoder_bias,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=".*"),
            "bias_range": (-0.015, 0.015),
        },
    )
    actuator_gains = EventTerm(
        func=mdp.randomize_actuator_gains,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=".*"),
            "stiffness_distribution_params": (0.8, 1.2),
            "damping_distribution_params": (0.8, 1.2),
            "operation": "scale",
        },
    )
    base_com = EventTerm(
        func=mdp.randomize_rigid_body_coms,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg(
                "robot", body_names=["base_Link", TORSO_BODY_NAME]
            ),
            "com_distribution_params": (
                (-0.05, 0.05),
                (-0.05, 0.05),
                (-0.05, 0.05),
            ),
            "operation": "add",
            "distribution": "uniform",
        },
    )
    reset_base = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {
                "x": (-0.5, 0.5),
                "y": (-0.5, 0.5),
                "z": (0.0, 0.0),
                "yaw": (-3.14, 3.14),
            },
            "velocity_range": {
                "x": (-0.5, 0.5),
                "y": (-0.5, 0.5),
                "z": (-0.5, 0.5),
                "roll": (-0.5, 0.5),
                "pitch": (-0.5, 0.5),
                "yaw": (-0.5, 0.5),
            },
        },
    )
    reset_joints = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "position_range": (-0.2, 0.2),
            "velocity_range": (0.0, 0.0),
            "asset_cfg": SceneEntityCfg(
                "robot", joint_names=POLICY_JOINT_NAMES
            ),
        },
    )
    push_robot = EventTerm(
        func=mdp.push_by_setting_velocity,
        mode="interval",
        interval_range_s=(5.0, 6.0),
        params={
            "velocity_range": {
                "x": (-0.5, 0.5),
                "y": (-0.5, 0.5),
                "z": (-0.4, 0.4),
                "roll": (-0.52, 0.52),
                "pitch": (-0.52, 0.52),
                "yaw": (-0.78, 0.78),
            }
        },
    )


_POSTURE_STD_STANDING = {".*": 0.05}
_POSTURE_STD_WALKING = {
    "proximal_pitch_[LR]_Joint": 0.50,
    "proximal_roll_[LR]_Joint": 0.15,
    "proximal_yaw_[LR]_Joint": 0.15,
    "knee_[LR]_Joint": 0.50,
    "ankle_pitch_[LR]_Joint": 0.15,
    "proximal_pitch_[LR]_U_Joint": 0.30,
    "proximal_roll_[LR]_U_Joint": 0.10,
    "proximal_yaw_[LR]_U_Joint": 0.10,
    "elbow_[LR]_U_Joint": 0.25,
    "wrist_(yaw|pitch|roll)_[LR]_U_Joint": 0.10,
    "head_(yaw|pitch)_Joint": 0.05,
}
_POSTURE_STD_RUNNING = {
    "proximal_pitch_[LR]_Joint": 0.50,
    "proximal_roll_[LR]_Joint": 0.25,
    "proximal_yaw_[LR]_Joint": 0.25,
    "knee_[LR]_Joint": 0.50,
    "ankle_pitch_[LR]_Joint": 0.25,
    "proximal_pitch_[LR]_U_Joint": 0.45,
    "proximal_roll_[LR]_U_Joint": 0.10,
    "proximal_yaw_[LR]_U_Joint": 0.10,
    "elbow_[LR]_U_Joint": 0.25,
    "wrist_(yaw|pitch|roll)_[LR]_U_Joint": 0.10,
    "head_(yaw|pitch)_Joint": 0.05,
}


@configclass
class RewardsCfg:
    """Whole-body rewards mapped to DASF_TRON2A bodies and physical scale."""

    track_linear_velocity = RewTerm(
        func=dasf_mdp.track_linear_velocity,
        weight=1.0,
        params={"command_name": "base_velocity", "std": math.sqrt(0.25)},
    )
    track_angular_velocity = RewTerm(
        func=dasf_mdp.track_angular_velocity,
        weight=1.0,
        params={"command_name": "base_velocity", "std": math.sqrt(0.5)},
    )
    body_orientation_l2 = RewTerm(
        func=dasf_mdp.body_orientation_l2,
        weight=-1.0,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=[TORSO_BODY_NAME])
        },
    )
    torso_pitch_l2 = RewTerm(
        func=dasf_mdp.torso_pitch_l2,
        weight=-2.0,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=[TORSO_BODY_NAME]),
            "deadband_deg": 5.0,
        },
    )
    pose = RewTerm(
        func=dasf_mdp.SpeedDependentPostureReward,
        weight=1.0,
        params={
            "command_name": "base_velocity",
            "asset_cfg": SceneEntityCfg(
                "robot", joint_names=ALL_JOINT_NAMES, preserve_order=True
            ),
            "std_standing": _POSTURE_STD_STANDING,
            "std_walking": _POSTURE_STD_WALKING,
            "std_running": _POSTURE_STD_RUNNING,
            "walking_threshold": 0.1,
            "running_threshold": 1.5,
        },
    )
    body_ang_vel = RewTerm(
        func=dasf_mdp.body_angular_velocity_l2,
        weight=-0.05,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=[TORSO_BODY_NAME])
        },
    )
    angular_momentum = RewTerm(
        func=dasf_mdp.whole_body_angular_momentum_l2,
        weight=-0.00575,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "normalize_by_mass": False,
        },
    )
    is_terminated = RewTerm(func=mdp.is_terminated, weight=-200.0)
    joint_acc_l2 = RewTerm(func=mdp.joint_acc_l2, weight=-2.5e-7)
    joint_pos_limits = RewTerm(func=mdp.joint_pos_limits, weight=-10.0)
    action_rate_l2 = RewTerm(func=mdp.action_rate_l2, weight=-0.05)
    foot_gait = RewTerm(
        func=dasf_mdp.feet_gait,
        weight=0.5,
        params={
            "period": GAIT_PERIOD,
            "offset": [0.0, 0.5],
            "threshold": 0.56,
            "command_threshold": 0.1,
            "command_name": "base_velocity",
            "sensor_cfg": SceneEntityCfg(
                "contact_forces", body_names=FOOT_BODY_NAMES, preserve_order=True
            ),
        },
    )
    arm_swing_phase_l2 = RewTerm(
        func=dasf_mdp.arm_swing_phase_l2,
        weight=-5.0,
        params={
            "period": GAIT_PERIOD,
            "shoulder_amplitude": 0.30,
            "elbow_flexion": 0.25,
            "elbow_weight": 0.5,
            "max_forward_speed": 1.0,
            "command_name": "base_velocity",
            "command_threshold": 0.1,
            "asset_cfg": SceneEntityCfg(
                "robot", joint_names=ARM_SWING_JOINT_NAMES, preserve_order=True
            ),
        },
    )
    arm_leg_coordination_l2 = RewTerm(
        func=dasf_mdp.arm_leg_coordination_l2,
        weight=-0.5,
        params={
            "command_name": "base_velocity",
            "command_threshold": 0.1,
            "foot_position_scale": 0.05,
            "hand_position_scale": 0.10,
            "hand_asset_cfg": SceneEntityCfg(
                "robot", body_names=HAND_BODY_NAMES, preserve_order=True
            ),
            "foot_asset_cfg": SceneEntityCfg(
                "robot", body_names=FOOT_BODY_NAMES, preserve_order=True
            ),
        },
    )
    foot_clearance = RewTerm(
        func=dasf_mdp.feet_clearance,
        weight=-1.0,
        params={
            "target_height": 0.092,
            "command_name": "base_velocity",
            "command_threshold": 0.1,
            "sole_offsets": SOLE_OFFSETS,
            "asset_cfg": SceneEntityCfg(
                "robot", body_names=FOOT_BODY_NAMES, preserve_order=True
            ),
        },
    )
    foot_slip = RewTerm(
        func=dasf_mdp.feet_slip,
        weight=-0.25,
        params={
            "command_name": "base_velocity",
            "command_threshold": 0.1,
            "sole_offsets": SOLE_OFFSETS,
            "sensor_cfg": SceneEntityCfg(
                "contact_forces", body_names=FOOT_BODY_NAMES, preserve_order=True
            ),
            "asset_cfg": SceneEntityCfg(
                "robot", body_names=FOOT_BODY_NAMES, preserve_order=True
            ),
        },
    )
    soft_landing = RewTerm(
        func=dasf_mdp.soft_landing,
        weight=-4.8e-4,
        params={
            "command_name": "base_velocity",
            "command_threshold": 0.1,
            "sensor_cfg": SceneEntityCfg(
                "contact_forces", body_names=FOOT_BODY_NAMES, preserve_order=True
            ),
        },
    )
    stand_still = RewTerm(
        func=dasf_mdp.stand_still,
        weight=-1.0,
        params={
            "command_name": "base_velocity",
            "command_threshold": 0.1,
            "asset_cfg": SceneEntityCfg(
                "robot", joint_names=ALL_JOINT_NAMES, preserve_order=True
            ),
        },
    )
    self_collisions = RewTerm(
        func=mdp.undesired_contacts,
        weight=-1.0,
        params={
            "sensor_cfg": SceneEntityCfg(
                "contact_forces", body_names="(?!ankle_pitch_[LR]_Link).*"
            ),
            "threshold": 21.0,
        },
    )


@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    fell_over = DoneTerm(
        func=mdp.bad_orientation,
        params={"limit_angle": math.radians(70.0)},
    )


@configclass
class CurriculumCfg:
    command_vel = CurrTerm(
        func=dasf_mdp.commands_vel,
        params={
            "command_name": "base_velocity",
            "velocity_stages": [
                {
                    "step": 0,
                    "lin_vel_x": (-0.5, 0.6),
                    "lin_vel_y": (-0.5, 0.5),
                    "ang_vel_z": (-1.0, 1.0),
                },
                {
                    "step": 5000 * 24,
                    "lin_vel_x": (-0.5, 1.0),
                    "lin_vel_y": (-1.0, 1.0),
                },
            ],
        },
    )


@configclass
class DASF_TRON2A_EnvCfg(ManagerBasedRLEnvCfg):
    """Independent 20-DoF DASF_TRON2A locomotion environment."""

    scene: DASF_TRON2A_SceneCfg = DASF_TRON2A_SceneCfg(
        num_envs=4096, env_spacing=2.5
    )
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventsCfg = EventsCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        self.decimation = 4
        self.episode_length_s = 20.0
        self.sim.dt = 0.005
        self.sim.render_interval = self.decimation
        self.sim.physics_material = self.scene.terrain.physics_material
        self.sim.physx.gpu_max_rigid_patch_count = 10 * 2**15

        if self.scene.height_scanner is not None:
            self.scene.height_scanner.update_period = self.decimation * self.sim.dt
        if self.scene.contact_forces is not None:
            self.scene.contact_forces.update_period = self.sim.dt

