# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""API views for irreversible record hard-delete."""

from flask import Response, g, jsonify, request
from flask.views import MethodView
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services.errors import PermissionDeniedError
from kcworks.proxies import current_kcworks_records_service
from kcworks.services.records.errors import HardDeleteError, HardDeleteLookupError
from kcworks.services.records.service import RECORD_ID_TYPES
from werkzeug.exceptions import BadRequest, NotFound


class RecordHardDeleteAPI(MethodView):
    """View for hard-deleting a single record.

    Requires a bearer token with `records:delete` (scope gate) and an
    administration (or system) identity (service permission).

    Path value is interpreted with optional body/query `id_type`
    (`recid` default, or `doi` / `import-recid`).
    """

    view_name = "record_hard_delete_api"

    def delete(self, pid_value: str) -> tuple[Response | str, int]:
        """Hard-delete the published or soft-deleted record.

        Args:
            pid_value: Identifier value (recid by default).

        Returns:
            Empty body with HTTP 204 on success.

        Raises:
            NotFound: No such published record.
            BadRequest: Invalid `id_type` or parent/ambiguous lookup.
            PermissionDeniedError: Caller lacks hard-delete permission.
        """
        # Silent: DELETE with `Content-Type: application/json` and an empty
        # body must not 400 on JSON parse.
        payload = request.get_json(silent=True) or {}
        note = payload.get("note")
        id_type = payload.get("id_type") or request.args.get("id_type") or "recid"

        try:
            current_kcworks_records_service.hard_delete_record(
                g.identity, pid_value, id_type=str(id_type), note=note
            )
        except PIDDoesNotExistError as exc:
            raise NotFound(
                description=f"Record {id_type}={pid_value!r} not found."
            ) from exc
        except HardDeleteLookupError as exc:
            raise BadRequest(description=str(exc)) from exc
        except HardDeleteError as exc:
            return jsonify({"message": str(exc), "status": 502}), 502
        except PermissionDeniedError:
            raise

        return "", 204


class RecordsHardDeleteBulkAPI(MethodView):
    """View for hard-deleting many records of one identifier type.

    Body (either form):

    - `{"ids": ["…", …], "id_type": "doi"|"import-recid"|"recid", "note": "…"}`
    - `{"recids": ["…"], "note": "…"}` — shorthand for `id_type=recid`

    One `id_type` per request. Same auth as single hard-delete.
    """

    view_name = "records_hard_delete_bulk_api"

    def post(self) -> tuple[Response, int]:
        """Hard-delete many published or soft-deleted records.

        Returns:
            JSON batch summary with HTTP 200 when every id succeeded, or
            207 Multi-Status when any id failed (body still lists per-id
            outcomes).

        Raises:
            BadRequest: Missing/empty/oversized/invalid ids.
            PermissionDeniedError: Propagated only if raised outside per-id
                handling (should not happen for normal auth).
        """
        payload = request.get_json(silent=True) or {}
        note = payload.get("note")
        ids = payload.get("ids")
        recids = payload.get("recids")

        if ids is not None and recids is not None:
            raise BadRequest(
                description="Provide either `ids` or `recids`, not both."
            )
        if ids is not None:
            if not isinstance(ids, list) or any(
                not isinstance(item, str) for item in ids
            ):
                raise BadRequest(
                    description="`ids` must be a JSON array of strings."
                )
            batch_ids = ids
            id_type = str(payload.get("id_type") or "recid").strip().lower()
        elif recids is not None:
            if not isinstance(recids, list) or any(
                not isinstance(item, str) for item in recids
            ):
                raise BadRequest(
                    description="`recids` must be a JSON array of strings."
                )
            batch_ids = recids
            id_type = "recid"
        else:
            raise BadRequest(
                description="Provide `ids` (with optional `id_type`) or `recids`."
            )

        if id_type not in RECORD_ID_TYPES:
            raise BadRequest(
                description=(
                    f"Unsupported id_type {id_type!r}; "
                    f"expected one of {sorted(RECORD_ID_TYPES)}."
                )
            )

        try:
            result = current_kcworks_records_service.hard_delete_records(
                g.identity,
                batch_ids,
                id_type=id_type,
                note=note,
            )
        except ValueError as exc:
            raise BadRequest(description=str(exc)) from exc
        except PermissionDeniedError:
            raise

        status = 207 if result["failed"] else 200
        return jsonify(result), status
