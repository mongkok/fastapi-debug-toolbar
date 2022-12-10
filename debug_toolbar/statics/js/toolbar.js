import { $$, ajax } from "./utils.js";

function onKeyDown(event) {
  if (event.keyCode === 27) {
    fastdt.hide_one_level();
  }
}

const fastdt = {
  handleDragged: false,
  init() {
    const fastDebug = document.getElementById("fastDebug");
    $$.show(fastDebug);
    $$.on(document.getElementById("fastDebugPanelList"), "click", "li a", function (event) {
      event.preventDefault();
      if (!this.className) {
        return;
      }
      const panelId = this.className;
      const current = document.getElementById(panelId);
      if ($$.visible(current)) {
        fastdt.hide_panels();
      } else {
        fastdt.hide_panels();

        $$.show(current);
        this.parentElement.classList.add("fastdt-active");

        const inner = current.querySelector(".fastDebugPanelContent .fastdt-scroll"),
          store_id = fastDebug.dataset.storeId;
        if (store_id && inner.children.length === 0) {
          const url = new URL(fastDebug.dataset.renderPanelUrl, window.location);
          url.searchParams.append("store_id", store_id);
          url.searchParams.append("panel_id", panelId);
          ajax(url).then(function (data) {
            inner.previousElementSibling.remove(); // Remove AJAX loader
            inner.innerHTML = data.content;
            $$.executeScripts(data.scripts);
            $$.applyStyles(inner);
            $$.loadScripts(inner);
            fastDebug.dispatchEvent(
              new CustomEvent("fastdt.panel.render", {
                detail: { panelId: panelId },
              })
            );
          });
        } else {
          fastDebug.dispatchEvent(
            new CustomEvent("fastdt.panel.render", {
              detail: { panelId: panelId },
            })
          );
        }
      }
    });
    $$.on(fastDebug, "click", ".fastDebugClose", function () {
      fastdt.hide_one_level();
    });
    $$.on(fastDebug, "click", ".fastDebugPanelButton input[type=checkbox]", function () {
      fastdt.cookie.set(this.dataset.cookie, this.checked ? "on" : "off", {
        path: "/",
        expires: 10,
      });
    });

    // Used by the SQL and template panels
    $$.on(fastDebug, "click", ".remoteCall", function (event) {
      event.preventDefault();

      let url;
      const ajax_data = {};

      if (this.tagName === "BUTTON") {
        const form = this.closest("form");
        url = this.formAction;
        ajax_data.method = form.method.toUpperCase();
        ajax_data.body = new FormData(form);
      } else if (this.tagName === "A") {
        url = this.href;
      }

      ajax(url, ajax_data).then(function (data) {
        const win = document.getElementById("fastDebugWindow");
        win.innerHTML = data.content;
        $$.show(win);
      });
    });

    // Used by the cache and SQL panels
    $$.on(fastDebug, "click", ".fastToggleSwitch", function () {
      const id = this.dataset.toggleId;
      const toggleOpen = "+";
      const toggleClose = "-";
      const open_me = this.textContent === toggleOpen;
      const name = this.dataset.toggleName;
      const container = document.getElementById(name + "_" + id);
      container.querySelectorAll(".fastDebugCollapsed").forEach(function (e) {
        $$.toggle(e, open_me);
      });
      container.querySelectorAll(".fastDebugUncollapsed").forEach(function (e) {
        $$.toggle(e, !open_me);
      });
      const self = this;
      this.closest(".fastDebugPanelContent")
        .querySelectorAll(".fastToggleDetails_" + id)
        .forEach(function (e) {
          if (open_me) {
            e.classList.add("fastSelected");
            e.classList.remove("fastUnselected");
            self.textContent = toggleClose;
          } else {
            e.classList.remove("fastSelected");
            e.classList.add("fastUnselected");
            self.textContent = toggleOpen;
          }
          const switch_ = e.querySelector(".fastToggleSwitch");
          if (switch_) {
            switch_.textContent = self.textContent;
          }
        });
    });

    document.getElementById("fastHideToolBarButton").addEventListener("click", function (event) {
      event.preventDefault();
      fastdt.hide_toolbar();
    });
    document.getElementById("fastShowToolBarButton").addEventListener("click", function () {
      if (!fastdt.handleDragged) {
        fastdt.show_toolbar();
      }
    });
    let startPageY, baseY;
    const handle = document.getElementById("fastDebugToolbarHandle");
    function onHandleMove(event) {
      // Chrome can send spurious mousemove events, so don't do anything unless the
      // cursor really moved.  Otherwise, it will be impossible to expand the toolbar
      // due to fastdt.handleDragged being set to true.
      if (fastdt.handleDragged || event.pageY !== startPageY) {
        let top = baseY + event.pageY;

        if (top < 0) {
          top = 0;
        } else if (top + handle.offsetHeight > window.innerHeight) {
          top = window.innerHeight - handle.offsetHeight;
        }

        handle.style.top = top + "px";
        fastdt.handleDragged = true;
      }
    }
    document.getElementById("fastShowToolBarButton").addEventListener("mousedown", function (event) {
      event.preventDefault();
      startPageY = event.pageY;
      baseY = handle.offsetTop - startPageY;
      document.addEventListener("mousemove", onHandleMove);
    });
    document.addEventListener("mouseup", function (event) {
      document.removeEventListener("mousemove", onHandleMove);
      if (fastdt.handleDragged) {
        event.preventDefault();
        localStorage.setItem("fastdt.top", handle.offsetTop);
        requestAnimationFrame(function () {
          fastdt.handleDragged = false;
        });
        fastdt.ensure_handle_visibility();
      }
    });
    const show = localStorage.getItem("fastdt.show") || fastDebug.dataset.defaultShow;
    if (show === "true") {
      fastdt.show_toolbar();
    } else {
      fastdt.hide_toolbar();
    }
  },
  hide_panels() {
    const fastDebug = document.getElementById("fastDebug");
    $$.hide(document.getElementById("fastDebugWindow"));
    fastDebug.querySelectorAll(".fastdt-panelContent").forEach(function (e) {
      $$.hide(e);
    });
    document.querySelectorAll("#fastDebugToolbar li").forEach(function (e) {
      e.classList.remove("fastdt-active");
    });
  },
  ensure_handle_visibility() {
    const handle = document.getElementById("fastDebugToolbarHandle");
    // set handle position
    const handleTop = Math.min(localStorage.getItem("fastdt.top") || 0, window.innerHeight - handle.offsetWidth);
    handle.style.top = handleTop + "px";
  },
  hide_toolbar() {
    fastdt.hide_panels();

    $$.hide(document.getElementById("fastDebugToolbar"));

    const handle = document.getElementById("fastDebugToolbarHandle");
    $$.show(handle);
    fastdt.ensure_handle_visibility();
    window.addEventListener("resize", fastdt.ensure_handle_visibility);
    document.removeEventListener("keydown", onKeyDown);

    localStorage.setItem("fastdt.show", "false");
  },
  hide_one_level() {
    const win = document.getElementById("fastDebugWindow");
    if ($$.visible(win)) {
      $$.hide(win);
    } else {
      const toolbar = document.getElementById("fastDebugToolbar");
      if (toolbar.querySelector("li.fastdt-active")) {
        fastdt.hide_panels();
      } else {
        fastdt.hide_toolbar();
      }
    }
  },
  show_toolbar() {
    document.addEventListener("keydown", onKeyDown);
    $$.hide(document.getElementById("fastDebugToolbarHandle"));
    $$.show(document.getElementById("fastDebugToolbar"));
    localStorage.setItem("fastdt.show", "true");
    window.removeEventListener("resize", fastdt.ensure_handle_visibility);
  },
  cookie: {
    set(key, value, options) {
      options = options || {};

      if (typeof options.expires === "number") {
        const days = options.expires,
          t = (options.expires = new Date());
        t.setDate(t.getDate() + days);
      }

      document.cookie = [
        encodeURIComponent(key) + "=" + String(value),
        options.expires ? "; expires=" + options.expires.toUTCString() : "",
        options.path ? "; path=" + options.path : "",
        options.domain ? "; domain=" + options.domain : "",
        options.secure ? "; secure" : "",
        "sameSite" in options ? "; sameSite=" + options.samesite : "; sameSite=Lax",
      ].join("");

      return value;
    },
  },
};
window.fastdt = {
  show_toolbar: fastdt.show_toolbar,
  hide_toolbar: fastdt.hide_toolbar,
  init: fastdt.init,
  close: fastdt.hide_one_level,
  cookie: fastdt.cookie,
};

if (document.readyState !== "loading") {
  fastdt.init();
} else {
  document.addEventListener("DOMContentLoaded", fastdt.init);
}
