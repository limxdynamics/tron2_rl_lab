import copy
import os

import torch
import torch.nn as nn

from .actor_critic import ActorCritic


def export_normalized_policy_as_jit(actor_critic, path):
    """Export the DASF_TRON2A actor together with its running normalizer."""
    os.makedirs(path, exist_ok=True)
    path = os.path.join(path, "policy.pt")
    model = copy.deepcopy(actor_critic.get_inference_actor()).to("cpu")
    torch.jit.script(model).save(path)


class EmpiricalNormalizer(nn.Module):
    """Running mean and variance normalization with clipped outputs."""

    def __init__(self, input_dim, epsilon=1.0e-5, clip=10.0):
        super().__init__()
        self.epsilon = epsilon
        self.clip = clip
        self.register_buffer("mean", torch.zeros(input_dim))
        self.register_buffer("variance", torch.ones(input_dim))
        self.register_buffer("count", torch.tensor(0.0))

    @torch.no_grad()
    def update(self, observations):
        batch_mean = observations.mean(dim=0)
        batch_variance = observations.var(dim=0, unbiased=False)
        batch_count = observations.shape[0]
        if self.count == 0:
            self.mean.copy_(batch_mean)
            self.variance.copy_(batch_variance)
            self.count.fill_(batch_count)
            return

        delta = batch_mean - self.mean
        total_count = self.count + batch_count
        new_mean = self.mean + delta * batch_count / total_count
        current_m2 = self.variance * self.count
        batch_m2 = batch_variance * batch_count
        new_m2 = (
            current_m2
            + batch_m2
            + torch.square(delta) * self.count * batch_count / total_count
        )
        self.mean.copy_(new_mean)
        self.variance.copy_(new_m2 / total_count)
        self.count.copy_(total_count)

    def forward(self, observations):
        normalized = (observations - self.mean) / torch.sqrt(
            self.variance + self.epsilon
        )
        return torch.clamp(normalized, -self.clip, self.clip)


class EmpiricalNormalizedActorCritic(ActorCritic):
    """DASF_TRON2A actor-critic with independent actor and critic normalizers."""

    def __init__(self, num_actor_obs, num_critic_obs, num_actions, **kwargs):
        super().__init__(num_actor_obs, num_critic_obs, num_actions, **kwargs)
        self.actor_obs_normalizer = EmpiricalNormalizer(num_actor_obs)
        self.critic_obs_normalizer = EmpiricalNormalizer(num_critic_obs)

    def update_actor_normalization(self, observations):
        self.actor_obs_normalizer.update(observations)

    def update_critic_normalization(self, observations):
        self.critic_obs_normalizer.update(observations)

    def update_distribution(self, observations):
        super().update_distribution(self.actor_obs_normalizer(observations))

    def act_inference(self, observations):
        return self.actor(self.actor_obs_normalizer(observations))

    def evaluate(self, critic_observations, **kwargs):
        return self.critic(self.critic_obs_normalizer(critic_observations))

    def get_inference_actor(self):
        return nn.Sequential(self.actor_obs_normalizer, self.actor)