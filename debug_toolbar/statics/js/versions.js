import { $$ } from "./utils.js";

function pypiIndex() {
    const loader = document
        .getElementById("VersionsPanel")
        .querySelector(".fastdt-loader");

    function versionInfo(releases, version) {
        return `
            <code>${version}</code>
            <span class="fast-date">
                ${new Date(releases[version]).toLocaleDateString()}
            </span>`;
    }
    function link(url) {
        return `
            <a href="${url}" target="_blank">
                ${$$.truncatechars(url, 40)}
            </a>`;
    }
    function render(rowVersion, data) {
        if (rowVersion.textContent !== data.version) {
            rowVersion.parentNode.style.backgroundColor =
                loader.nextElementSibling.dataset.warningColor;
        }
        if (data.releases[rowVersion.textContent] !== null) {
            rowVersion.innerHTML =
                versionInfo(data.releases, rowVersion.textContent);
        }
        const lastVersion = rowVersion.nextElementSibling;
        lastVersion.innerHTML = versionInfo(data.releases, data.version);

        const python = lastVersion.nextElementSibling;
        python.innerHTML = data.requires_python;

        const status = python.nextElementSibling;
        status.innerHTML = data.status ? data.status.slice(26) : "";
        status.nextElementSibling.innerHTML = link(data.home_page);
    }
    function getData(pypi) {
        return {
            version: pypi.info.version,
            requires_python: pypi.info.requires_python,
            home_page: pypi.info.home_page,
            releases: Object.fromEntries(
                Object.entries(pypi.releases).map(
                    function([k, v], i) {
                        return [k, v.length ? v[0].upload_time : null];
                    }
                )
            ),
            status: pypi.info.classifiers.find(
                function(classifier) {
                    return classifier.startsWith("Development Status");
                }
            )
        };
    }
    function updateRow(row) {
        return new Promise((resolve) => {
            const name = row.firstElementChild.textContent.trim();
            const data = JSON.parse(localStorage.getItem(`pypi-${name}`));
            const rowVersion = row.children.item(1);

            if (data === null || !(rowVersion.textContent in data.releases)) {
                fetch(`https://pypi.org/pypi/${name}/json`)
                    .then(function (response) {
                        if (response.ok) {
                            response.json().then(function (pypi) {
                                const data = getData(pypi);

                                if (!(rowVersion.textContent in data.releases)) {
                                    data.releases[rowVersion.textContent] = null;
                                }
                                localStorage.setItem(`pypi-${name}`, JSON.stringify(data));
                                render(rowVersion, data);
                                resolve();
                            });
                        }
                    });
            } else {
                render(rowVersion, data);
                resolve();
            }
        });
    }
    if (loader && !loader.getAttribute("lock")) {
        loader.setAttribute("lock", true);

        const table = loader.nextElementSibling;
        const queryResult = table.querySelectorAll("tbody > tr");
        const promises = [];

        for (let i = 0; i < queryResult.length; i++) {
            promises.push(updateRow(queryResult[i]));
        }
        Promise.all(promises).then(() => {
            loader.remove();
            table.classList.remove("fastdt-hidden");
        });
    }
}

const fastDebug = document.getElementById("fastDebug");
pypiIndex();
$$.onPanelRender(fastDebug, "VersionsPanel", pypiIndex);
