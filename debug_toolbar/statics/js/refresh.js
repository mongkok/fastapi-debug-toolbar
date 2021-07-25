(function(JSON) {
    const parse = JSON.parse;

    JSON.parse = function(text) {
        let data = parse(text);

        if (data === null || !data.hasOwnProperty("debugToolbar")) return data;

        Object.entries(data.debugToolbar.panels).map(([id, panel]) => {
            if (panel.subtitle) {
                document
                    .getElementById(`fastdt-${id}`)
                    .querySelector("small").textContent = panel.subtitle;
            }
            const panelContent = document.getElementById(id);
            panelContent.querySelector("h3").textContent = panel.title;

            let panelScroll = panelContent.querySelector(".fastdt-scroll");
            panelScroll.innerHTML = "";

            if (panelScroll.parentNode.querySelector(".fastdt-loader") === null) {
                let loader = document.createElement("div");
                loader.className = "fastdt-loader";
                panelScroll.parentNode.prepend(loader);
            }
        });
        document
            .getElementById("fastDebug")
            .setAttribute("data-store-id", data.debugToolbar.storeId);

        delete data.debugToolbar;
        return data;
    }
})(JSON);
