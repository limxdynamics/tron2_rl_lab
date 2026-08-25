import math
import os

import isaaclab.sim as sim_utils
from isaaclab.assets.articulation import ArticulationCfg

from bipedal_locomotion.actuators import DelayedImplicitActuatorCfg


current_dir = os.path.dirname(__file__)
usd_path = os.path.join(current_dir, "../usd/DASF_TRON2A/usd/robot.usd")


DASF_TRON2A_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=usd_path,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            rigid_body_enabled=True,
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=10000.0,
            max_angular_velocity=10000.0,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True,
            solver_position_iteration_count=4,
            solver_velocity_iteration_count=0,
        ),
        activate_contact_sensors=True,
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        # The zero pose reaches the floor at a base height of about 0.726 m.
        pos=(0.0, 0.0, 0.73),
        joint_pos={
            # lower body -- DASF_TRON2A uses the URDF zero pose
            "proximal_pitch_[LR]_Joint": 0.0,
            "proximal_roll_[LR]_Joint": 0.0,
            "proximal_yaw_[LR]_Joint": 0.0,
            "knee_[LR]_Joint": 0.0,
            "ankle_pitch_[LR]_Joint": 0.0,
            # upper body -- user-provided walking pose
            "proximal_pitch_[LR]_U_Joint": 0.0,
            "proximal_roll_L_U_Joint": math.radians(165.0),
            "proximal_roll_R_U_Joint": math.radians(-165.0),
            "proximal_yaw_[LR]_U_Joint": 0.0,
            "elbow_[LR]_U_Joint": 0.0,
            "wrist_(yaw|pitch|roll)_[LR]_U_Joint": 0.0,
            "head_(yaw|pitch)_Joint": 0.0,
        },
        joint_vel={".*": 0.0},
    ),
    # The new +/-165 deg upper-roll defaults remain inside a 0.9-scaled
    # soft range and retain margin to the asymmetric URDF hard limits.
    # Keep the same soft-limit factor as the original SF task.
    soft_joint_pos_limit_factor=0.9,
    actuators={
        # Effort and velocity limits follow the DASF_TRON2A URDF. PD gains and
        # reflected inertias retain the corresponding SF_TRON2A motor model.
        "lower_heavy": DelayedImplicitActuatorCfg(
            joint_names_expr=[
                "proximal_pitch_[RL]_Joint",
                "proximal_roll_[RL]_Joint",
                "knee_[RL]_Joint",
            ],
            armature=0.161777558,
            effort_limit=140.0,
            velocity_limit=12.57,
            stiffness=159.67,
            damping=10.16,
            friction=0.0,
            min_delay=0,
            max_delay=4,
        ),
        "lower_light": DelayedImplicitActuatorCfg(
            joint_names_expr=[
                "proximal_yaw_[RL]_Joint",
                "ankle_pitch_[RL]_Joint",
            ],
            armature=0.053923687,
            effort_limit=60.0,
            velocity_limit=14.66,
            stiffness=53.22,
            damping=3.39,
            friction=0.0,
            min_delay=0,
            max_delay=4,
        ),
        "upper_pitch_roll": DelayedImplicitActuatorCfg(
            joint_names_expr=[
                "proximal_pitch_[RL]_U_Joint",
                "proximal_roll_[RL]_U_Joint",
            ],
            armature=0.161777558,
            effort_limit=140.0,
            velocity_limit=12.57,
            stiffness=159.67,
            damping=10.16,
            friction=0.0,
            min_delay=0,
            max_delay=4,
        ),
        "upper_yaw": DelayedImplicitActuatorCfg(
            joint_names_expr=["proximal_yaw_[RL]_U_Joint"],
            armature=0.053923687,
            effort_limit=60.0,
            velocity_limit=14.66,
            stiffness=53.22,
            damping=3.39,
            friction=0.0,
            min_delay=0,
            max_delay=4,
        ),
        "upper_elbow": DelayedImplicitActuatorCfg(
            joint_names_expr=["elbow_[RL]_U_Joint"],
            armature=0.053923687,
            effort_limit=60.0,
            velocity_limit=14.66,
            stiffness=53.22,
            damping=3.39,
            friction=0.0,
            min_delay=0,
            max_delay=4,
        ),
        "upper_wrist_head": DelayedImplicitActuatorCfg(
            joint_names_expr=[
                "wrist_(yaw|pitch|roll)_[RL]_U_Joint",
                "head_(yaw|pitch)_Joint",
            ],
            armature=0.053923687,
            effort_limit=20.0,
            velocity_limit=14.66,
            stiffness=53.22,
            damping=3.39,
            friction=0.0,
            min_delay=0,
            max_delay=4,
        ),
    },
)
