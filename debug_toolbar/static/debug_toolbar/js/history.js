import { $$, ajaxForm } from "./utils.js";

const djDebug = document.getElementById("djDebug");

$$.on(djDebug, "click", ".switchHistory", function (event) {
    event.preventDefault();
    const newStoreId = this.dataset.storeId;
    const tbody = this.closest("tbody");

    const highlighted = tbody.querySelector(".djdt-highlighted");
    if (highlighted) {
        highlighted.classList.remove("djdt-highlighted");
    }
    this.closest("tr").classList.add("djdt-highlighted");

    ajaxForm(this).then(function (data) {
        djDebug.setAttribute("data-store-id", newStoreId);
        // Check if response is empty, it could be due to an expired store_id.
        if (Object.keys(data).length === 0) {
            const container = document.getElementById("djdtHistoryRequests");
            container.querySelector(
                'button[data-store-id="' + newStoreId + '"]'
            ).innerHTML = "Switch [EXPIRED]";
        } else {
            Object.keys(data).forEach(function (panelId) {
                const panel = document.getElementById(panelId);
                if (panel) {
                    panel.outerHTML = data[panelId].content;
                    document.getElementById("djdt-" + panelId).outerHTML =
                        data[panelId].button;
                }
            });
        }
    });
});

$$.on(djDebug, "click", ".refreshHistory", function (event) {
    event.preventDefault();
    const container = document.getElementById("djdtHistoryRequests");
    ajaxForm(this).then(function (data) {
        // Remove existing rows first then re-populate with new data
        container
            .querySelectorAll("tr[data-store-id]")
            .forEach(function (node) {
                node.remove();
            });
        data.requests.forEach(function (request) {
            container.innerHTML = request.content + container.innerHTML;
        });
    });
});
