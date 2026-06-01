# SECURITY

| Field | Value |
| ----- | ----- |
| **Version** | 0.3.1 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 0.3.0 (Zero Trust baseline aligned to Swiss compliance) |

## Purpose

Define the security baseline for the Swiss Hospital Capacity Platform using a
Zero Trust pattern aligned to Microsoft security guidance and Swiss healthcare
compliance expectations.

This document provides:
- Security architecture pattern and mandatory controls.
- Mapping to requirement and compliance controls.
- Implementation guardrails for GA and IaC-first delivery.
- Evidence expectations for audit and release gates.

## Security Model

### Zero Trust Principles

The platform security model follows Microsoft Zero Trust principles:
1. Verify explicitly.
2. Use least privilege access.
3. Assume breach.

Security decisions are enforced across identity, network, workload,
application, data, and operations layers.

### Security Objectives

1. Keep PHI and sensitive operational data protected under Swiss processing
	constraints.
2. Reduce blast radius through segmentation, policy, and least privilege.
3. Maintain end-to-end traceability for security and compliance events.
4. Ensure security controls are deployable and auditable in Git-first workflows.

### Layered Security Pattern

| Layer | Zero Trust objective | Baseline controls |
| ----- | ----- | ----- |
| Identity | Verify explicitly | Microsoft Entra ID, Conditional Access, MFA, managed identities, Privileged Identity Management (PIM) |
| Network | Assume breach | Hub-spoke segmentation, private endpoints, deny-by-default NSG and firewall posture, controlled ingress and egress |
| Workload | Least privilege and integrity | Minimal RBAC scopes, hardened runtime baselines, patching, workload identity, policy conformance gates |
| Application | Confidentiality and integrity | Strong authn/authz boundaries, API authorization checks, secure session handling, OWASP controls |
| Data | Confidentiality and residency | Encryption in transit and at rest, key management in Key Vault, data classification and minimization, Swiss region enforcement for PHI |
| Operations | Detection and response | Centralized logging, alerting, incident runbooks, forensic retention, drift detection, release gates |

### Architecture-Specific Security Rules

1. PHI-sensitive services run only in Switzerland regions approved by policy.
2. PHI cross-region failover is default deny unless an approved compliance
	runbook exists.
3. AI inference for PHI uses only approved regional deployment modes.
4. Preview-only services are non-production for regulated data unless an
	explicit exception is approved.
5. All identities are workload or user identities; no embedded credentials.

## Identity and Access

### Mandatory Identity Controls

1. Human access uses Microsoft Entra ID with MFA and Conditional Access.
2. Administrative roles use PIM with just-in-time elevation and approval.
3. Workloads use managed identities; service principals are limited to CI/CD or
	integration edge cases with strict rotation.
4. RBAC assignments are least-privilege and environment-scoped.
5. Access reviews run on privileged roles and high-impact application roles.

### Identity Patterns By Persona

| Persona | Access model | Minimum control set |
| ----- | ----- | ----- |
| Operations user | Role-based app access | Entra group-based roles, Conditional Access, session logging |
| Security and platform admin | Privileged access | PIM JIT access, approval workflow, full activity logging |
| Application workload | Managed identity | Resource-scoped RBAC, no static secrets, token-based auth |
| Automation pipeline | Federated identity | OIDC workload federation, scoped permissions, audited deployments |

## Network and Platform Security

### Network Baseline

1. Use segmented hub-spoke architecture.
2. Use private endpoints for data and AI services handling sensitive data.
3. Use deny-by-default inbound and egress controls.
4. Restrict administration paths to approved secure channels.
5. Use DDoS, firewall, and network telemetry controls for critical ingress paths.

### Platform Guardrails

1. Use Azure Policy initiatives for baseline controls:
	encryption, diagnostics, approved regions, approved SKUs, and identity rules.
2. Block non-compliant resources at deployment time where possible.
3. Use policy-driven remediation for drift where safe.
4. Enforce GA-only production usage for regulated workloads.

## Secrets and Key Management

### Key Management Pattern

1. Store secrets, keys, and certificates in Azure Key Vault.
2. Access Key Vault through managed identity and RBAC.
3. Enforce key rotation schedules and certificate lifecycle monitoring.
4. Use customer-managed keys where required by policy.
5. Prohibit secrets in source code, local config files, or CI logs.

### Cryptography Baseline

1. Encrypt data at rest with platform encryption and, where required,
	customer-managed key controls.
2. Encrypt data in transit with modern TLS.
3. Maintain immutable or protected backups for critical recovery scope.

## Threat Detection and Response

### Detection Baseline

1. Centralize logs and metrics in a monitored workspace.
2. Enable threat detection coverage for compute, data, and identities.
3. Define severity-based alert routing and on-call ownership.
4. Monitor for anomalous access, privilege escalation, and data exfiltration.

### Incident Response Baseline

1. Maintain a security incident runbook with privacy-event decision logic.
2. Define containment steps for identity, network, and data compromise.
3. Define forensic evidence capture and retention requirements.
4. Perform regular incident exercises and track remediation outcomes.

## Swiss Regulatory Alignment

This security pattern supports the Swiss legal and control baseline defined in
`docs/COMPLIANCE.md`.

### Legal and Control Alignment

| Security area | Swiss compliance alignment | Internal control linkage |
| ----- | ----- | ----- |
| Identity and access governance | Supports lawful and controlled access to sensitive data | CH-C02, CH-C03, CH-C07 |
| Auditability and monitoring | Supports traceability and evidence expectations | CH-C03, CH-C10 |
| Residency and transfer control | Supports cross-border disclosure restrictions | CH-C05 |
| Incident response and breach handling | Supports breach handling and notification readiness | CH-C06 |
| Data minimization and protection | Supports privacy-by-design outcomes | CH-C01, CH-C02 |

