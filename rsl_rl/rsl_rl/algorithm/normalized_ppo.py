import torch

from .ppo import PPO


class NormalizedPPO(PPO):
    """PPO rollout path that updates DASF_TRON2A actor and critic normalization."""

    def act(self, obs, obs_history, commands, critic_obs):
        critic_obs = torch.cat((critic_obs, commands), dim=-1)

        encoder_out = self.encoder.encode(obs_history)
        actor_obs = torch.cat((encoder_out, obs, commands), dim=-1)
        self.actor_critic.update_actor_normalization(actor_obs)
        self.transition.actions = self.actor_critic.act(actor_obs).detach()

        if self.critic_take_latent:
            critic_obs = torch.cat((critic_obs, encoder_out), dim=-1)
        self.actor_critic.update_critic_normalization(critic_obs)
        self.transition.values = self.actor_critic.evaluate(critic_obs).detach()

        self.transition.actions_log_prob = self.actor_critic.get_actions_log_prob(
            self.transition.actions
        ).detach()
        self.transition.action_mean = self.actor_critic.action_mean.detach()
        self.transition.action_sigma = self.actor_critic.action_std.detach()
        self.transition.observations = obs
        self.transition.critic_obs = critic_obs
        self.transition.observation_history = obs_history
        self.transition.commands = commands
        return self.transition.actions