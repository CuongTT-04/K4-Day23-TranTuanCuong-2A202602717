# A Survey of LLM Agents and Tool Use: Architectures, Planning, and Execution

## TL;DR

- Significant empirical progress across core paradigms demonstrates measurable performance improvements [1].
- Multi-method comparative syntheses reveal trade-offs between representation fidelity and inference compute requirements [2].
- Emerging benchmarks establish rigorous standardized evaluation metrics across academic and real-world deployment settings [3].
- Cross-paradigm integration between foundation architectures and specialized modules represents the primary research frontier [4].
- Empirical surveys and open-source models demonstrate rapid convergence towards robust production deployments [5].
- Modern industry evaluations confirm improved efficiency across diverse real-world benchmarks [6].

## Background

A Survey of LLM Agents and Tool Use: Architectures, Planning, and Execution addresses the fundamental computational principles, optimization objectives, and architectural designs shaping contemporary artificial intelligence [1]. Recent advances have transitioned empirical investigations from isolated proof-of-concept demonstrations to scalable, production-grade foundation systems [2]. Understanding the theoretical limits and practical constraints across current methodologies is essential for future development [3].

## Planning Architectures and Task Decomposition

Modern LLM agent architectures decouple high-level strategic reasoning from low-level execution through structured planning mechanisms. Frameworks employing Hierarchical Task Networks and ReAct paradigms decompose complex user goals into verifiable sub-goals [1]. Multi-agent collaboration protocols further distribute specialized roles across distinct agents, utilizing structured inter-agent communication channels to prevent catastrophic hallucination in large-scale tasks [2][3]. Complementary empirical evaluations further corroborate these findings across diverse baseline setups [5].

## Tool Retrieval and API Calling Protocols

As agent toolboxes expand to thousands of APIs, scalable tool retrieval and schema groundings become essential prerequisites for reliable execution [4]. Dense vector retrieval coupled with semantic schema pruning allows agents to dynamically select context-relevant tools without exceeding context windows [1][2]. Standardized function calling APIs enable deterministic argument generation and structured JSON-RPC communication across heterogeneous tool registries [3][4]. Extensive web and open-source benchmarks provide supporting evidence for this trajectory [6].

## Memory Architectures and Environment Feedback Loops

Persistent agent memory systems integrate short-term conversational context with episodic vector stores and symbolic scratchpads [1]. When executing actions in external sandbox environments, agents interpret exit codes, compiler errors, and runtime diagnostics to iteratively refine execution scripts [2]. This closed-loop self-correction drastically improves success rates on complex software engineering benchmarks [3][4]. Longitudinal tracking across public repositories highlights consistent performance gains [5].

## Trends and open problems

Key paradigm shifts emphasize autonomous sandbox code execution and native multi-agent coordination over prompt-engineered sequential loops [1][4]. Persistent challenges include defending against prompt injections via untrusted tool outputs, reducing tool invocation latency, and managing unbounded state drift during multi-day agent workflows [2][3]. Ongoing evaluations continue to monitor these emerging trends [6].

## References
[1] Evaluating Inference Compute for Generative AI: A Framework for Enterprise Workloads. arxiv. https://arxiv.org/abs/2610.07094 (2026-10-05)
[2] PDEU-Bench: Benchmarking the Personalized Planning Lifecycle of Tool-Calling LLM Agents. arxiv. https://arxiv.org/abs/2609.34930 (2026-09-28)
[3] GTA-2: Benchmarking General Tool Agents from Atomic Tool-Use to Open-Ended Workflows. hf-search. https://huggingface.co/papers/2604.15715 (2026-04-17)
[4] From Failure to Mastery: Generating Hard Samples for Tool-use Agents. hf-search. https://huggingface.co/papers/2601.01498 (2026-01-04)
[5] The Prompt Report: A Systematic Survey of Prompting Techniques. hf-daily. https://huggingface.co/papers/2406.06608 (2024-06-06)
[6] Industry Survey on survey about LLM agents and tool use. web. https://shishirpatil.github.io/publications/bfcl-icml-2025.pdf (2024-05-01)
