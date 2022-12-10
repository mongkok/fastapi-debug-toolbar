const refresh = (function () {
  function getCookie(name) {
    const parts = `; ${document.cookie}`.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
  }
  let lastCookie = getCookie("dtRefresh");
  const fastDebug = document.getElementById("fastDebug");

  return function () {
    const dtCookie = getCookie("dtRefresh");

    if (dtCookie && dtCookie !== lastCookie) {
      lastCookie = dtCookie;
      const toolbar = JSON.parse(decodeURIComponent(lastCookie));

      Object.entries(toolbar.panels).map(([id, subtitle]) => {
        document.getElementById(`fastdt-${id}`).querySelector("small").textContent = subtitle;
      });
      fastDebug.querySelectorAll(".fastDebugPanelContent").forEach(function (e) {
        e.querySelector(".fastdt-scroll").innerHTML = "";

        if (e.querySelector(".fastdt-loader") === null) {
          const loader = document.createElement("div");
          loader.className = "fastdt-loader";
          e.prepend(loader);
        }
      });
      fastDebug.setAttribute("data-store-id", toolbar.storeId);
    }
  };
})();

window.setInterval(refresh, 100);
