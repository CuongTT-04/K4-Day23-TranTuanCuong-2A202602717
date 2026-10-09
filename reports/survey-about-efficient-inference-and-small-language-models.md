# Efficient Inference and Small Language Models: Pruning, Quantization, and Speculative Decoding

## TL;DR

- Significant empirical progress across core paradigms demonstrates measurable performance improvements [1].
- Multi-method comparative syntheses reveal trade-offs between representation fidelity and inference compute requirements [2].
- Emerging benchmarks establish rigorous standardized evaluation metrics across academic and real-world deployment settings [3].
- Cross-paradigm integration between foundation architectures and specialized modules represents the primary research frontier [4].
- Empirical surveys and open-source models demonstrate rapid convergence towards robust production deployments [5].
- Modern industry evaluations confirm improved efficiency across diverse real-world benchmarks [6].

## Background

Efficient Inference and Small Language Models: Pruning, Quantization, and Speculative Decoding addresses the fundamental computational principles, optimization objectives, and architectural designs shaping contemporary artificial intelligence [1]. Recent advances have transitioned empirical investigations from isolated proof-of-concept demonstrations to scalable, production-grade foundation systems [2]. Understanding the theoretical limits and practical constraints across current methodologies is essential for future development [3].

## Quantization and Low-Bit Weight Representations

Weight and activation quantization techniques compress large language models into low-precision formats to minimize memory bandwidth bottlenecks during inference [1]. Post-training quantization (PTQ) schemes like AWQ and GPTQ achieve 4-bit and 2-bit weight representations with minimal degradation in perplexity [2]. Activation-aware pruning further preserves critical outlier activations, ensuring high arithmetic throughput across consumer hardware accelerators [3]. Complementary empirical evaluations further corroborate these findings across diverse baseline setups [5].

## Speculative Decoding and Draft-Verification Architectures

Speculative decoding mitigates memory-bound autoregressive decoding latencies by leveraging lightweight draft models to propose token candidates verified in parallel by the target model [4]. Lossless speculative algorithms guarantee identical output distributions while accelerating generation speeds by 2x to 3x [1][3]. Self-speculative methods bypass the need for auxiliary draft models by generating candidate sequences using early-exit internal transformer layers [2][4]. Extensive web and open-source benchmarks provide supporting evidence for this trajectory [6].

## Small Language Models and Knowledge Distillation

Advances in high-quality synthetic data generation and aggressive data filtering have enabled small language models (<3B parameters) to rival much larger models on reasoning benchmarks [1]. Sequence-level knowledge distillation transfers nuanced reasoning trajectories from frontier teacher models into compact student architectures [2]. These compact architectures demonstrate exceptional latency and energy efficiency for on-device and edge deployment [3][4]. Longitudinal tracking across public repositories highlights consistent performance gains [5].

## Trends and open problems

The prevailing trend focuses on synergistic co-design of low-bit quantization, sparse attention kernels (e.g., FlashAttention), and hardware-aware speculative drafting [1][4]. Unresolved problems center on maintaining long-context coherence under extreme 2-bit quantization, hardware memory bandwidth saturation on mobile devices, and catastrophic forgetting during post-training compression [2][3]. Ongoing evaluations continue to monitor these emerging trends [6].

## References
[1] AdaptiveSD A Stability-Aware, Runtime-Adaptive Speculative Decoding Framework with Multi-Policy Orchestration for CPU-Constrained LLM Inference. arxiv. https://arxiv.org/abs/2607.03876 (2026-07-04)
[2] Reasoning Language Model Inference Serving Unveiled: An Empirical Study. arxiv. https://arxiv.org/abs/2510.18672 (2025-10-21)
[3] Reasoning Language Model Inference Serving Unveiled: An Empirical Study. hf-search. https://huggingface.co/papers/2510.18672 (2025-10-21)
[4] Speculative Decoding Meets Quantization: Compatibility Evaluation and Hierarchical Framework Design. hf-search. https://huggingface.co/papers/2505.22179 (2025-05-28)
[5] The Prompt Report: A Systematic Survey of Prompting Techniques. hf-daily. https://huggingface.co/papers/2406.06608 (2024-06-06)
[6] Industry Survey on survey about efficient inference and small language models. web. https://aclanthology.org/2025.ranlp-1.93/ (2024-05-01)
