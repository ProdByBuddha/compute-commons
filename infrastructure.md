SF Compute Architecture Overview
SF Compute provides a market for buying time on GPU clusters, offering both individual Virtual Machine nodes and multi-node Kubernetes clusters with InfiniBand. Their architecture focuses on providing flexible and scalable compute resources for AI workloads.


Here's a breakdown of how they accomplish their architecture:
Compute Offerings:
Virtual Machine Nodes: Users can buy reserved VM nodes with varying numbers of GPUs, duration, and start times. These nodes can be accessed via SSH.
InfiniBand Clusters: They offer interconnected Kubernetes clusters with InfiniBand, which provides high-speed communication between nodes, crucial for large-scale distributed workloads.
Hardware: SF Compute provides access to NVIDIA H100, H200, and AMD MI300/325X (coming soon) GPUs.
Cluster Management:
CLI and Dashboard: Users can interact with the platform through a command-line interface (CLI) or a web dashboard to buy and manage nodes and clusters.
Kubernetes: For cluster orchestration, they utilize Kubernetes (K3s or full K8s) along with NVIDIA GPU Operator, Node Feature Discovery, Prometheus, and Grafana.
Job Scheduling: They support various job schedulers like Slurm, Ray, or custom credit-based schedulers.
Parallel SSH: SF Compute has developed a Rust-based library called parallel_ssh for seamless cluster management and remote command execution across multiple nodes.
Networking:
High-speed Interconnect: Kubernetes clusters include a 3.2Tb/s InfiniBand fabric, enabling fast data transfer between nodes.
Top-of-rack switch: They use Mellanox / NVIDIA Spectrum SN2100 switches (100GbE or 200GbE).
NICs: ConnectX-6 100GbE NICs are used per node for both data and cluster planes.
Storage:
Local NVMe: For ephemeral workloads, they offer 8–10TB NVMe local storage per node.
Cluster Storage: For persistent data, they recommend 3x nodes running Ceph or MinIO, with each node having 30–60TB HDD plus NVMe cache. This enables multi-user persistent data, buckets, models, and user artifacts.
Power and Cooling:
Redundant PDUs: They use 2x 208V 30A PDUs with redundant A/B feeds.
Power Budget: They provide power budget estimates for different GPU node configurations, networking, and storage.
Infrastructure: They utilize 42U standard racks with cable management kits and optional fan trays.
Partnership with Modular: SF Compute has partnered with Modular to create a Large Scale Inference Batch API. This collaboration combines SF Compute's real-time spot market for GPUs with Modular's high-performance AI serving stack to provide cost-effective and high-throughput inference for large-scale offline tasks. This partnership aims to unify hardware and cloud platforms, abstracting physical infrastructure and enabling intelligent workload placement based on various factors including real-time market pricing.
In essence, SF Compute's architecture is designed to provide a flexible, high-performance, and cost-efficient platform for GPU-accelerated workloads, particularly for AI inference and training, through a combination of robust hardware, efficient cluster management, and strategic partnerships.
Personal Infrastructure Implementation
To mimic the SF Compute architecture within a local environment constrained by residential power limits, we have designed the "Nanopod" Node. This hardware configuration replicates the architectural topology of an SF Compute node—specifically the PCIe switching fabric, NVMe tiering, and RDMA networking capability—but is physically verified to run on a standard US 15A/120V residential circuit through strict component selection and software-defined power management.

The following components were selected to maximize architectural parity with the HGX/Superpod design while adhering to a ~1440W power envelope.

Category
Component
Specific Model
Role in Architecture
Est. Cost
Compute Core
CPU
High-Frequency HEDT Processor
(24+ Cores, High PCIe Lane Count)
The Control Plane
~$1,450
Fabric Board
Motherboard
Workstation Class E-ATX Board
(IPMI, Multi-PCIe 5.0 x16 Slots)
The Baseboard
~$1,299
Accelerators
GPUs
2x High-Memory Consumer GPUs
(24GB+ VRAM per card, Unified Memory Capable)
The Compute
~$3,600
Memory
RAM
128GB+ ECC DDR5 RDIMM
(Server-Grade Reliability)
Unified Memory
~$650
Interconnect
NIC
Dual-Port 100GbE SmartNIC
(RoCE/RDMA Support)
The InfiniBand
~$350 (Used)
Hot Storage
NVMe
2x 4TB High-Performance NVMe
Ephemeral Node Storage
~$600
Cold Storage
SSD
2x 20TB Enterprise HDDs
Cluster Storage
~$550
Cooling
CPU Cooler
High-Performance Air/Liquid Solution
Thermal Management
~$130
Power	PSU
PSU
High-Efficiency Tier 1 PSU
(1600W+, Titanium Rated)
Power Distribution
~$550
Chassis
Case
E-ATX Optimized Full Tower
The Rack
~$230
Total






