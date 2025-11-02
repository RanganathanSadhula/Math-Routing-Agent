# Math-Routing-Agent
This document provides a final proposal and implementation code skeleton for the 'Math Routing Agent' assignment. The system is an Agentic-RAG (Retrieval-Augmented Generation) architecture designed to act like a mathematics professor: when given a math question it first checks a knowledge base, retrieves step-by-step solutions.

Math Routing Agent - Final Proposal & Implementation
Prepared for: Generative AI Assignment
Prepared by: Sadhula Ranganathan 


1.	Introduction
This document provides a final proposal and implementation code skeleton for the 'Math Routing Agent' assignment. The system is an Agentic-RAG (Retrieval-Augmented Generation) architecture designed to act like a mathematics professor: when given a math question it first checks a knowledge base, retrieves step-by-step solutions if present, otherwise performs a controlled web search (or MCP) and generates a clear, pedagogical step-by-step solution. The agent includes input/output guardrails and a human-in-the-loop feedback loop for continuous learning.

2.	Objectives
Build an Agentic RAG that prioritizes educational (mathematics) content. - Implement input/output guardrails to enforce privacy and restrict content. - Use a VectorDB-backed knowledge base (e.g., Qdrant) to store math Q&A.; - Fall back to a web search or Model Context Protocol (MCP) when KB miss occurs. - Integrate a human-in-the-loop feedback mechanism to refine answers over time. - Provide a FastAPI backend and code that can be extended to a React front-end.

3.	System Architecture Overview
High-level components: 
1. API Gateway / AI Gateway (Ingress) - applies input guardrails, routing policies.
2. Routing Agent - decides whether to query Knowledge Base or Web/MCP. 
3. Retrieval: VectorDB (Qdrant/Weaviate) + indexer (LlamaIndex or custom embeddings). 
4. Generator: LLM for step-by-step solution generation (with MCP/context handling). 
5. Feedback Agent: collects human feedback, verifies correctness, and triggers re-indexing or model fine-tuning steps. 6. Storage: Vector DB + relational store for metadata + feedback logs.

4.	Input & Output Guardrails (Privacy & Safety)
Input Guardrails: - Allow only educational math questions (block PII, personal data, harmful or unrelated prompts). - Enforce maximum context size; strip any uploaded files that contain PII before processing. - Rate-limit requests and authenticate clients (API keys / OAuth). Output Guardrails: - Enforce pedagogical style: always include step-by-step rationale and final answer. - Avoid hallucinations: require provenance when answer derived from web or KB (attach source links). - If no reliable source is found, respond with a safe fallback: ask for clarification or indicate "I could not verify this". Why this approach: - Education-focused guardrails reduce the chance of harmful or off-topic outputs. - Provenance and "I don't know" behaviors increase trust and reduce hallucination risk.

5.	Knowledge Base Creation
Dataset choice: - For math pedagogy, use curated problem-solution pairs. Options: * MATH dataset (competition math problems) for advanced problems. * JEE / JEEBench-style curated questions for Indian entrance exam coverage (recommended for bonus benchmarking). * Custom dataset: collection of textbook problems + step-by-step solutions. Storage: - Use Qdrant as VectorDB. Store embeddings (OpenAI or any embedding model) with metadata: difficulty, topic, canonical solution, LaTeX steps. Example KB queries to include in the deliverable: 
1) Solve: Integrate x * e^{x^2} dx. 
2) Solve: Find the limit: lim_{x->0} (sin x)/x. 
3) Solve: Prove that sequence a_n = 1/n converges to 0. If found in KB, return stored step-by-step solution; otherwise route to Web/MCP.
 

6.	Web Search / MCP Strategy
Use MCP (Model Context Protocol) to provide rich context when calling LLMs (include sources, provenance, and retrieval snippets). - For web search extraction: * Use a structured search client (Serper/Exa) to fetch candidate webpages and extract math content. * Prefer authoritative sources (wikipedia, arXiv, math.stackexchange, educational sites) and capture snippets, titles, and URLs. * Convert math content to a canonical LaTeX/markdown form before passing to the generator. Questions that should exercise web search (examples): 
1) Evaluate integral _0^ x^2 e^{-x} dx. (typical analytic solution online) 
2) Historical question: "Who proved the prime number theorem?" (requires web provenance) 
3) Advanced unsolved problem mention (should return 'not available' if unverifiable). MCP setup: - Send retrieval snippets as structured context blocks, each labeled with source and confidence. - Ask the LLM to explicitly reference which snippet(s) were used to generate the steps.

7.	Human-in-the-Loop Feedback Mechanism
Provide a feedback UI where a human (teacher/T.A.) can rate answers: Correct/Partially correct/Incorrect and provide corrections. - Feedback agent collects corrections and: * If minor, append corrected solution as alternate KB entry with higher weight. * If frequent errors on a topic, flag for retraining or prompt engineering adjustments. - Implement a review pipeline: sampled answers are periodically audited and used to create high-quality KB entries. - Optionally use DSPy for feedback orchestration to get bonus credit.

8.	Benchmarking with JEE Bench (Bonus)
If JEEBench dataset is available, run the retrieval+generation pipeline on held-out questions and compute metrics: * Exact answer accuracy, step-by-step quality score (human-rated), retrieval recall@k. - Provide a skeleton benchmark script (included below).

9.	Deliverables
PDF report (this document). - Source code (FastAPI + agent code) — skeleton included below; adapt and run locally. - Demo video (not provided here) — suggested content: architecture flowchart, live demo of sample queries showing KB hit & miss.
