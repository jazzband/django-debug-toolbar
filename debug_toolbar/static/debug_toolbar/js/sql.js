import { $$ } from "./utils.js";

function sortTable(sortIndex, order = "asc") {
    let rows, switching, i, x, y, shouldSwitch;
    const table = document.getElementsByClassName("sql-table")[0];
    switching = true;
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 1; i < rows.length - 1; i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[sortIndex];
            y = rows[i + 1].getElementsByTagName("TD")[sortIndex];
            // Check if the two rows should switch place:
            if (order === "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}

function onClickEventForSort(event) {
    const targetColumnId = event.target.id;
    if (targetColumnId !== "") {
        const [, sortIndex] = targetColumnId.split("-");
        if (event.target.classList.contains("asending")) {
            sortTable(sortIndex, "dsc");
            event.target.classList.add("desending");
            event.target.classList.remove("asending");
        } else {
            sortTable(sortIndex, "asc");
            event.target.classList.add("asending");
            event.target.classList.remove("desending");
        }
    }
}

function addSortEventListners() {
    document.querySelectorAll(".sort-icon").forEach((element) => {
        // MDN Docs:
        //: If a particular anonymous function is in the list of event listeners registered for a certain target,
        // and then later in the code, an identical anonymous function is given in an addEventListener call,
        // the second function will also be added to the list of event listeners for that target.
        element.addEventListener("click", onClickEventForSort);
    });
}
// Insert the addSortEventListners now since it's possible for this
// script to miss the initial panel load event. same as the explanation for timer.js
const djDebug = document.getElementById("djDebug");
addSortEventListners();
$$.onPanelRender(djDebug, "SQLPanel", addSortEventListners);
