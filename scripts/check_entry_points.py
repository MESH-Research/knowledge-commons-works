from importlib_metadata import entry_points, EntryPoint


def check_entry_points():
    print("Checking invenio_base.blueprints entry points:")
    for ep in entry_points(group="invenio_base.blueprints"):
        print(f"  - {ep.name}: {ep.value}")
        if ep.name in [
            "kcworks_views",
            "knowledge_commons_works_menu",
            "kcworks_stats_dashboard_view",
        ]:
            print(f"    Module: {ep.module}")
            print(f"    Attrs: {ep.attr}")
            try:
                loaded = ep.load()
                print(f"    Loaded successfully: {loaded}")
            except Exception as e:
                print(f"    Failed to load: {e}")

    print("\nChecking invenio_base.apps entry points:")
    for ep in entry_points(group="invenio_base.apps"):
        print(f"  - {ep.name}: {ep.value}")
        if ep.name == "kcworks":
            print(f"    Module: {ep.module}")
            print(f"    Attrs: {ep.attr}")
            try:
                loaded = ep.load()
                print(f"    Loaded successfully: {loaded}")
            except Exception as e:
                print(f"    Failed to load: {e}")

    print("\nChecking invenio_base.api_blueprints entry points:")
    for ep in entry_points(group="invenio_base.api_blueprints"):
        print(f"  - {ep.name}: {ep.value}")
        if ep.name == "kcworks_api":
            print(f"    Module: {ep.module}")
            print(f"    Attrs: {ep.attr}")
            try:
                loaded = ep.load()
                print(f"    Loaded successfully: {loaded}")
            except Exception as e:
                print(f"    Failed to load: {e}")


if __name__ == "__main__":
    check_entry_points()