~$9,409


Concurrent User Capacity and Cost-Benefit for Public Benefit
The Nanopod Node is architecturally capable of supporting approximately 5 to 20 concurrent developers for compute-intensive AI workloads. This capability is realized through:
VRAM Efficiency: The dual high-memory consumer GPUs provide ~48GB of unified VRAM, which is efficiently utilized for Large Language Model (LLM) inference by employing quantization techniques (e.g., 4-bit loading of 70B parameter models). This allows multiple, simultaneous inference sessions to share the core compute resource.
Decoupled Workload Management: The high-core count CPU serves as a robust control plane to run the "Developer-access Plane" software stack (e.g., Firecracker for sandboxing, Kubernetes for job orchestration). This decouples the overhead of user management, billing, and API gateway traffic from the GPU-accelerated compute, ensuring high, dedicated GPU utilization.
This high-throughput, low-cost singular server node offers a significant cost-benefit over traditional cloud compute. By providing a low-friction, subsidized compute allocation to multiple developers, the platform maximizes the potential for public benefit by:
Accelerating Open-Source Contributions: Granting fast, reliable access to high-end compute removes a major financial barrier for individual contributors to train, fine-tune, and deploy models, accelerating the pace of public-good AI research and development.
High Throughput per Dollar: The throughput realized from 5-20 concurrent users on a single residential-compatible server offers an orders-of-magnitude reduction in operational cost per "GPU-hour" compared to commercial cloud providers, enabling larger-scale, sustained compute allocation for non-profit and educational partners.

### Strategic Hardware Diversification & Risk Mitigation
**Risk Assessment:** The reliance on specific consumer-grade hardware vendors introduces significant "Supplier Power" risk regarding licensing terms and driver-level feature segmentation.
**Mitigation Strategy:** To ensure resilience against vendor lock-in and regulatory intervention, the roadmap prioritizes immediate validation of **Hardware Agnostic Middleware**. This includes integrating open compute stacks (e.g., ROCm, Vulkan, OpenCL) to support high-performance consumer accelerators from multiple vendors (such as AMD Radeon or Intel Arc series). This diversification prevents the platform from having a single point of failure in its supply chain while adhering to residential power and availability constraints.

Horizontal Expansion Strategy: The Federated Compute Model
The architecture is designed to be inherently scalable through horizontal expansion, moving beyond the single Nanopod unit to form a larger, decentralized network. This strategy focuses on both increasing the quality/quantity of compute available and enabling an ad-hoc, partner-driven supply chain:
Capacity Scaling (Quality & Quantity): The core Nanopod design serves as a verified, reproducible unit for scaling compute. The platform is engineered to integrate higher-quality hardware (e.g., more powerful GPUs, faster interconnects) or a higher quantity of standard Nanopods to increase the total pool of available compute resources, thus confidently serving a larger developer base.
Franchisable Compute Network: The most potent form of horizontal expansion is the adoption of a federated, ad-hoc partnership model. In this model, individual entities, non-profits, or other compute providers can become "partners" by independently building a verified compute node (like the Nanopod) which is financed, sponsored, or paid out-of-pocket by the partner.
Decentralized Bandwidth: Each partner node integrates into the larger network by pooling its resources on a shared Virtual Private Cloud (VPC) or Virtual Private Network (VPN). This decentralized approach rapidly increases the overall network bandwidth and available compute capacity without central capital expenditure, transforming each independent node into a fractional contributor to the platform's total power. 
**Technical Constraint:** Due to the inherent latency of VPN connections over public internet, Federated nodes are strictly designated for **Latency-Tolerant Workloads** (e.g., Batch Inference, Single-Node Fine-tuning). High-bandwidth, latency-sensitive workloads (such as large-scale distributed training) are routed exclusively to centralized, InfiniBand-connected clusters. This model positions the project as a compute vertical, offering a highly scalable, community-driven alternative to traditional cloud provider lock-in.

