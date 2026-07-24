# Sprint 23 - Unified Curavias organisation refactoring

We need to extend the scope of the sprint 23 and align it with the new requirements we got as follows:
•	Based on the restriction of the MCAPS Tenant that does not allow to provisioning the sample users and details within Microsoft Entra, we need to establish a dedicated location to upload the master data extracts covering the full sample curavias master data (master-data) to load it on demand via Data Pipeline (Bronze, Silver Gold) into the gold tables in the datalake
•	Based on the gold tables we need to establish the Semantic Data Model and the Ontology model supporting the existing ontology model from a staff/person point of view, but also what kind of skills are required on the bed (Pflegepersonal) and ops (Doctors and Specialized Teams).
•	The Skills sources should use a similar pattern to get data from external sources as plugin architecture either real api based or simulated services
•	Key Skills based evidence we want to mimic (not real system is in place as of now) are SuccessFactors, LMS, and SkillsManager with Work-ID
•	Rest please evaluate the details from ideas\\unified-curavias-organisation-and-skills-ontology
Use superpower to update the existing sprint issue and documents and brainstorm how to refactor and build this sub-agent driven as dedicated parallel session stream. Please also cross check the patterns used in sprint 21 as well.





Details please review and incorporate everything in the subfolder \\unified-curavias-organisation-and-skills-ontology



