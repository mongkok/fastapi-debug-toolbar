(function(JSON) {
    const parse = JSON.parse;
    const fastDebug = document.getElementById("fastDebug");

    function getCookie(name) {
        const parts = `; ${document.cookie}`.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
    function deleteCookie(name) {
        document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
    }
    JSON.parse = function(text) {
        const data = parse(text);
        const cookie = getCookie("dtRefresh");

        if (!cookie) return data;

        deleteCookie("dtRefresh");
        const toolbar = parse(decodeURIComponent(cookie));

        Object.entries(toolbar.panels).map(([id, subtitle]) => {
            document
                .getElementById(`fastdt-${id}`)
                .querySelector("small").textContent = subtitle;
        });
        fastDebug.querySelectorAll('.fastDebugPanelContent').forEach(function (e) {
            e.querySelector(".fastdt-scroll").innerHTML = "";

            if (e.querySelector(".fastdt-loader") === null) {
                const loader = document.createElement("div");
                loader.className = "fastdt-loader";
                e.prepend(loader);
            }
        });
        fastDebug.setAttribute("data-store-id", toolbar.storeId);
        return data;
    }
})(JSON);
