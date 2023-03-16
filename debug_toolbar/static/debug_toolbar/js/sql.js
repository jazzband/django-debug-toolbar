import DataTable from "./lib/dataTables.js";
import { $$ } from "./utils.js";

const djDebug = document.getElementById("djDebug");

// Insert the browser sql now since it's possible for this
// script to miss the initial panel load event.
const table = new DataTable(".sql-table", {
    columnDefs: [{ targets: [0, 1, 3, 5], orderable: false }],
});

$$.onPanelRender(djDebug, "SQLPanel", function () {
    new DataTable(".sql-table", {
        retrieve: true,
        columnDefs: [{ targets: [0, 1, 3, 5], orderable: false }],
    });
});
