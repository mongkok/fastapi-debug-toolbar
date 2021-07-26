const $$ = {
    on(root, eventName, selector, fn) {
        root.addEventListener(eventName, function (event) {
            const target = event.target.closest(selector);
            if (root.contains(target)) {
                fn.call(target, event);
            }
        });
    },
    onPanelRender(root, panelId, fn) {
        /*
        This is a helper function to attach a handler for a `fastdt.panel.render`
        event of a specific panel.

        root: The container element that the listener should be attached to.
        panelId: The Id of the panel.
        fn: A function to execute when the event is triggered.
         */
        root.addEventListener("fastdt.panel.render", function (event) {
            if (event.detail.panelId === panelId) {
                fn.call(event);
            }
        });
    },
    show(element) {
        element.classList.remove("fastdt-hidden");
    },
    hide(element) {
        element.classList.add("fastdt-hidden");
    },
    toggle(element, value) {
        if (value) {
            $$.show(element);
        } else {
            $$.hide(element);
        }
    },
    visible(element) {
        return !element.classList.contains("fastdt-hidden");
    },
    executeScripts(scripts) {
        scripts.forEach(function (script) {
            const el = document.createElement("script");
            el.type = "module";
            el.src = script;
            el.async = true;
            document.head.appendChild(el);
        });
    },
    applyStyles(container) {
        /*
         * Given a container element, apply styles set via data-fastdt-styles attribute.
         * The format is data-fastdt-styles="styleName1:value;styleName2:value2"
         * The style names should use the CSSStyleDeclaration camel cased names.
         */
        container
            .querySelectorAll("[data-fastdt-styles]")
            .forEach(function (element) {
                const styles = element.dataset.fastdtStyles || "";
                styles.split(";").forEach(function (styleText) {
                    const styleKeyPair = styleText.split(":");
                    if (styleKeyPair.length === 2) {
                        const name = styleKeyPair[0].trim();
                        const value = styleKeyPair[1].trim();
                        element.style[name] = value;
                    }
                });
            });
    },
    loadScripts(container) {
        container
            .querySelectorAll("script")
            .forEach(function (element) {
                const script = document.createElement("script");
                Array.from(element.attributes)
                    .forEach(attr => script.setAttribute(attr.name, attr.value));
                script.appendChild(document.createTextNode(element.innerHTML));
                element.parentNode.replaceChild(script, element);
        });
    },
    truncatechars(text, n) {
        return (text.length > n) ? `${text.slice(0, n)}...` : text;
    },
};

function ajax(url, init) {
    init = Object.assign({ credentials: "same-origin" }, init);
    return fetch(url, init)
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
            return Promise.reject(
                new Error(response.status + ": " + response.statusText)
            );
        })
        .catch(function (error) {
            const win = document.getElementById("fastDebugWindow");
            win.innerHTML = `
                <div class="fastDebugPanelTitle">
                    <button type="button" class="fastDebugClose">»</button>
                    <h3>${error.message}</h3>
                </div>`;
            $$.show(win);
            throw error;
        });
}

function ajaxForm(element) {
    const form = element.closest("form");
    const url = new URL(form.action);
    const formData = new FormData(form);
    for (const [name, value] of formData.entries()) {
        url.searchParams.append(name, value);
    }
    const ajaxData = {
        method: form.method.toUpperCase(),
    };
    return ajax(url, ajaxData);
}

export { $$, ajax, ajaxForm };
