// Sprint 12 — Entra demo org: SIT parameters.
//
// Users are shared across SIT and PROD (design spec D-6); only the redirect URIs
// and the friendly env tag differ between this file and prod.bicepparam.
// temporaryPassword is intentionally NOT set here — it is provided securely at
// apply time (az deployment sub create --parameters temporaryPassword=<value>)
// and must never be committed (T4 refusal rule).
using '../main.bicep'

param solutionShort = 'ihzhhpf'
param env = 'sit'
param spaRedirectUris = [
  'https://app-platform-ihzhhpf-sit.azurewebsites.net'
  'http://localhost:5173' // Sprint 13 dev
]
param personas = [
  {
    upn: 'dr.andrea.keller@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Dr. Andrea Keller'
    appRole: 'HCC.OperationsLead'
    defaultHospital: 'USZ'
    mailNickname: 'dr.andrea.keller'
  }
  {
    upn: 'markus.frei@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Markus Frei'
    appRole: 'HCC.BedManager'
    defaultHospital: 'USZ'
    mailNickname: 'markus.frei'
  }
  {
    upn: 'sandra.huber@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Sandra Huber'
    appRole: 'HCC.FlowManager'
    defaultHospital: 'USZ'
    mailNickname: 'sandra.huber'
  }
  {
    upn: 'thomas.brunner@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Dr. Thomas Brunner'
    appRole: 'HCC.EDLead'
    defaultHospital: 'USZ'
    mailNickname: 'thomas.brunner'
  }
  {
    upn: 'nicole.baumann@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Nicole Baumann'
    appRole: 'HCC.ORCoordinator'
    defaultHospital: 'USZ'
    mailNickname: 'nicole.baumann'
  }
  {
    upn: 'peter.schmid@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Peter Schmid'
    appRole: 'HCC.StaffingCoordinator'
    defaultHospital: 'USZ'
    mailNickname: 'peter.schmid'
  }
  {
    upn: 'claudia.steiner@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Claudia Steiner'
    appRole: 'HCC.DischargeCoordinator'
    defaultHospital: 'USZ'
    mailNickname: 'claudia.steiner'
  }
  {
    upn: 'michael.weber@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Dr. Michael Weber'
    appRole: 'HCC.CrisisManager'
    defaultHospital: 'USZ'
    mailNickname: 'michael.weber'
  }
  {
    upn: 'regula.bucher@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Dr. Regula Bucher'
    appRole: 'HCC.OperationsLead'
    defaultHospital: 'LUKS'
    mailNickname: 'regula.bucher'
  }
  {
    upn: 'stefan.zuend@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Stefan Zünd'
    appRole: 'HCC.BedManager'
    defaultHospital: 'LUKS'
    mailNickname: 'stefan.zuend'
  }
  {
    upn: 'martina.achermann@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Martina Achermann'
    appRole: 'HCC.DischargeCoordinator'
    defaultHospital: 'LUKS'
    mailNickname: 'martina.achermann'
  }
  {
    upn: 'daniel.kaufmann@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Daniel Kaufmann'
    appRole: 'HCC.ORCoordinator'
    defaultHospital: 'LUKS'
    mailNickname: 'daniel.kaufmann'
  }
  {
    upn: 'barbara.widmer@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Barbara Widmer'
    appRole: 'HCC.OperationsLead'
    defaultHospital: 'Zollikerberg'
    mailNickname: 'barbara.widmer'
  }
  {
    upn: 'lukas.frei@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Lukas Frei'
    appRole: 'HCC.FlowManager'
    defaultHospital: 'Zollikerberg'
    mailNickname: 'lukas.frei'
  }
  {
    upn: 'christoph.vogt@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Dr. Christoph Vogt'
    appRole: 'HCC.Executive'
    defaultHospital: 'Aggregated'
    mailNickname: 'christoph.vogt'
  }
  {
    upn: 'isabelle.girard@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Dr. Isabelle Girard'
    appRole: 'HCC.CantonalViewer'
    defaultHospital: 'Aggregated'
    mailNickname: 'isabelle.girard'
  }
  {
    upn: 'urs.ruegg@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Urs Rüegg'
    appRole: 'HCC.PlatformAdmin'
    defaultHospital: 'All'
    mailNickname: 'urs.ruegg'
  }
  {
    upn: 'elena.fischer@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Elena Fischer'
    appRole: 'HCC.OntologySteward'
    defaultHospital: 'All'
    mailNickname: 'elena.fischer'
  }
  {
    upn: 'rafael.moser@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Rafael Moser'
    appRole: 'HCC.AIGovernance'
    defaultHospital: 'All'
    mailNickname: 'rafael.moser'
  }
  {
    upn: 'sophie.meier@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Sophie Meier'
    appRole: 'HCC.DemoOperator'
    defaultHospital: 'All'
    mailNickname: 'sophie.meier'
  }
  {
    upn: 'hans.meier@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Hans Meier'
    appRole: 'HCC.Auditor'
    defaultHospital: 'All'
    mailNickname: 'hans.meier'
  }
  {
    upn: 'super.admin@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Super Admin'
    appRole: 'HCC.SuperAdmin'
    defaultHospital: 'All'
    mailNickname: 'super.admin'
  }
  {
    upn: 'demo.guest@mngenvmcap164444.onmicrosoft.com'
    displayName: 'Demo Guest'
    appRole: 'HCC.GuestReadOnly'
    defaultHospital: 'Aggregated'
    mailNickname: 'demo.guest'
  }
]
