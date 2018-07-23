(function ($) {
    $('#djDebug a.djDebugToggle').on('click', function(e) {
        e.preventDefault();
        $(this).parent().find('.djDebugCollapsed').toggle();
        $(this).parent().find('.djDebugUncollapsed').toggle();
    });
    djdt.applyStyle('background-color');
    djdt.applyStyle('left');
    djdt.applyStyle('width');
    
    function sortTable(table, col, reverse, head) {
		var tb = table.tBodies[0], // use `<tbody>` to ignore `<thead>` and `<tfoot>` rows
			tr = Array.prototype.slice.call(tb.rows, 0), // put rows into array
			expr = /sqlDetails/,
			tr_details = [],
			final_tr = [],
			i;
		reverse = -((+reverse) || -1);
		tr_copy = tr.slice(0);
		tr_copy.forEach(function(element, idx) {
			if(expr.test(element.id)) { // removing details row for soting.
				tr_details.push(tr_copy.splice(idx, 1)[0]);
			}
        });
        $(head).toggleClass("asc desc"); 
		tr_copy = tr_copy.sort(function (a, b) { // sort rows
			return reverse // `-1 *` if want opposite order
				* (a.cells[col].textContent.trim() // using `.textContent.trim()` for test
					.localeCompare(b.cells[col].textContent.trim())
					);
				});
		tr_copy.forEach(function(element, idx) {
			var match = tr_details.find(function(obj) {
				return obj.id.split("sqlDetails_")[1] === element.id.split("sqlMain_")[1];
			})
			if (match) {
				final_tr.push(element, match); // adding details and main row after soting.
			} 
		});
		for(i = 0; i < final_tr.length; ++i) tb.appendChild(final_tr[i]); // append each row in order
	}
	function hasClass(element, cls) {
		return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
	}
	function makeSortable(table, header_name) {
		var th = table.tHead, i;
		th && (th = th.rows[0]) && (th = th.cells);
		if (th) i = th.length;
        else return; // if no `<thead>` then do nothing
		while (--i >= 0) (function (i) {
			var dir = 1;
			if (hasClass(th[i], header_name)) { // adding sorting to time
				th[i].addEventListener('click', function () {
                    sortTable(table, i, (dir = 1 - dir), th[i]);
                });
                sortTable(table, i, (dir = 1 - dir), th[i]);
                $(th[i]).toggleClass("desc"); 
			}
		}(i));
	}
	function makeAllSortable(parent, header_name) {
		parent = parent || document.body;
		var t = parent.getElementsByTagName('table')[0];
		makeSortable(t, header_name);
	}
	makeAllSortable(document.getElementById("SQLPanel"), 'djdt-time');
})(djdt.jQuery);
