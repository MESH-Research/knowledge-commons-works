# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""KCWorks instance configuration fragments.

Modules such as ``auth``, ``mail``, ``security``, URLs, custom fields, and
deposit layout are loaded from ``invenio.cfg`` via ``from kcworks.config...``
so the cfg file can be executed without a parent package (Flask
``from_pyfile`` / test ``exec``).
"""
