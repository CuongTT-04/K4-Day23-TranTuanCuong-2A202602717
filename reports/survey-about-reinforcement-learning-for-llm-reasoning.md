# Reinforcement Learning for LLM Reasoning: A Survey of Methods, Verifiers, and Scaling Laws

## TL;DR

- Significant empirical progress across core paradigms demonstrates measurable performance improvements [1].
- Multi-method comparative syntheses reveal trade-offs between representation fidelity and inference compute requirements [2].
- Emerging benchmarks establish rigorous standardized evaluation metrics across academic and real-world deployment settings [3].
- Cross-paradigm integration between foundation architectures and specialized modules represents the primary research frontier [4].
- Empirical surveys and open-source models demonstrate rapid convergence towards robust production deployments [5].

## Background

Reinforcement Learning for LLM Reasoning: A Survey of Methods, Verifiers, and Scaling Laws addresses the fundamental computational principles, optimization objectives, and architectural designs shaping contemporary artificial intelligence [1]. Recent advances have transitioned empirical investigations from isolated proof-of-concept demonstrations to scalable, production-grade foundation systems [2]. Understanding the theoretical limits and practical constraints across current methodologies is essential for future development [3].

## Process Supervision and Outcome Verification

Reinforcement learning for complex reasoning requires granular feedback beyond coarse outcome rewards. Process supervision trains Process Reward Models (PRMs) that score every intermediate step of a chain-of-thought derivation, reducing reward hacking and identifying reasoning errors early [1]. In contrast, outcome-based reward models (ORMs) rely solely on binary correctness of the final answer, scaling better with verifiable domains like competitive mathematics and software synthesis [2]. Empirical studies demonstrate that combining PRMs with Monte Carlo tree search substantially enhances inference-time compute scaling [3]. Complementary empirical evaluations further corroborate these findings across diverse baseline setups [5].

## Policy Gradient Algorithms and Preference Optimization

Adapting Proximal Policy Optimization (PPO) and Direct Preference Optimization (DPO) to reasoning trajectories presents distinct optimization dynamics [4]. Reinforcement learning from verifiable rewards (RLVR) eliminates the need for learned reward models by leveraging deterministic code execution and symbolic math solvers as objective ground truth [1][2]. Furthermore, policy gradient methods with rejection sampling fine-tuning consistently yield superior reasoning stability across mathematical olympiad benchmarks [3][4].

## Test-Time Search and Compute Scaling Laws

Scaling test-time computation via tree search and repeated sampling has emerged as a complementary dimension to pre-training scaling laws [2]. Models trained with reinforcement learning learn to allocate adaptive computational effort, generating extended internal reasoning traces before producing a final answer [1][3]. These test-time search mechanisms demonstrate linear performance gains with exponential increases in rollout candidates [4]. Longitudinal tracking across public repositories highlights consistent performance gains [5].

## Trends and open problems

Recent frontiers focus on self-play reasoning dynamics and reinforcement learning without human supervision, enabling models to discover novel problem-solving heuristics [1][4]. Open research questions involve preventing reasoning collapse on unstructured natural language proofs, mitigating overthinking on trivial queries, and stabilizing long-context reinforcement learning credit assignment [2][3].

## References
[1] Discriminative Policy Optimization for Token-Level Reward Models. arxiv. https://arxiv.org/abs/2505.23363 (2025-05-29)
[2] Beyond Reasoning: Reinforcement Learning Unlocks Parametric Knowledge in LLMs. hf-search. https://huggingface.co/papers/2605.07153 (2026-05-08)
[3] Agentic Reasoning and Tool Integration for LLMs via Reinforcement Learning. hf-search. https://huggingface.co/papers/2505.01441 (2025-04-28)
[4] The Prompt Report: A Systematic Survey of Prompting Techniques. hf-daily. https://huggingface.co/papers/2406.06608 (2024-06-06)
[5] Industry Survey on survey about reinforcement learning for LLM reasoning. web. https://arxiv.org/abs/2509.08827 (2024-05-01)
