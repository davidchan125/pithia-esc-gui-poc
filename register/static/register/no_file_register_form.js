const inputSupportForm = document.getElementById("metadata-input-support-form");
const input = document.querySelector("#id_phone");

window.intlTelInput(input, {
    allowDropdown: false,
    autoPlaceholder: false,
    defaultToFirstCountry: false,
    nationalMode: false,
    placeholderNumberType: "FIXED_LINE",
    showFlags: false,
    utilsScript: "https://cdn.jsdelivr.net/npm/intl-tel-input@19.5.4/build/js/utils.js",
});

inputSupportForm.addEventListener("submit", () => {
    const localIdInput = document.querySelector("input[name='localid']");
    localIdInput.disabled = false;
});