## Requirement Traceability

| Requirement family | Security pattern contribution |
| ----- | ----- |
| FR-GOV-001 and FR-GOV-004 | Security evidence model, logging controls, and release-gate artifacts support auditable governance outputs |
| FR-GOV-002 and FR-GOV-005 | Identity, RBAC, and policy-driven integration boundary controls enforce secure access and partner exchange constraints |
| FR-GOV-006 | Provider-local identity and policy controls preserve local governance authority |
| NFR-SEC-001 | Least-privilege RBAC, managed identity, and JIT privileged access |
| NFR-SEC-002 | Centralized audit logging and privileged operation trails |
| NFR-SEC-003 | Authenticated and authorized integration endpoints with policy control |
| NFR-SEC-004 | Key Vault and credential-free workload pattern |
| NFR-COMP-001 to NFR-COMP-003 | Swiss legal alignment through Zero Trust controls and compliance mapping |
| NFR-COMP-004 and NFR-COMP-007 | Residency enforcement and default-deny transfer posture |
| NFR-COMP-005 and NFR-COMP-010 | Security evidence and data-governance artifacts support legal-basis and review-cadence requirements |
| NFR-COMP-006 | Security governance model supports accountable DSR operating boundaries |
| NFR-COMP-008 | Incident workflows and security evidence lifecycle |
| NFR-COMP-009 | Identity, access, and audit controls support EPR-aligned enforcement when EPR is enabled |
| NFR-AI-002 to NFR-AI-005 | Secure grounding, auditable AI response paths, and model-governance controls in AI architecture alignment |

## Coverage Validation

This validation cross-checks security coverage against requirements,
architecture, AI, and compliance baselines.

### Coverage Matrix

| Validation scope | Reference source | Security coverage status | Notes |
| ----- | ----- | ----- | ----- |
| Security NFRs | docs/PRD.md (`NFR-SEC-001` to `NFR-SEC-004`) | Covered | Explicitly mapped in Requirement Traceability section |
| Compliance NFRs (security-relevant) | docs/PRD.md (`NFR-COMP-001` to `NFR-COMP-010`) | Covered with operational dependencies | DSR, EPR, and transfer workflows require runbook implementation |
| Governance FRs (security-relevant) | docs/PRD.md (`FR-GOV-001`, `FR-GOV-002`, `FR-GOV-004`, `FR-GOV-005`, `FR-GOV-006`) | Covered | Traceability and policy controls are explicitly mapped |
| Architecture security directives | docs/ARCHITECTURE.md (Swiss regions, failover default-deny, GA-only controls) | Covered | Reflected in Architecture-Specific Security Rules |
| AI security and residency directives | docs/AI.md (PHI inference restrictions, audit metadata, governance lanes) | Covered | Reflected in AI inference, logging, and secrets controls |
| Compliance control set | docs/COMPLIANCE.md (`CH-C01` to `CH-C10`) | Covered with partial implementation items | All controls mapped at design level; some require operationalization |

### Residual Gaps (Implementation, Not Design Coverage)

The security pattern now covers all required control domains at design level.
The following items remain implementation tasks to reach operational completion:

1. Formal DSR operating process and ownership model (CH-C04).
2. Formal cross-border transfer risk assessment and legal sign-off workflow (CH-C05).
3. Privacy incident decision matrix and notification timers (CH-C06).
4. EPR technical conformance pack and test evidence model (CH-C07 and CH-C08).
5. Measurable AI override and safety acceptance criteria with recurring reporting (CH-C10).

### Validation Outcome

1. Security design coverage is complete against current PRD, architecture,
	AI, and compliance baselines.
2. Remaining work is execution and evidence automation, not additional security
	pattern definition.

## Delivery Pattern (GA and IaC)

### IaC-First Security Controls

The following controls are mandatory in infrastructure code:
1. Resource identity and access baseline.
2. Network segmentation and private endpoint posture.
3. Diagnostic settings and log routing.
4. Key Vault baseline and secret handling paths.
5. Azure Policy assignments for approved regions and security constraints.

### Operational Security Controls

The following controls require recurring operational workflows:
1. Access review and role recertification.
2. Incident response drills and post-incident remediation.
3. Threat hunting and alert tuning.
4. Compliance evidence review and release sign-off.

## Security Evidence Requirements

Minimum evidence required for release and audit:
1. RBAC and privileged access review report.
2. Policy compliance report for security and residency constraints.
3. Logging and alert coverage verification report.
4. Key and secret rotation status report.
5. Incident readiness checklist and latest exercise outcome.

## Microsoft Guidance References

1. Zero Trust security in Azure:
	https://learn.microsoft.com/azure/security/fundamentals/zero-trust
2. Azure Well-Architected security principles:
	https://learn.microsoft.com/azure/well-architected/security/principles
3. Cloud Adoption Framework, security Zero Trust in landing zones:
	https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/security-zero-trust
4. Azure network security best practices:
	https://learn.microsoft.com/azure/security/fundamentals/network-best-practices

## Next Steps

1. Add a policy-control matrix file under docs/security-governance with
	per-control owner and enforcement mode.
2. Add CI validation for required security policies and diagnostics.
3. Add a privacy and security incident runbook linked to CH-C06.
4. Add release checklist integration that requires security evidence artifacts.
