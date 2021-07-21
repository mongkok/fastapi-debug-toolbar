import { $$, ajaxForm } from "./utils.js";

const fastDebug = document.getElementById("fastDebug");

$$.on(fastDebug, "click", ".switchHistory", function (event) {
    event.preventDefault();
    const newStoreId = this.dataset.storeId;
    const tbody = this.closest("tbody");

    tbody
        .querySelector(".fastdt-highlighted")
        .classList.remove("fastdt-highlighted");
    this.closest("tr").classList.add("fastdt-highlighted");

    ajaxForm(this).then(function (data) {
        fastDebug.setAttribute("data-store-id", newStoreId);
        Object.keys(data).forEach(function (panelId) {
            const panel = document.getElementById(panelId);
            if (panel) {
                panel.outerHTML = data[panelId].content;
                document.getElementById("fastdt-" + panelId).outerHTML =
                    data[panelId].button;
            }
        });
    });
});

$$.on(fastDebug, "click", ".refreshHistory", function (event) {
    event.preventDefault();
    const container = document.getElementById("fastdtHistoryRequests");
    ajaxForm(this).then(function (data) {
        data.requests.forEach(function (request) {
            if (
                !container.querySelector('[data-store-id="' + request.id + '"]')
            ) {
                container.innerHTML = request.content + container.innerHTML;
            }
        });
    });
});
