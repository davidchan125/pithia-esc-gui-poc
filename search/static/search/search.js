function getEnclosingLiNode(checkbox) {
    let currentParentNode = checkbox;
    let currentChildNode = checkbox;
    while (currentParentNode !== null && currentParentNode.nodeName !== "LI") {
        currentParentNode = currentChildNode.parentNode;
        currentChildNode = currentParentNode;
    }
    return currentParentNode;
}

function updateParentNodeCheckboxes(childNodeCheckbox) {
    const siblingNodeCheckboxes = document.querySelectorAll(`input[data-parent-node-in-ontology='${childNodeCheckbox.dataset.parentNodeInOntology}']`);
    const siblingNodeCheckboxesChecked = document.querySelectorAll(`input[data-parent-node-in-ontology='${childNodeCheckbox.dataset.parentNodeInOntology}']:checked`);
    const parentNodeCheckbox = document.getElementById(childNodeCheckbox.dataset.parentNodeInOntology);
    parentNodeCheckbox.checked = siblingNodeCheckboxes.length === siblingNodeCheckboxesChecked.length;
    if (parentNodeCheckbox.dataset.parentNodeInOntology !== "") {
        updateParentNodeCheckboxes(parentNodeCheckbox);
    }
}

function updateChildNodeCheckboxes(parentNodeCheckbox) {
    const childNodeCheckboxes = document.querySelectorAll(`input[data-parent-node-in-ontology='${parentNodeCheckbox.id}']`);
    const enclosingLiNode = getEnclosingLiNode(parentNodeCheckbox);
    const childDetailsNodes = enclosingLiNode.querySelectorAll("details");
    childDetailsNodes.forEach(detailsNode => {
        detailsNode.open = true;
    });
    childNodeCheckboxes.forEach(checkbox => {
        checkbox.checked = parentNodeCheckbox.checked;
        const childNodeCheckboxesOfChildNodeCheckbox = document.querySelectorAll(`input[data-parent-node-in-ontology='${checkbox.id}']`);
        if (childNodeCheckboxesOfChildNodeCheckbox.length > 0) {
            updateChildNodeCheckboxes(checkbox);
        }
    })
}

function filterObservedPropertyCheckboxes(treeContainerId, selectedCheckboxes) {
    if (treeContainerId === "phenomenons-tree-container") {
        
    }
}

function setupCheckboxesForTreeContainer(treeContainerId) {
    const allCheckboxesForTree = document.querySelectorAll(`#${treeContainerId} input`);
    const ontologyParentNodeCheckboxesForTree = document.querySelectorAll(`#${treeContainerId} input[data-is-parent-node='true']`);
    const ontologyChildNodeCheckboxesForTree = document.querySelectorAll(`#${treeContainerId} input:not([data-parent-node-in-ontology=''])`);

    allCheckboxesForTree.forEach(checkbox => {
        checkbox.addEventListener("change", event => {
            filterObservedPropertyCheckboxes(treeContainerId, document.querySelectorAll(`#${treeContainerId}} input:checked`));
        });
    });

    ontologyParentNodeCheckboxesForTree.forEach(checkbox => {
        checkbox.addEventListener("change", event => {
            const childNodeCheckboxes = document.querySelectorAll(`input[data-parent-node-in-ontology='${checkbox.id}']`);
            if (childNodeCheckboxes.length > 0) {
                updateChildNodeCheckboxes(checkbox);
            }
        });
    });

    ontologyChildNodeCheckboxesForTree.forEach(checkbox => {
        checkbox.addEventListener("change", event => {
            updateParentNodeCheckboxes(checkbox);
        });
    });
}

async function parseResponseText(response) {
    return response.text();
}

function getTreeContainerIdFromHTML(html) {
    if (html.includes('name="measurands"')) {
        return "measurands-tree-container";
    } else if (html.includes('name="observed_properties"')) {
        return "observed-properties-tree-container";
    } else if (html.includes('name="phenomenons"')) {
        return "phenomenons-tree-container";
    } else if (html.includes('name="qualifiers"')) {
        return "qualifiers-tree-container";
    }
    return "unknown";
}

async function loadSearchFormComponent(html) {
    let treeContainerId = getTreeContainerIdFromHTML(html);
    if (treeContainerId === "unknown") {
        return;
    }
    setTimeout(async () => {
        document.getElementById(treeContainerId).innerHTML = html;
        setupCheckboxesForTreeContainer(treeContainerId);
        document.getElementById(treeContainerId).style.opacity = 1;
    }, 300);
    document.getElementById(treeContainerId).style.opacity = 0;
}

async function loadSearchFormComponents() {
    const fetchParams = { method: "GET" };

    fetch("/search/templates/form/component/measurand/", fetchParams)
        .then(parseResponseText)
        .then(loadSearchFormComponent)
        .catch (error => {
            console.error("Unable to load measurand checkboxes");
            console.error(error);
        });

    fetch("/search/templates/form/component/observedProperty/", fetchParams)
        .then(parseResponseText)
        .then(loadSearchFormComponent)
        .catch (error => {
            console.error("Unable to load observed property checkboxes");
            console.error(error);
        });

    fetch("/search/templates/form/component/phenomenon/", fetchParams)
        .then(parseResponseText)
        .then(loadSearchFormComponent)
        .catch (error => {
            console.error("Unable to load phenomenon checkboxes");
            console.error(error);
        });

    fetch("/search/templates/form/component/qualifier/", fetchParams)
        .then(parseResponseText)
        .then(loadSearchFormComponent)
        .catch (error => {
            console.error("Unable to load qualifier checkboxes");
            console.error(error);
        });
}

document.getElementById("search-script").addEventListener("load", async event => {
    await loadSearchFormComponents();
});