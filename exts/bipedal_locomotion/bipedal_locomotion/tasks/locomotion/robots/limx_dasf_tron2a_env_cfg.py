from isaaclab.utils import configclass

from bipedal_locomotion.assets.config.dasf_tron2a_cfg import DASF_TRON2A_CFG
from bipedal_locomotion.tasks.locomotion.cfg.DASF_TRON2A.limx_base_env_cfg import (
    DASF_TRON2A_EnvCfg,
)


@configclass
class DASF_TRON2A_BaseEnvCfg(DASF_TRON2A_EnvCfg):
    """Base DASF_TRON2A environment with the robot asset wired into the scene."""

    def __post_init__(self):
        super().__post_init__()

        self.scene.robot = DASF_TRON2A_CFG.replace(
            prim_path="{ENV_REGEX_NS}/Robot"
        )

        self.viewer.origin_type = "env"


@configclass
class DASF_TRON2A_BaseEnvCfg_PLAY(DASF_TRON2A_BaseEnvCfg):
    """Deterministic play configuration."""

    def __post_init__(self):
        super().__post_init__()

        self.scene.num_envs = 32
        self.observations.policy.enable_corruption = False
        self.observations.obsHistory.enable_corruption = False

        # Keep only nominal physics during policy inspection.
        self.events.mass_inertia = None
        self.events.body_physics_material = None
        self.events.foot_friction = None
        self.events.encoder_bias = None
        self.events.actuator_gains = None
        self.events.base_com = None
        self.events.push_robot = None
        self.events.reset_base.params["velocity_range"] = {}
        self.events.reset_joints.params["position_range"] = (0.0, 0.0)
        self.curriculum.command_vel = None
        self.commands.base_velocity.ranges.lin_vel_x = (0.5, 1.0)
        self.commands.base_velocity.ranges.lin_vel_y = (-0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (-0.0, 0.0)


@configclass
class DASF_TRON2A_BlindFlatEnvCfg(DASF_TRON2A_BaseEnvCfg):
    """Flat-ground DASF_TRON2A training environment."""

    def __post_init__(self):
        super().__post_init__()
        self.scene.height_scanner = None
        self.observations.critic.height_scan = None


@configclass
class DASF_TRON2A_BlindFlatEnvCfg_PLAY(DASF_TRON2A_BaseEnvCfg_PLAY):
    """Flat-ground DASF_TRON2A play environment."""

    def __post_init__(self):
        super().__post_init__()
        self.scene.height_scanner = None
        self.observations.critic.height_scan = None
