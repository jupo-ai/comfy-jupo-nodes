import { api } from "../../scripts/api.js";
import { $el } from "../../scripts/ui.js";

const author = "jupo";
const packageName = "jupoNodes";

export function _name(name) {
    return `${author}.${packageName}.${name}`;
}

export function _endpoint(part) {
    return `/${author}/${packageName}/${part}`;
}

const DEBUG = true;
export function debug(data) {
    if (DEBUG) {
        api.fetchApi(_endpoint("debug"), {
            method: "POST", 
            body: JSON.stringify(data)
        });
    }
}

export function loadCSS(file) {
    function __joinPath(...segment) {
        return segment.map(segment => segment.replace("/\/+$/", "")).join("/");
    }

    const thisFile = import.meta.url;
    const webDirectory = thisFile.slice(0, thisFile.lastIndexOf("/"));
    const url = __joinPath(webDirectory, file);

    $el("link", {
        parent: document.head, 
        rel: "stylesheet", 
        type: "text/css", 
        href: url.startsWith("http") ? url: getUrl(url), 
    });
}