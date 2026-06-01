# Case Study 26

## AI-Powered Patient Flow and Hospital Capacity Platform  

## for a Swiss Cantonal Hospital Provider (e.g. USZ or LUKS)

---

## Overview

| Category | Details |
| -------- | ------- |
| **Industry** | Healthcare (Acute) |
| **Geographic Context** | Switzerland |
| **Operating Model** | Single-provider deployment within a cantonal healthcare system (e.g. Canton Zürich or Luzern) |
| **Example Providers** | One dedicated provider per deployment, such as Universitätsspital Zürich (USZ) or Luzerner Kantonsspital (LUKS) |
| **Regulatory Context** | Swiss DSG · KVG/LAMal · Cantonal healthcare regulations |

---

## Business Challenge

A Swiss cantonal hospital provider such as **USZ** or **LUKS** faces:

- Bed occupancy levels frequently exceeding optimal thresholds, impacting emergency department throughput  
- Increasing emergency demand displacing elective procedures  
- Discharge delays due to fragmented handovers with external care partners:
  - Rehabilitation clinics  
  - Spitex (home care services)  
  - Insurer-linked coordination units  
- Emergency department (Notfall) performance below target levels  
- Limited real-time visibility across internal departments and external downstream partners  
- Clinical staff planning based primarily on historical patterns rather than real-time demand signals  

---

## Transformation Objective

Implement an AI-powered patient flow and capacity intelligence platform that:

- Predicts demand surges for a single hospital provider (site-level and specialty-level)  
- Optimises discharge coordination from the provider to downstream partners in the cantonal ecosystem  
- Improves emergency department performance (Notfall)  
- Provides end-to-end visibility from admission through discharge for that provider, including outbound transitions to post-acute care  

While ensuring compliance with:

- Swiss **DSG (Data Protection Act)**  
- Cantonal data governance frameworks  
- Healthcare interoperability standards  

---

## Azure Services

- Azure Health Data Services  
- Azure OpenAI  
- Azure Machine Learning  
- Microsoft Fabric  
- Power BI  
- Microsoft Purview  
- Dynamics 365 Customer Service  
- Azure Logic Apps  

---

## Expected Outcomes

- Improved emergency department performance and reduced waiting times  
- Reduction of discharge delays through better coordination with downstream care providers  
- Lower elective surgery cancellation rates  
- Optimised bed occupancy for the target provider (e.g. USZ or LUKS)  
- Increased operational transparency for hospital management  

---

## AI Infusion Point

- A **72-hour demand forecasting model** predicts emergency admissions by specialty and time window within the target provider
- A **discharge coordination AI** identifies patients approaching discharge readiness and triggers downstream care processes (e.g. Spitex, rehabilitation)  
- A **GenAI-powered bed management copilot** provides real-time capacity insights and recommendations for hospital operations teams  
- Integrated data platform (Microsoft Fabric) connects:
  - Internal provider systems (KIS, operations, planning)  
  - External cantonal ecosystem partners (as integration endpoints)  
  - Reporting and analytics tools (Power BI)  

---

## Positioning Statement (for Workshops)

> This solution is deployed for one Swiss cantonal hospital provider at a time, such as **USZ** or **LUKS**, operating within a decentralised, multi-stakeholder healthcare environment. By combining AI-driven demand forecasting, discharge optimisation, and operational copilots, the platform improves provider-level patient flow and capacity management while enabling structured coordination with external care partners.
