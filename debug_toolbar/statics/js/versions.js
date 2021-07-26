import { $$ } from "./utils.js";

function pypiIndex() {
    
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
    function render(row, data) {
        let rowVersion = row.children.item(1);

        if (rowVersion.textContent != data.version) {
            row.classList.add("fastdt-pypi-outdated");
        }
        row.children.item(2).innerHTML =
            versionInfo(data.releases, data.version);

        rowVersion.innerHTML =
            versionInfo(data.releases, rowVersion.textContent);

        row.children.item(3).innerHTML = data.requires_python;

        row.children.item(4).innerHTML =
            data.status ? data.status.slice(26) : "";

        row.children.item(5).innerHTML = link(data.home_page);
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
        const name = row.firstElementChild.textContent.trim();
        const data = localStorage.getItem(`pypi-${name}`);

        if (data === null) {
            fetch(`https://pypi.org/pypi/${name}/json`)
                .then(function (response) {
                    if (response.ok) {
                        response.json().then(function (pypi) {
                            const data = getData(pypi);
                            localStorage.setItem(`pypi-${name}`, JSON.stringify(data));
                            render(row, data);
                        });
                    }
                });
        } else {
            render(row, JSON.parse(data));
        }
    }
    const loader = document
        .getElementById("VersionsPanel")
        .querySelector(".fastdt-loader");

    if (loader) {
        const table = loader.nextElementSibling;
        table.querySelectorAll("tbody > tr").forEach(row => updateRow(row));

        // TODO
        loader.remove();
        table.classList.remove("fastdt-hidden");
    }
}

const fastDebug = document.getElementById("fastDebug");
pypiIndex();
$$.onPanelRender(fastDebug, "VersionsPanel", pypiIndex);