Developer-access Plane (The Platform):
API Gateway: Provides an entry point for developers to access their services.
Usage-tier System: Manages usage and billing.
Subsidy Verification Logic: Handles verification for subsidized credits.
Developer Identity + Reputation Scoring: Manages developer identities and reputations.
Runtime Sandboxing: Offers secure execution environments for jobs (e.g., Firecracker for microVMs with Daytona OSS serving as its control plane).
The "Developer-access Plane" is the most software-intensive part of the stack. Unlike hardware, where you buy off-the-shelf components, this layer requires integrating several open-source projects to create a cohesive platform.
Here is the open-source software stack that perfectly replicates SF Compute's "Developer-access Plane" capabilities.
1. The API Gateway (Entry Point)
Software: Apache APISIX
Role: The front door for all developer traffic. It handles rate limiting, authentication, and routing requests to your GPU clusters.
Why: It is cloud-native and high-performance (based on Nginx/OpenResty). Crucially, it has deep plugin support for AI Gateways, meaning it can route specific AI-inference requests (like OpenAI-compatible APIs) to specific GPU backends, just like SF Compute’s inference API.
2. Usage-tier System (Billing & Metering)
Software: Lago
Role: The "cash register" of your cloud. It tracks usage (e.g., "GPU-seconds used") and manages billing.
Why: Lago is the open-source standard for usage-based billing (the exact model of SF Compute). It handles:
Metering: Ingests events like gpu_active_time or bandwidth_used.
Plans: Lets you define "Spot Instances" vs. "On-Demand" pricing tiers.
Invoicing: Generates the bills sent to users.

3. Subsidy Verification Logic (Policy Engine)
Software: Open Policy Agent (OPA)
Role: The logic engine that decides who gets what.
How it works: You write "Policies as Code" (in Rego language) that intercept requests at the API Gateway.
Example Rule: "If User X has reputation_score > 50 AND subsidy_grant_active = true, then set billing_rate = 0."
Why: This decouples your business logic ("who gets free credits") from your infrastructure code.
4. Developer Identity + Reputation Scoring
Identity Software: Keycloak
Role: Manages user logins, API keys, and OAuth2 flows (Login with GitHub/Google).
Reputation Data Source: Gitcoin Passport
Role: The "Anti-Bot" and Reputation layer.
Why: We need to verify "subsidy" eligibility without manual review. Gitcoin Passport provides a "Sybil Resistance" score by checking if a user has a GitHub account older than X years, a LinkedIn profile, or an ENS domain.
Integration: You can gate your "Subsidy" tier behind a requirement: User must present a Gitcoin Passport with a score > 20.
Contribution Analytics: GrimoireLab
Role: If you want to score developers based on their open source contributions (e.g., "Give free compute hours to active PyTorch contributors"), GrimoireLab analyzes GitHub/GitLab activity to generate a "Developer Reputation" score.

5. Runtime Sandboxing (Secure Execution)
Software: Firecracker
Role: The virtualization technology that creates the "Virtual Machine Nodes."
Why: It creates microVMs in milliseconds. This is exactly what AWS Lambda and SF Compute use to ensure one user’s code cannot crash or spy on another user’s node, even on the same physical server.
Orchestration Layer: Daytona OSS
Role: The API that manages the Firecracker VMs for AI code.
Why: Firecracker is low-level. Daytona gives you a high-level API to "Spawn an AI Sandbox," "Upload Python Code," and "Get Results," effectively providing the "Runtime Sandboxing" service developer experience.
The "Glue": The Integrated Platform UI
To tie all of this into a "Marketplace" dashboard where users buy nodes:
Frontend: Paymenter (Recommended)
Role: The "Storefront" UI.
Why: It is an open-source hosting billing panel.[1] It integrates natively with Pterodactyl (game server panel), which can be repurposed to sell "GPU Containers" or "VMs" instead of Minecraft servers. It handles the "Buy Now" button, credit card processing, and provisions the server automatically.
Alternative Frontend: Backstage
Role: A pure "Developer Portal."
Why: If you want a more "Enterprise" look (less "Hosting Company," more "Cloud Platform"), you use Backstage. You would write a custom plugin that calls the Lago API to show usage and the Daytona API to spin up environments.