from mongodb import db

CurrentOrganisation = db['current-organisations']
CurrentIndividual = db['current-individuals']
CurrentProject = db['current-projects']
CurrentPlatform = db['current-platforms']
CurrentInstrument = db['current-instruments']
CurrentOperation = db['current-operations']
CurrentAcquisitionCapability = db['current-acquisition-capabilities']
CurrentAcquisition = db['current-acquisitions']
CurrentComputationCapability = db['current-computation-capabilities']
CurrentComputation = db['current-computations']
CurrentProcess = db['current-processes']
CurrentDataCollection = db['current-data-collections']

OrganisationRevision = db['organisation-revisions']
IndividualRevision = db['individual-revisions']
ProjectRevision = db['project-revisions']
PlatformRevision = db['platform-revisions']
InstrumentRevision = db['instrument-revisions']
OperationRevision = db['operation-revisions']
AcquisitionCapabilityRevision = db['acquisition-capability-revisions']
AcquisitionRevision = db['acquisition-revisions']
ComputationCapabilityRevision = db['computation-capability-revisions']
ComputationRevision = db['computation-revisions']
ProcessRevision = db['process-revisions']
DataCollectionRevision = db['data-collection-revisions']

OriginalMetadataXml = db['original-metadata-xmls']