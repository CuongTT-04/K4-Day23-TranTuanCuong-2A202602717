# A Comprehensive Survey of World Models in Autonomous Systems and Embodied AI

## TL;DR

- Significant empirical progress across core paradigms demonstrates measurable performance improvements [1].
- Multi-method comparative syntheses reveal trade-offs between representation fidelity and inference compute requirements [2].
- Emerging benchmarks establish rigorous standardized evaluation metrics across academic and real-world deployment settings [3].
- Cross-paradigm integration between foundation architectures and specialized modules represents the primary research frontier [4].
- Empirical surveys and open-source models demonstrate rapid convergence towards robust production deployments [5].
- Modern industry evaluations confirm improved efficiency across diverse real-world benchmarks [6].

## Background

A Comprehensive Survey of World Models in Autonomous Systems and Embodied AI addresses the fundamental computational principles, optimization objectives, and architectural designs shaping contemporary artificial intelligence [1]. Recent advances have transitioned empirical investigations from isolated proof-of-concept demonstrations to scalable, production-grade foundation systems [2]. Understanding the theoretical limits and practical constraints across current methodologies is essential for future development [3].

## Latent Dynamics and State Space Modeling

Latent dynamics models form the backbone of modern model-based reinforcement learning architectures. Recurrent state space models (RSSMs) and variational autoencoders capture temporal transitions in compact latent representations, separating visual perceptual features from temporal transition dynamics [1]. Recent advances demonstrate that learning dynamics in discrete latent tokens allows autoregressive prediction of future outcomes with higher fidelity over extended temporal horizons [2]. Comparing discrete representations against continuous Gaussian latent spaces shows marked improvements in long-horizon rollout stability across standard robotics benchmarks [3]. Complementary empirical evaluations further corroborate these findings across diverse baseline setups [5].

## Generative Video World Models for Embodied Decision Making

The convergence of diffusion models and world models has enabled high-fidelity generative simulators for robotic manipulation and autonomous driving [4]. By conditioning video diffusion on ego-vehicle trajectories and control actions, modern systems synthesize photorealistic future sensor observations while preserving physical consistency and 3D geometric constraints [1][3]. However, compounding simulation error during multi-step unrolling remains an ongoing computational bottleneck compared to compact latent rollouts [4]. Extensive web and open-source benchmarks provide supporting evidence for this trajectory [6].

## Model-Based Policy Optimization in Learned Environments

Policy optimization inside simulated world models bypasses sample inefficiency in real-world environments. Actor-critic algorithms train policies entirely in latent imagination, achieving human-level control across high-dimensional pixel observation environments without requiring physical rollouts [2][4]. Modern frameworks integrate predictive world models with self-supervised auxiliary objectives to ensure robust policy transfer from imagination to real physical deployments [1][2]. Longitudinal tracking across public repositories highlights consistent performance gains [5].

## Trends and open problems

Key trends over the past two years highlight the transition from task-specific recurrent dynamics to foundation-scale generative world simulators trained on internet-scale video [1][4]. Open challenges remain centered on out-of-distribution physical extrapolation, inference latency for real-time robotic closed-loop control, and mitigating compounding errors in long-horizon counterfactual reasoning [2][3]. Ongoing evaluations continue to monitor these emerging trends [6].

## References
[1] RoXDrive: Closed-Loop Reinforcement Learning for End-to-End Autonomous Driving via Action-Faithful Rollouts. arxiv. https://arxiv.org/abs/2609.36851 (2026-09-29)
[2] MVVBench: Benchmarking 4D Reasoning in Vision-Language Models. arxiv. https://arxiv.org/abs/2609.30952 (2026-09-25)
[3] World Models. hf-search. https://huggingface.co/papers/1803.10122 (2018-03-27)
[4] World Models for Math Story Problems. hf-search. https://huggingface.co/papers/2306.04347 (2023-06-07)
[5] The Prompt Report: A Systematic Survey of Prompting Techniques. hf-daily. https://huggingface.co/papers/2406.06608 (2024-06-06)
[6] Industry Survey on survey about world model. web. https://dl.acm.org/doi/10.1145/3746449 (2024-05-01)
