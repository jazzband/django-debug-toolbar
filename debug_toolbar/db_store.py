from debug_toolbar import store
from debug_toolbar.models import PanelStore, ToolbarStore


class DBStore(store.BaseStore):
    @classmethod
    def ids(cls):
        return (
            ToolbarStore.objects.using("debug_toolbar")
            .values_list("key", flat=True)
            .order_by("created")
        )

    @classmethod
    def exists(cls, store_id):
        return ToolbarStore.objects.using("debug_toolbar").filter(key=store_id).exists()

    @classmethod
    def set(cls, store_id):
        _, created = ToolbarStore.objects.using("debug_toolbar").get_or_create(
            key=store_id
        )
        if (
            created
            and ToolbarStore.objects.using("debug_toolbar").all().count()
            > cls.config["RESULTS_CACHE_SIZE"]
        ):
            ToolbarStore.objects.using("debug_toolbar").earliest("created").delete()

    @classmethod
    def delete(cls, store_id):
        ToolbarStore.objects.using("debug_toolbar").filter(key=store_id).delete()

    @classmethod
    def save_panel(cls, store_id, panel_id, stats=None):
        toolbar, _ = ToolbarStore.objects.using("debug_toolbar").get_or_create(
            key=store_id
        )
        toolbar.panelstore_set.update_or_create(
            panel=panel_id, defaults={"data": store.serialize(stats)}
        )

    @classmethod
    def panel(cls, store_id, panel_id):
        panel = (
            PanelStore.objects.using("debug_toolbar")
            .filter(toolbar__key=store_id, panel=panel_id)
            .first()
        )
        return {} if not panel else store.deserialize(panel.data)
