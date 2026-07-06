// Part of the Knowledge Commons Repository
// Copyright (C) 2024-2026 MESH Research
//
// Knowledge Commons Repository is free software; you can redistribute it
// and/or modify it under the terms of the MIT License; see LICENSE file for
// more details.

import { connect } from "react-redux";
import { SubmitReviewModal } from "@js/invenio_rdm_records";
import { getReadableFields } from "@js/invenio_modular_deposit_form/utils";

const mapStateToProps = (state) => {
  const community = state.deposit.editorState.selectedCommunity;
  const permissionsPerField = state.deposit.config?.permissions_per_field ?? {};
  const policy = permissionsPerField?.[community?.slug]?.policy;
  let extraCheckboxes = [];
  if (policy) {
    const restrictedFields = Array.isArray(policy)
      ? policy
      : Object.keys(policy);
    if (restrictedFields.length > 0) {
      const [readable, readableWithArrays] = getReadableFields(restrictedFields);
      const labels = [...readable, ...readableWithArrays].join(", ");
      extraCheckboxes = [
        {
          fieldPath: "acceptRestrictedFields",
          text: `The ${community.metadata.title} collection has additional editing restrictions. After publishing, you may not be able to change these fields without approval: ${labels}.`,
        },
      ];
    }
  }
  return { extraCheckboxes };
};

export const KcworksSubmitReviewModal = connect(mapStateToProps)(SubmitReviewModal);
