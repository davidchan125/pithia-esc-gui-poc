import {
    generateUniqueElemIdFromCurrentElemId,
    updateDuplicatedElemsWithIdsInContainer,
} from "/static/register_with_support/components/utils.js";


export class DynamicEditorTab {
    constructor(tabListSelector, tabContentSelector, tabPaneContentTemplateSelector, removeTabAndTabPaneButtonSelector, jsonExportElementSelector, tabButtonPrefixText = "Tab") {
        this.tabList = document.querySelector(tabListSelector);
        this.tabContent = document.querySelector(tabContentSelector);
        this.tabPaneContentTemplate = JSON.parse(document.querySelector(tabPaneContentTemplateSelector).textContent);
        this.removeTabAndTabPaneButtonSelector = removeTabAndTabPaneButtonSelector;
        this.jsonExportElement = document.querySelector(jsonExportElementSelector);
        this.tabButtonPrefixText = tabButtonPrefixText;
        this.createTabElement = this.tabList.querySelector(".create-tab");
        this.createTabButton = this.tabList.querySelector(".create-tab button");
        this.nextTabNumber = 2;
    }

    // Initial setup
    setup() {
        const firstTabPane = this.tabContent.querySelector(".tab-pane");
        this.loadPreviousTabData();
        this.setupTabPaneEventListeners(firstTabPane);
        this.createTabButton.addEventListener("click", () => {
            const newTabPane = this.createTabAndTabPane();
            this.createTabOnClickActions(newTabPane);
            this.exportTabData();
        });
    }

    // Utils
    getParentTabPaneOfChildNode(childNode) {
        const tabPanes = this.tabContent.querySelectorAll(".tab-pane");
        for (const tabPane of tabPanes) {
            if (tabPane.contains(childNode)) {
                return tabPane;
            }
        }
    }

    getTabButtonOfTabPane(tabPane) {
        const tabPaneLabelledBy = tabPane.getAttribute("aria-labelledby");
        const correspondingTabButton = document.getElementById(tabPaneLabelledBy);
        return correspondingTabButton;
    }

    // Helpers
    disableFirstRemoveTabAndTabPaneButtonIfOnlyOneTab() {
        const firstRemoveTabAndTabPaneButton = this.tabContent.querySelector(this.removeTabAndTabPaneButtonSelector);
        firstRemoveTabAndTabPaneButton.disabled = this.tabContent.querySelectorAll(".tab-pane").length === 1;
    }

    focusLastTabPane() {
        const tabs = this.tabList.querySelectorAll("button[aria-controls]");
        const lastTab = tabs[tabs.length - 1];
        lastTab.click();
    }

    switchToTabPaneContainingChildNode(childNode) {
        const containingTabPane = this.getParentTabPaneOfChildNode(childNode);
        const correspondingTabButton = this.getTabButtonOfTabPane(containingTabPane);
        correspondingTabButton.click();
    }

    // Tab removal
    removeTabAndTabPane(childNode) {
        const containingTabPane = this.getParentTabPaneOfChildNode(childNode);
        const correspondingTabButton = this.getTabButtonOfTabPane(containingTabPane)
        const containingTabListItem = correspondingTabButton.parentElement;
        this.tabContent.removeChild(containingTabPane);
        this.tabList.removeChild(containingTabListItem);
        this.disableFirstRemoveTabAndTabPaneButtonIfOnlyOneTab();
    }

    // Tab setup
    setupRemoveTabAndTabPaneButton(removeTabAndTabPaneButton) {
        removeTabAndTabPaneButton.addEventListener("click", e => {
            this.removeTabAndTabPane(e.currentTarget);
            this.exportTabData();
            this.focusLastTabPane();
        });
    }

    setupTabPaneEventListeners(tabPane) {
        const inputs = tabPane.querySelectorAll("input");
        const selects = tabPane.querySelectorAll("select");
    
        inputs.forEach(input => {
            input.addEventListener("invalid", e => {
                this.switchToTabPaneContainingChildNode(e.currentTarget);
            });
        });
    
        selects.forEach(select => {
            select.addEventListener("invalid", e => {
                this.switchToTabPaneContainingChildNode(e.currentTarget);
            });
        });
    
        const removeTabAndTabPaneButton = tabPane.querySelector(this.removeTabAndTabPaneButtonSelector);
        this.setupRemoveTabAndTabPaneButton(removeTabAndTabPaneButton);
    }

