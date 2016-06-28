(function ($) {
    $.fn.djdtShow = function (duration, completeFn) {
        this.removeAttr('hidden').show(duration, completeFn);
        return this;
    };

    $.fn.djdtHide = function (duration, completeFn) {
        console.log(this);
        if (duration) {
            var self = this;
            this.hide(duration, function () {
                self.attr('hidden', 'hidden');
                if (completeFn) {
                    completeFn.bind(self)();
                }
            });
        } else {
            this.attr('hidden', 'hidden').hide();
        }
        return this;
    };
})(djdt.jQuery);
