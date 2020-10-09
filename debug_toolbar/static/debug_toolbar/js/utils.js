const $$ = {
    on(root, eventName, selector, fn) {
        root.addEventListener(eventName, function (event) {
            const target = event.target.closest(selector);
            if (root.contains(target)) {
                fn.call(target, event);
            }
        });
    },
    show(element) {
        element.classList.remove("djdt-hidden");
    },
    hide(element) {
        element.classList.add("djdt-hidden");
    },
    toggle(element, value) {
        if (value) {
            $$.show(element);
        } else {
            $$.hide(element);
        }
    },
    visible(element) {
        return !element.classList.contains("djdt-hidden");
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
            const win = document.getElementById("djDebugWindow");
            win.innerHTML =
                '<div class="djDebugPanelTitle"><button type="button" class="djDebugClose">»</button><h3>' +
                error.message +
                "</h3></div>";
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
