// This file is part of Knowledge Commons Works
// Adapted from the component in Invenio-RDM-Records
// Copyright (C) 2026 MESH Research
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2021 Graz University of Technology.
//
// Knowledge-Commons-Works and Invenio-RDM-Records are free software; you can
// redistribute them and/or modify them under the terms of the MIT License; see
// LICENSE file for more details.

import React, { useRef, useState } from "react";
import { useSelector } from "react-redux";
import PropTypes from "prop-types";
import { useFormikContext, getIn } from "formik";
import { Accordion, Form, Icon, Segment } from "semantic-ui-react";
import { i18next } from "@translations/i18next";
import { useMeasuredHeightAnimation } from "@js/invenio_modular_deposit_form/util/useMeasuredHeightAnimation";
import {
  MetadataAccess,
  FilesAccess,
  EmbargoAccess,
  AccessRequestsAccess,
  AccessMessage,
} from "./access_rights_components";

const ACCORDION_INDEX = 0;
const HEIGHT_ANIMATING_CLASS = "height-animating";

/**
 * Access settings panel: Message (top-attached) + bottom-attached Segment with
 * a measured-height accordion wrapping the visibility controls.
 */
const AccessRightField = ({
  fieldPath,
  allowRecordRestriction = true,
  // Kept for Overridable / FieldComponentWrapper API compatibility.
  icon: _icon = undefined,
  label: _label = i18next.t("Access Permissions"),
  record = {},
  recordRestrictionGracePeriod = undefined,
  showMetadataAccess = undefined,
}) => {
  const community = useSelector((s) => s.deposit.editorState.selectedCommunity);
  const files = useSelector((s) => s.files);

  const isGhostCommunity = community?.is_ghost === true;
  const communityAccess =
    (community && !isGhostCommunity && community.access.visibility) || "public";
  const { values } = useFormikContext();
  // New drafts / incomplete fixtures may omit files; treat as metadata-only.
  const isMetadataOnly = !record.files?.enabled || Object.entries(files?.entries ?? {}).length < 1;

  const [open, setOpen] = useState(false);
  const contentRef = useRef(null);
  const { isAnimating, expand, collapse } = useMeasuredHeightAnimation(contentRef, {
    open,
    onOpen: () => setOpen(true),
    onClose: () => setOpen(false),
    // Lift CSS `height: 0` briefly so scrollHeight is the full open size.
    openMeasure: { addClass: HEIGHT_ANIMATING_CLASS },
  });
  // Keep `.active` through the close tween so content stays measurable.
  const contentActive = open || isAnimating;

  return (
    <>
      <AccessMessage
        access={getIn(values, fieldPath)}
        accessCommunity={communityAccess}
        metadataOnly={isMetadataOnly}
        attached="top"
      />
      <Segment
        id="visibility-section"
        className="access-right pr-0 pl-0 pb-0 pt-0"
        attached="bottom"
      >
        <Accordion fluid exclusive={false} className="measured-height">
          <Accordion.Title
            as="button"
            active={open}
            index={ACCORDION_INDEX}
            className="ui button transparent basic padded borderless borderless-hover fluid access-settings-toggle pl-20 pb-5 pr-0"
            onClick={() => (open ? collapse() : expand())}
          >
            {!open ? i18next.t("Change access permissions") : i18next.t("Hide settings")}
            <Icon name={open ? "chevron up" : "chevron down"} className="mt-5" aria-hidden="true" />
          </Accordion.Title>
          <div
            ref={contentRef}
            className={`content${contentActive ? " active" : ""}${
              isAnimating ? ` ${HEIGHT_ANIMATING_CLASS}` : ""
            }`}
          >
            <Form.Field required>
              {showMetadataAccess && (
                <MetadataAccess
                  recordAccess={getIn(values, `${fieldPath}.record`)}
                  communityAccess={communityAccess}
                  record={record}
                  recordRestrictionGracePeriod={recordRestrictionGracePeriod}
                  allowRecordRestriction={allowRecordRestriction}
                  className="mt-20"
                />
              )}

              <FilesAccess
                access={getIn(values, fieldPath)}
                accessCommunity={communityAccess}
                metadataOnly={isMetadataOnly}
              />
              <EmbargoAccess
                access={getIn(values, fieldPath)}
                accessCommunity={communityAccess}
                metadataOnly={isMetadataOnly}
              />
              <AccessRequestsAccess
                access={getIn(values, fieldPath)}
                metadataOnly={isMetadataOnly}
                className="mb-20"
              />
            </Form.Field>
          </div>
        </Accordion>
      </Segment>
    </>
  );
};

AccessRightField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  icon: PropTypes.string,
  allowRecordRestriction: PropTypes.bool,
  record: PropTypes.object,
  recordRestrictionGracePeriod: PropTypes.number,
  showMetadataAccess: PropTypes.bool,
};

export { AccessRightField };
