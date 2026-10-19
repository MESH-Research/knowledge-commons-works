/*
 * This file is part of Knowledge Commons Works.
 * Copyright (C) 2026 Mesh Research.
 */

import { CommunitySettingsForm } from "@js/invenio_communities/settings/components";
import { i18next } from "@translations/kcworks/i18next";
import { useField, useFormikContext } from "formik";
import _get from "lodash/get";
import PropTypes from "prop-types";
import React from "react";
import { Form, Header, Message } from "semantic-ui-react";

/**
 * Toggle for `children.allow`.
 *
 * @returns {React.ReactElement} Allow-subcollections field.
 */
function AllowSubcollectionsField() {
  const [field, , helpers] = useField({ name: "children.allow", type: "checkbox" });

  return (
    <Form.Field>
      <Form.Checkbox
        toggle
        label={i18next.t("Allow other collections to join as subcollections")}
        checked={Boolean(field.value)}
        onChange={(_event, { checked }) => helpers.setValue(checked)}
      />
      <div className="helptext">
        {i18next.t(
          "When enabled, this collection can accept subcollection requests and a Browse menu appears. Subcollections may themselves accept further subcollections (multi-level nesting)."
        )}
      </div>
    </Form.Field>
  );
}

/**
 * Guidance shown when subcollections are currently allowed in the form.
 *
 * @param {object} props - Component props.
 * @param {string} props.newSubcollectionUrl - URL for the new-subcollection page.
 * @returns {React.ReactElement|null} Next-steps message, or null.
 */
function SubcollectionsNextSteps({ newSubcollectionUrl }) {
  const { values } = useFormikContext();
  if (!_get(values, "children.allow")) {
    return null;
  }

  return (
    <Message className="rel-mt-1">
      <Message.Header>{i18next.t("Next steps")}</Message.Header>
      <Message.Content>
        <p>
          {i18next.t(
            "After saving, refresh the page to see the Browse menu. You can also request that an existing collection join as a subcollection, or create a new one:"
          )}
        </p>
        <p>
          <a href={newSubcollectionUrl}>{i18next.t("New subcollection")}</a>
        </p>
      </Message.Content>
    </Message>
  );
}

SubcollectionsNextSteps.propTypes = {
  newSubcollectionUrl: PropTypes.string.isRequired,
};

/**
 * Settings form for subcollection parent capability.
 *
 * @param {object} props - Component props.
 * @param {object} props.community - Serialized community.
 * @returns {React.ReactElement} Subcollections settings form.
 */
export default function CommunitySubcollectionsForm({ community }) {
  const newSubcollectionUrl = `/collections/${community.slug}/subcommunities/new`;

  return (
    <CommunitySettingsForm
      community={community}
      initialValues={{
        children: {
          allow: false,
        },
      }}
    >
      <Header as="h2" size="small">
        {i18next.t("Subcollections")}
        <Header.Subheader className="mt-5">
          {i18next.t(
            "Control whether this collection can act as a parent for other collections."
          )}
        </Header.Subheader>
      </Header>

      <AllowSubcollectionsField />

      <SubcollectionsNextSteps newSubcollectionUrl={newSubcollectionUrl} />
    </CommunitySettingsForm>
  );
}

CommunitySubcollectionsForm.propTypes = {
  community: PropTypes.object.isRequired,
};
