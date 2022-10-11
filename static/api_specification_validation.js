import {
    enableSubmitButtonIfReady
} from "/static/is_file_upload_ready.js"

export let isApiSpecificationLinkValid = false;
export let isApiSpecificationInputAvailable = false;
export const apiExecutionMethodCheckbox = document.querySelector('input[type="checkbox"][name="interaction_methods"][value="api"]');
export const apiSpecificationUrlInput = document.querySelector("#id_api_specification_url");
const validationStatusList = document.querySelector(".api-specification-url-status-validation");
const apiSpecificationValidationUrl = JSON.parse(document.getElementById("api-specification-validation-url").textContent);
let userInputTimeout;

apiExecutionMethodCheckbox.addEventListener("change", event => {
    toggleApiSpecificationUrlTextInput(apiExecutionMethodCheckbox);
    if (apiExecutionMethodCheckbox.checked) {
        isApiSpecificationLinkValid = false;
        enableSubmitButtonIfReady();
        startOpenApiSpecificationUrlValidation();
    } else {
        enableSubmitButtonIfReady();
    }
});

apiSpecificationUrlInput.addEventListener("input", async event => {
    startOpenApiSpecificationUrlValidation();
    const url = apiSpecificationUrlInput.value;
    if (apiExecutionMethodCheckbox.checked && url.trim().length === 0) {
        isApiSpecificationLinkValid = false;
        enableSubmitButtonIfReady();
    }
});

export function toggleApiSpecificationUrlTextInput(apiExecutionMethodCheckbox) {
    if (apiExecutionMethodCheckbox.checked) {
        apiSpecificationUrlInput.disabled = false;
        apiSpecificationUrlInput.required = true;
    } else {
        apiSpecificationUrlInput.disabled = true;
        apiSpecificationUrlInput.required = false;
    }
}

export function startOpenApiSpecificationUrlValidation() {
    const url = apiSpecificationUrlInput.value;
    if (url.length === 0) {
        isValidationStatusListVisibile(false);
        enableSubmitButtonIfReady();
        return;
    }

    document.querySelector("button[type='submit']").disabled = true;
    displayValidatingSpinner(true);
    if (userInputTimeout !== undefined) {
        clearTimeout(userInputTimeout);
    }
    userInputTimeout = setTimeout(async () => {
        try {
            const validationResult = await sendOpenApiSpecificationUrlForValidation(url);
            const { valid, error, details } = validationResult;
            isApiSpecificationLinkValid = valid;
            displayValidLinkResult(validationResult);
            enableSubmitButtonIfReady();
        } catch (e) {
            console.log(e);
            displayValidLinkResult(false);
        }
    }, 500);
}

function isValidationStatusListVisibile(isVisible) {
    if (isVisible) {
        return validationStatusList.classList.remove("d-none");
    }
    return validationStatusList.classList.add("d-none");
}

function displayValidatingSpinner(isVisible) {
    isValidationStatusListVisibile(false);
    document.querySelector(".status-invalid-link").classList.add("d-none");
    if (isVisible === true) {
        document.querySelector(".status-validating-link").classList.remove("d-none");
    } else {
        document.querySelector(".status-validating-link").classList.add("d-none");
    }
}

function displayValidLinkResult(validationResult) {
    const { valid, error, details } = validationResult;
    isValidationStatusListVisibile(true);
    document.querySelector(".status-validating-link").classList.add("d-none");
    if (valid === true) {
        isValidationStatusListVisibile(false);
        document.querySelector(".status-invalid-link").classList.add("d-none");
    } else {
        document.querySelector(".status-invalid-link .status-details").classList.add("d-none");
        document.querySelector(".status-invalid-link").classList.remove("d-none");
        document.querySelector(".status-invalid-link .status-text").innerHTML = "An unexpected error occurred.";
        if (error) {
            document.querySelector(".status-invalid-link .status-text").innerHTML = error;
        }
        if (details) {
            document.querySelector(".status-invalid-link .status-details span").innerHTML = details;
            document.querySelector(".status-invalid-link .status-details").classList.remove("d-none");
        }
    }
}

async function sendOpenApiSpecificationUrlForValidation(url) {
    const formData = new FormData();
    const csrfMiddlewareToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
    formData.append("csrfmiddlewaretoken", csrfMiddlewareToken);
    formData.append("api_specification_url", url);
    const response = await fetch(apiSpecificationValidationUrl, {
        method: "POST",
        body: formData
    });
    return await response.json();
}

window.addEventListener("load", event => {
    isApiSpecificationInputAvailable = true;
});