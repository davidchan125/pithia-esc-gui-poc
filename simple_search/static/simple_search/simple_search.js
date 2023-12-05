const simpleSearchForm = document.querySelector("#simple-search-form");
const simpleSearchFormSubmitButton = document.querySelector("#simple-search-form button[type='submit']");

window.addEventListener("unload", event => {
    simpleSearchFormSubmitButton.innerHTML = "Search";
});

simpleSearchForm.addEventListener("submit", event => {
    simpleSearchFormSubmitButton.innerHTML = `<div class="spinner-border spinner-border-sm text-light mx-3" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>`;
});

const popover = new bootstrap.Popover('.popover-simple-search-help', {
    trigger: 'focus'
});