import { $$, ajaxForm } from "./utils.js";

const djDebug = document.getElementById("djDebug");

$$.on(djDebug, "click", ".switchHistory", function (event) {
    event.preventDefault();
    const newStoreId = this.dataset.storeId;
    const tbody = this.closest("tbody");

    tbody
        .querySelector(".djdt-highlighted")
        .classList.remove("djdt-highlighted");
    this.closest("tr").classList.add("djdt-highlighted");

    ajaxForm(this).then(function (data) {
        djDebug.setAttribute("data-store-id", newStoreId);
        Object.keys(data).forEach(function (panelId) {
            if (djDebug.querySelector("#" + panelId)) {
                djDebug.querySelector("#" + panelId).outerHTML =
                    data[panelId].content;
                djDebug.querySelector("#djdt-" + panelId).outerHTML =
                    data[panelId].button;
            }
        });
    });
});

$$.on(djDebug, "click", ".refreshHistory", function (event) {
    event.preventDefault();
    const container = djDebug.querySelector("#djdtHistoryRequests");
    ajaxForm(this).then(function (data) {
        if (data.requests.constructor === Array) {
            data.requests.forEach(function (request) {
                if (
                    !container.querySelector(
                        '[data-store-id="' + request.id + '"]'
                    )
                ) {
                    container.innerHTML = request.content + container.innerHTML;
                }
            });
        }
    });
});