    createTabAndTabPane() {
        // New tab
        const newTab = document.createElement("LI");
        newTab.className = "nav-item";
        newTab.setAttribute("role", "presentation");
        
        // New tab button
        const newTabButton = document.createElement("BUTTON");
        const newTabIdPrefix = generateUniqueElemIdFromCurrentElemId(this.tabButtonPrefixText.toLowerCase().replace(/\s/g, ""));
        newTabButton.className = "nav-link";
        newTabButton.id = `${newTabIdPrefix}-tab`;
        newTabButton.dataset.bsToggle = "tab";
        newTabButton.dataset.bsTarget = `#${newTabIdPrefix}-tab-pane`;
        newTabButton.type = "button";
        newTabButton.role = "tab";
        newTabButton.setAttribute("aria-controls", `${newTabIdPrefix}-tab-pane`);
        newTabButton.innerHTML = `${this.tabButtonPrefixText} ${this.nextTabNumber}`;
    
        // Add new tab button to tab
        newTab.appendChild(newTabButton);
    
        // Append to current list
        this.tabList.insertBefore(newTab, this.createTabElement);
    
        // Create corresponding tab pane
        const newTabPane = this.createTabPane(newTabIdPrefix);
        this.setupTabPaneEventListeners(newTabPane);
        
        // Show the newly created tab
        this.focusLastTabPane();
    
        this.nextTabNumber += 1;

        return newTabPane;
    }

    createTabPane(newTabIdPrefix) {
        // Attributes
        const newTabPane = document.createElement("DIV");
        newTabPane.className = "tab-pane fade";
        newTabPane.id = `${newTabIdPrefix}-tab-pane`;
        newTabPane.setAttribute("role", "tabpanel");
        newTabPane.setAttribute("aria-labelledby", `${newTabIdPrefix}-tab`);
        newTabPane.setAttribute("tabindex", "0");
    
        // Content
        newTabPane.innerHTML = this.tabPaneContentTemplate;
        const elemsWithIds = newTabPane.querySelectorAll("[id]");
        updateDuplicatedElemsWithIdsInContainer(elemsWithIds, newTabPane);
    
        // Enable remove tab and tab pane button
        const removeTabAndTabPaneButton = newTabPane.querySelector(this.removeTabAndTabPaneButtonSelector);
        removeTabAndTabPaneButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash-fill me-2" viewBox="0 0 16 16">
            <path d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5M8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5m3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0"/>
        </svg>Remove ${this.tabButtonPrefixText} ${this.nextTabNumber}`;
        removeTabAndTabPaneButton.disabled = false;
    
        this.tabContent.appendChild(newTabPane);
    
        this.disableFirstRemoveTabAndTabPaneButtonIfOnlyOneTab();
    
        const selects = Array.from(newTabPane.querySelectorAll("select:not([multiple])"));
        const multipleChoiceSelects = Array.from(newTabPane.querySelectorAll("select[multiple]"));

        if (selects.length > 0) {
            window.dispatchEvent(new CustomEvent("newSelectsAdded", {
                detail: selects.map(select => select.id),
            }));
        }
        if (multipleChoiceSelects.length > 0) {
            window.dispatchEvent(new CustomEvent("newMultipleChoiceSelectsAdded", {
                detail: multipleChoiceSelects.map(select => select.id),
            }));
        }
    
        return newTabPane;
    }

    createTabOnClickActions() {
        // Can be customised in child class
    }

    // Tab data saving/loading
    getTabDataAsJson() {
        // Implemented in child class
    }

    exportTabData() {
        this.jsonExportElement.value = JSON.stringify(this.getTabDataAsJson());
    }

    loadPreviousTabData() { 
        // Implemented in child class
    }
}