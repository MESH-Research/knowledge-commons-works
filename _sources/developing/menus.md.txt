# Menus (Flask-Menu)

KCWorks uses [Flask-Menu](https://github.com/inveniosoftware/flask-menu) to build navigation trees that Jinja2 templates render. Community header tabs, main navigation, and similar UI menus are all `MenuNode` instances registered at application startup and exposed to templates as `current_menu`.

This page documents the Flask-Menu `MenuNode` API and KCWorks-specific patterns for registering, customizing, filtering, and ordering community menu items.

## Accessing the menu

The Flask-Menu extension registers `current_menu` as a Jinja2 global. In Python code, import the same proxy:

```python
from flask_menu import current_menu
```

`current_menu` is the root `MenuNode`. Navigate the tree with dotted paths:

```python
communities = current_menu.submenu("communities")
members = current_menu.submenu("communities.members")
```

In templates:

```jinja
{% set items = current_menu.submenu('communities').children %}
```

`children` returns a **sorted list** of child `MenuNode` objects (sorted by each child's `order`). It is recomputed on every access; you cannot assign to it.

## Registering items in KCWorks

Extensions register menu items during `init` or `finalize_app`. KCWorks adds community header items in `site/kcworks/ext.py` (`register_community_menu_items`), which runs from `finalize_app` after other extensions have registered theirs.

```python
current_menu.submenu("communities").submenu("contribute").register(
    endpoint="invenio_app_rdm_records.deposit_create",
    text=_("Contribute"),
    order=70,
    endpoint_arguments_constructor=deposit_args,
    icon="plus",
    permissions="can_submit_record",
)
```

Stock Invenio community items (`requests`, `members`, `settings`, etc.) are registered in `invenio_communities.ext.register_menus`. The stats tab is registered by `invenio_stats_dashboard`.

Call `register()` on a submenu path to **create** a new item or **update** an existing one in place. You do not need to reassign the parent submenu.

## KCWorks community header pipeline

The community details header template (`templates/semantic-ui/invenio_communities/details/header.html`) does not render `.children` directly. It runs two KCWorks filters from `site/kcworks/templates/template_filters.py`:

1. **`sort_menu_items_by_name`** — reorders items by a hard-coded name list (`community_menu_order` in the template). Items not in that list are appended in their existing order.
2. **`filter_visible_community_menu_items`** — applies Flask-Menu visibility, permission checks, and KCWorks-specific gates (stats dashboard enabled, hide `search` when `home` exists, hide `submit`, etc.).

Because of step 1, changing `order` in `register()` or via `_order` mutation often **does not change the displayed tab order**. Update `community_menu_order` in the header template (or change the filter) when you care about display order.

## `MenuNode` reference

Flask-Menu defines a single entry type: `MenuNode` (`flask_menu.menu.MenuNode`). There is no separate `MenuItem` class.

### Identity and tree structure

| Member | Kind | Use |
|--------|------|-----|
| `name` | public attribute | Stable key for the node (e.g. `"members"`, `"stats"`). Used in `submenu("members")` and in KCWorks filters via `item.name`. |
| `parent` | public attribute | Parent `MenuNode`, or `None` for the root. |
| `_child_entries` | private attribute | `dict[str, MenuNode]` of child nodes keyed by name. Source of truth for the tree. |
| `children` | read-only property | Sorted list of child `MenuNode` objects, ordered by each child's `order`. |
| `submenu(path, auto_create=True)` | method | Navigate or create children. `"communities.members"` walks the tree; returns the target node. |
| `list_path(from_path, to_path)` | method | Returns the ancestor→descendant path as a list of nodes, or `None` if the paths are on unrelated branches. |

### Configuration (set via `register()`)

These values are stored on private fields. `register()` is the supported way to set them initially.

| Backing field | `register()` parameter | Use |
|---------------|------------------------|-----|
| `_endpoint` | `endpoint` | Flask endpoint name for `url_for(...)`. Mutually exclusive with `external_url`. |
| `_external_url` | `external_url` | Static URL when there is no endpoint. Used when `_endpoint` is unset. |
| `_text` | `text` | Label shown in templates (`item.text`). Defaults to `name` on register. |
| `_order` | `order` | Sort key for `children`. Lower values appear earlier. |
| `_expected_args` | `expected_args` | URL argument names (e.g. `["pid_value"]`) pulled from `g._menu_kwargs` when building `url`. |
| `_endpoint_arguments_constructor` | `endpoint_arguments_constructor` | Callable returning extra `url_for` keyword arguments. |
| `_dynamic_list_constructor` | `dynamic_list_constructor` | Callable returning a list of nodes to render instead of just `self` (for dynamic menu expansion). |
| `_visible_when` | `visible_when` | Callable; item is visible only if it returns a truthy value (and `_text` is set). Default: always visible. |
| `_active_when` | `active_when` | Callable deciding whether the item is "active". Default: match endpoint, path prefix, or exact path. |
| `**kwargs` | e.g. `icon`, `permissions` | Arbitrary extra attributes via `setattr`. Re-registering with a **different** value for an existing kwarg raises `RuntimeError`. |

### Read-only computed properties

These are what templates and filters usually read.

| Property | Use |
|----------|-----|
| `text` | Display label. Falls back to `"MenuNode item not initialised"` if `_text` is `None`. |
| `url` | Link target. Built from `endpoint` and arguments, or `external_url`, or `"#"`. |
| `order` | Exposes `_order` (getter only; no setter). |
| `visible` | `True` if `_text is not None` **and** `_visible_when()` is truthy. |
| `active` | `True` if `_active_when()` considers this item to match the current request. |
| `active_item` | Deepest active node in this subtree, or `self` if active, else `None`. |
| `dynamic_list` | Result of `_dynamic_list_constructor()`, or `[self]` if unset. |

### Methods

| Method | Use |
|--------|-----|
| `register(...)` | Configure or reconfigure a node. Updates backing fields in place. |
| `hide()` | Sets `_visible_when` to always-false so the item never shows. |
| `has_active_child(recursive=True)` | Whether any descendant is active. |
| `has_visible_child(recursive=True)` | Whether any descendant is visible. |

### Request-time URL building

Flask-Menu's extension stores the current route's view arguments on `g._menu_kwargs` during each request. When building `url`, only keys listed in `_expected_args` are passed to `url_for`. Community menu items therefore register `expected_args=["pid_value"]` so links include the current community slug.

### KCWorks-specific extra attributes

These are not part of Flask-Menu itself. They are set via `register(**kwargs)` and used by KCWorks templates and filters.

| Attribute | Use in KCWorks |
|-----------|----------------|
| `permissions` | Permission key checked in `filter_visible_community_menu_items` (e.g. `"can_read"`, `"can_update"`). `True` means no permission gate. |
| `icon` | Semantic UI icon name for rendering (not used by Flask-Menu core). |

## Modifying items after registration

A helper can mutate existing `MenuNode` objects in place. `submenu(...)` returns a reference to the node already stored in the tree; changes are visible the next time `.children` is read.

### Via `register()` (supported API)

```python
communities = current_menu.submenu("communities")
communities.submenu("members").register(order=25, text=_("Members"))
communities.submenu("submit").hide()
```

Re-calling `register()` updates `_order`, `_text`, `_visible_when`, and other standard fields. Custom kwargs such as `permissions` cannot be changed to a new value via re-`register()`; Flask-Menu raises `RuntimeError` if the value differs.

### Via direct mutation (post-registration tweaks)

Public properties like `order`, `text`, and `visible` are read-only. Mutate the backing fields Flask-Menu actually stores:

```python
item = current_menu.submenu("communities").submenu("members")
item._order = 25
item._text = _("Members")
item.permissions = "can_read"  # custom attribute from register(**kwargs)
item._visible_when = my_visible_fn
```

Or call `item.hide()` instead of assigning `_visible_when`.

### What you can and cannot do

| Goal | Approach | Notes |
|------|----------|-------|
| Add an item | `.submenu("name").register(...)` | Works from `finalize_app` after other extensions. |
| Change text, endpoint, `visible_when` | Re-call `.register(...)` on that submenu | Supported API. |
| Change `order` | `register(order=...)` or `item._order = ...` | May not affect display; template name-order list wins. |
| Change `permissions` after registration | Direct assignment (`item.permissions = ...`) | Re-`register()` with a different value errors. |
| Hide an item | `.hide()` or template filter | Filter may also remove items regardless of `visible`. |
| Change displayed tab order | Edit `community_menu_order` in header template | Primary control for community header order. |

## Mental model

```text
MenuNode tree
├── name, parent           # structure
├── _child_entries         # children dict
├── register() / hide()    # configure
├── children, url, text,   # read in templates
│   visible, active, order
└── custom attrs           # icon, permissions, etc.
```

**Read in templates and filters:** `name`, `parent`, `text`, `url`, `order`, `visible`, `active`, `children`, `active_item`, `dynamic_list`.

**Write via `register()`, `hide()`, or private fields:** `_order`, `_text`, `_endpoint`, `_visible_when`, `_active_when`, and custom attributes such as `permissions` and `icon`.
