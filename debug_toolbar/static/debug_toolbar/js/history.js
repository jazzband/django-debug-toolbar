import { $$, ajaxForm, pluckData, replaceToolbarState } from "./utils.js";

const djDebug = document.getElementById("djDebug");

function difference(setA, setB) {
    const _difference = new Set(setA);
    for (const elem of setB) {
        _difference.delete(elem);
    }
    return _difference;
}

function switchHistory(newStoreId) {
    const formTarget = djDebug.querySelector(
        ".switchHistory[data-store-id='" + newStoreId + "']"
    );
    const tbody = formTarget.closest("tbody");

    const highlighted = tbody.querySelector(".djdt-highlighted");
    if (highlighted) {
        highlighted.classList.remove("djdt-highlighted");
    }
    formTarget.closest("tr").classList.add("djdt-highlighted");

    ajaxForm(formTarget).then(function (data) {
        if (Object.keys(data).length === 0) {
            const container = document.getElementById("djdtHistoryRequests");
            container.querySelector(
                'button[data-store-id="' + newStoreId + '"]'
            ).innerHTML = "Switch [EXPIRED]";
        }
        replaceToolbarState(newStoreId, data);
    });
}

function refreshHistory() {
    const formTarget = djDebug.querySelector(".refreshHistory");
    const container = document.getElementById("djdtHistoryRequests");
    const oldIds = new Set(
        pluckData(container.querySelectorAll("tr[data-store-id]"), "storeId")
    );

    return ajaxForm(formTarget)
        .then(function (data) {
            // Remove existing rows first then re-populate with new data
            container
                .querySelectorAll("tr[data-store-id]")
                .forEach(function (node) {
                    node.remove();
                });
            data.requests.forEach(function (request) {
                container.innerHTML = request.content + container.innerHTML;
            });
        })
        .then(function () {
            const allIds = new Set(
                pluckData(
                    container.querySelectorAll("tr[data-store-id]"),
                    "storeId"
                )
            );
            const newIds = difference(allIds, oldIds);
            const lastRequestId = newIds.values().next().value;
            return {
                allIds,
                newIds,
                lastRequestId,
            };
        });
}

$$.on(djDebug, "click", ".switchHistory", function (event) {
    event.preventDefault();
    switchHistory(this.dataset.storeId);
});

$$.on(djDebug, "click", ".refreshHistory", function (event) {
    event.preventDefault();
    refreshHistory();
});

window.djdt.refreshHistory = refreshHistory;
window.djdt.switchHistory = switchHistory;
