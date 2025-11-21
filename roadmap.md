PHASE 0 — Prep

Form Wyoming Holding Company (Nexus Integrated Holdings, LLC)
Form Texas Subsidiary (Compute Commons, LLC)

Secure pilot partner(s): World Foundation/Tools for Humanity, FWB, Ethereum, Arizona State University, FYI.
Define “merit criteria” v1.
Hardware Risk Mitigation: Begin validation of vendor-agnostic software stacks (e.g., ROCm, ZLUDA, Vulkan) to support diverse high-performance consumer hardware architectures and reduce single-vendor dependency.

Create a waitlist at https://computecommons.org

PHASE 1 — Proof-of-Concept Compute Portal

Build just enough to simulate subsidized compute access.

Features:
Login
GPU job launcher (simple UI + API)
Job queue
Usage dashboard
Subsidized tier with small free monthly allocation
Paywall for more usage
Billing via Stripe

No need for contribution scoring yet.
Use manual onboarding via “grant access if user is vouched for.”

PHASE 2 — Contribution Scoring (8–12 weeks)

Build:
Contribution profile
GitHub integration
Verify OSS commits
Verify issues, docs, PR reviews
Identity verification (GitHub + email minimum)
Scoring pipeline: contribution → compute credits
Abuse detection minimally (time-bound caps)


PHASE 3 — Paid Convenience & Scaling Features

Add:
priority queue
concurrency boost
persistent storage
snapshots
dataset cache
guaranteed job start
custom endpoints
multi-GPU jobs (8–16 GPUs)
basic enterprise features (org billing, SSO beta)
Federation Beta: Pilot integration of a single partner Nanopod into the Compute Portal. **Strictly focused on Batch Inference workloads to validate network latency constraints.**

PHASE 4 — Decentralized Funder Pools & Scaling

Add:
funder dashboard
Decentralized pool creation (e.g., “Open-Source Lab Pool: $100k” via smart contract)
allocation reporting
impact metrics
distribution logic
contributions → pool claims
frictionless renewals for funders
Federation V1: Implement a verified, non-custodial resource integration layer for new partner nodes (Federated Compute Model). **Rollout follows verification of the economic model in Phase 3.**

PHASE 5 — Decentralized Ecosystem & Governance Layer

Add:
marketplace for workflows, models, templates
revenue share
team collaboration
reproducible pipelines
“publish your workflow” button
build → train → deploy cycle
Governance Layer Formation: Establish on-chain governance for platform parameters and merit criteria, focusing on **utility and effective resource allocation** rather than speculative tokenomics.

PHASE 6 — Community Ownership & Utility
Focus: Finalize the transition to a fully decentralized, self-sustaining public utility.
Add:
Integration of Compute-backed **Utility Rights** (Tokens/NFTs) for resource access and collateral.
Migration of all core "Developer-access Plane" services (Identity, Billing, Policy Engine) to a Web3-native stack where possible.
Implementation of Zero-Knowledge (ZK) proofs for privacy-preserving reputation scoring and subsidy verification.
Finalize the transition to community ownership, ensuring the **"Merit" economy** remains the core driver of value.