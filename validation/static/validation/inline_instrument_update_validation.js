import {
    MetadataFileUpdate,
    MetadataFileUpdateValidator,
    MetadataUpdateValidationStatusUIController,
} from "/static/validation/inline_update_validation.js";
import {
    startValidationProcess,
} from "/static/validation/inline_metadata_file_validation.js";
const fileInput = document.querySelector("#id_files");

class InstrumentMetadataFileUpdate extends MetadataFileUpdate {
    constructor(xmlFileString, xmlFileName) {
        super(xmlFileString, xmlFileName);
        this.operationalModeUpdateErrors = undefined;
        this.operationalModeUpdateWarnings = undefined;
    }

    static async fromFile(xmlFile) {
        const xmlFileString = await xmlFile.text();
        return new InstrumentMetadataFileUpdate(xmlFileString, xmlFile.name);
    }

    get isOperationalModeValidationComplete() {
        if (this.operationalModeUpdateErrors === undefined) {
            return false;
        }
        return this.operationalModeUpdateErrors.length === 0;
    }

    get isEachOperationalModePresentFromLastVersion() {
        if (this.operationalModeUpdateWarnings === undefined) {
            return false;
        }
        return this.operationalModeUpdateWarnings.length === 0;
    }

    get isValid() {
        return [
            this.isSyntaxValid,
            this.isNamespaceValid,
            this.isLocalIDValid,
            this.isRootElementNameValid,
            this.isXSDValid,
            this.isEachMetadataReferenceValid,
            this.isEachOntologyReferenceValid,
            this.isUpdateValid,
            this.isOperationalModeValidationComplete,
        ].every(result => result === true);
    }

    get totalErrorCount() {
        return [
            this.syntaxErrors,
            this.namespaceErrors,
            this.localIDErrors,
            this.rootElementNameErrors,
            this.XSDErrors ? this.XSDErrors : [],
            this.metadataReferenceErrors ? this.metadataReferenceErrors : [],
            this.ontologyReferenceErrors ? this.ontologyReferenceErrors : [],
            this.updateErrors ? this.updateErrors : [],
            this.operationalModeUpdateErrors ? this.operationalModeUpdateErrors : [],
        ].flat().length;
    }

    getTotalWarningCount() {
        return (this.operationalModeUpdateWarnings ? this.operationalModeUpdateWarnings : []).length;
    }

    #addInstrumentUpdateValidationResults(results) {
        this.operationalModeUpdateErrors = results.operationalModeUpdateErrors;
        this.operationalModeUpdateWarnings = results.operationalModeUpdateWarnings;
    }

    addServerValidationResults(results) {
        this.addReferenceValidationResults(results);
        this.#addInstrumentUpdateValidationResults(results);
        this.addUpdateValidationResults(results);
    }
}

class InstrumentMetadataFileUpdateValidator extends MetadataFileUpdateValidator {
    async serverValidationFetchRequest(metadataFile) {
        const validationUrl = JSON.parse(document.getElementById("inline-validation-url").textContent);
        const existingMetadataId = JSON.parse(document.getElementById("resource-id").textContent);
        
        return fetch(`${validationUrl}?` + new URLSearchParams({
            xml_file_string: metadataFile.xmlFileString,
            xml_file_name: metadataFile.name,
            existing_metadata_id: existingMetadataId,
        }));
    }

    serverValidationErrorObject(errorMsg) {
        return {
            metadataReferenceErrors: [errorMsg],
            ontologyReferenceErrors: [errorMsg],
            updateErrors: [errorMsg],
            operationalModeUpdateErrors: [errorMsg],
            operationalModeUpdateWarnings: [errorMsg],
        };
    }

    serverValidationResultsObject(results) {
        return {
            metadataReferenceErrors: results.incorrectly_structured_url_errors
                                        .concat(results.unregistered_operational_mode_url_errors)
                                        .concat(results.unregistered_resource_url_errors),
            ontologyReferenceErrors: results.invalid_ontology_url_errors,
            updateErrors: results.xml_file_update_errors,
            operationalModeUpdateErrors: results.xml_file_op_mode_errors,
            operationalModeUpdateWarnings: results.xml_file_op_mode_warnings,
        };
    }
}

class InstrumentMetadataUpdateValidationStatusUIController extends MetadataUpdateValidationStatusUIController {
    #addInstrumentUpdateValidationStatusListItemForMetadataFile(metadataFile) {
        const statusList = document.querySelector(`.file-list-group-item-${metadataFile.id} .details-validation ul`);
        statusList.append(this.htmlToElement(`
            <li class="iuv-list-group-item py-2">
                <div class="text-secondary">
                    <div class="spinner-grow spinner-grow-sm me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>Validating operational modes
                </div>
            </li>
        `));
    }

    #addWarningValidationResultsForFile(warningText, warnings, selector) {
        const statusElem = document.querySelector(selector);
        let warningLisString = "";
        warnings.forEach(e => warningLisString += `<li>${e}</li>`);
        statusElem.innerHTML = `
        <details class="text-warning-emphasis">
            <summary>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-exclamation-triangle-fill me-2" viewBox="0 0 16 16">
                    <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5m.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2"/>
                </svg>${warningText}
            </summary>
            <div class="pt-2">
                <ul>
                    ${warningLisString}
                </ul>
            </div>
        </details>`;
    }

    addMetadataFileToValidationStatusList(metadataFile) {
        this.addGenericListItemForMetadataFile(metadataFile);
        this.#addInstrumentUpdateValidationStatusListItemForMetadataFile(metadataFile);
        this.addUpdateValidationStatusListItemForMetadataFile(metadataFile);
    }

    #updateInstrumentUpdateValidationResultsForFile(metadataFile) {
        const fileListGroupItemSelector = `.file-list-group-item-${metadataFile.id}`;
        const iuvSelector = `.iuv-list-group-item`;

        // Operational mode validation results
        // Check for errors first
        if (!metadataFile.isOperationalModeValidationComplete) {
            return this.addFailedValidationResultsForFile(
                "Failed operational mode validation.",
                metadataFile.operationalModeUpdateErrors,
                `${fileListGroupItemSelector} ${iuvSelector}`
            );
        } else if (!metadataFile.isEachOperationalModePresentFromLastVersion) {
            // If no errors, check for warnings
            // Add "addWarningValidationResultsForFile() method"
            return this.#addWarningValidationResultsForFile(
                "Some operational modes are missing in this update.",
                metadataFile.operationalModeUpdateWarnings,
                `${fileListGroupItemSelector} ${iuvSelector}`
            );
        }

        // Else, operational mode validation has passed.
        return this.addSuccessValidationResultsForFile(
            "Passed operational mode validation.",
            `${fileListGroupItemSelector} ${iuvSelector}`
        );
    }

    updateServerValidationResultsForFile(metadataFile) {
        this.updateReferenceValidationResultsForFile(metadataFile);
        this.updateUpdateValidationResultsForFile(metadataFile);
        this.#updateInstrumentUpdateValidationResultsForFile(metadataFile);
    }
}

export async function startInstrumentMetadataFileUpdateValidationProcess() {
    const files = Array.from(fileInput.files);
    const validator = new InstrumentMetadataFileUpdateValidator();

    const metadataFileListElem = document.querySelector(".file-validation-status-list");
    const validationStatusUIController = new InstrumentMetadataUpdateValidationStatusUIController(metadataFileListElem, fileInput);
    const newMetadataFileObjectFn = InstrumentMetadataFileUpdate.fromFile;

    return startValidationProcess(files, validator, validationStatusUIController, newMetadataFileObjectFn);
}