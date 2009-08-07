import os
from optparse import make_option

from django.core.management.base import NoArgsCommand
from django.db.backends import util

# Optional sqlparse to make the SQL look pretty...
# http://code.google.com/p/python-sqlparse/
try:
    import sqlparse
except ImportError:
    sqlparse = None

class PrintQueryWrapper(util.CursorDebugWrapper):
    def execute(self, sql, params=()):
        try:
            return self.cursor.execute(sql, params)
        finally:
            raw_sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            if sqlparse:
                print sqlparse.format(raw_sql, reindent=True)
            else:
                print raw_sql
            print

util.CursorDebugWrapper = PrintQueryWrapper

# The rest is copy/paste from django/core/management/commands/shell.py

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--plain', action='store_true', dest='plain',
            help='Tells Django to use plain Python, not IPython.'),
    )
    help = "Runs a Python interactive interpreter. Tries to use IPython, if it's available."

    requires_model_validation = False

    def handle_noargs(self, **options):
        # XXX: (Temporary) workaround for ticket #1796: force early loading of all
        # models from installed apps.
        from django.db.models.loading import get_models
        loaded_models = get_models()

        use_plain = options.get('plain', False)

        try:
            if use_plain:
                # Don't bother loading IPython, because the user wants plain Python.
                raise ImportError
            import IPython
            # Explicitly pass an empty list as arguments, because otherwise IPython
            # would use sys.argv from this script.
            shell = IPython.Shell.IPShell(argv=[])
            shell.mainloop()
        except ImportError:
            import code
            # Set up a dictionary to serve as the environment for the shell, so
            # that tab completion works on objects that are imported at runtime.
            # See ticket 5082.
            imported_objects = {}
            try: # Try activating rlcompleter, because it's handy.
                import readline
            except ImportError:
                pass
            else:
                # We don't have to wrap the following import in a 'try', because
                # we already know 'readline' was imported successfully.
                import rlcompleter
                readline.set_completer(rlcompleter.Completer(imported_objects).complete)
                readline.parse_and_bind("tab:complete")

            # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
            # conventions and get $PYTHONSTARTUP first then import user.
            if not use_plain:
                pythonrc = os.environ.get("PYTHONSTARTUP")
                if pythonrc and os.path.isfile(pythonrc):
                    try:
                        execfile(pythonrc)
                    except NameError:
                        pass
                # This will import .pythonrc.py as a side-effect
                import user
            code.interact(local=imported_objects)
