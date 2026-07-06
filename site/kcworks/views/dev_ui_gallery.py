# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Dev-only UI component gallery for theme review."""

from flask import render_template
from flask_login import login_required


@login_required
def dev_ui_gallery():
    """Render the KC Works UI style gallery.

    Login required; not linked from site navigation.

    Returns:
        str: Rendered gallery page.
    """
    return render_template("kcworks/view_templates/ui_gallery.html")
