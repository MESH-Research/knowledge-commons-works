/*
 * This file is part of Knowledge Commons Works.
 * Copyright (C) 2026 Mesh Research.
 */

import { CommunityApi } from "@js/invenio_communities/api";
import { communityErrorSerializer } from "@js/invenio_communities/api/serializers";
import { i18next } from "@translations/kcworks/i18next";
import _defaultsDeep from "lodash/defaultsDeep";
import _get from "lodash/get";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { Form, Header, Message } from "semantic-ui-react";

/**
 * Guidance shown when subcollections are allowed.
 *
 * @param {object} props - Component props.
 * @param {string} props.linkSubcollectionUrl - URL to link an existing collection.
 * @param {string} props.newSubcollectionUrl - URL to create a new subcollection.
 * @returns {React.ReactElement} Next-steps message.
 */
function SubcollectionsNextSteps({ linkSubcollectionUrl, newSubcollectionUrl }) {
  return (
    <Message className="rel-mt-1">
      <Message.Header>{i18next.t("Next steps")}</Message.Header>
      <Message.Content>
        <p>
          {i18next.t(
            "You can create a new subcollection, or link an existing collection that you own:"
          )}
        </p>
        <p>
          <a className="ui mini button primary" href={newSubcollectionUrl}>
            {i18next.t("New subcollection")}
          </a>{" "}
          <a className="ui mini button" href={linkSubcollectionUrl}>
            {i18next.t("Link existing")}
          </a>
        </p>
      </Message.Content>
    </Message>
  );
}

SubcollectionsNextSteps.propTypes = {
  linkSubcollectionUrl: PropTypes.string.isRequired,
  newSubcollectionUrl: PropTypes.string.isRequired,
};

/**
 * Settings form for subcollection parent capability.
 *
 * Persists `children.allow` immediately when the toggle changes, then reloads
 * so nav (e.g. Browse) reflects the new setting.
 *
 * @param {object} props - Component props.
 * @param {object} props.community - Serialized community.
 * @returns {React.ReactElement} Subcollections settings form.
 */
export default function CommunitySubcollectionsForm({ community }) {
  const [allow, setAllow] = useState(Boolean(_get(community, "children.allow")));
  const [error, setError] = useState(undefined);
  const [isSaving, setIsSaving] = useState(false);

  const newSubcollectionUrl = `/collections/${community.slug}/subcommunities/new?mode=new`;
  const linkSubcollectionUrl = `/collections/${community.slug}/subcommunities/new?mode=link`;
  const hasError = error !== undefined;

  /**
   * Persist the toggle value and reload on success.
   *
   * @param {boolean} checked - New `children.allow` value.
   * @returns {Promise<void>}
   */
  const handleToggle = async (checked) => {
    const previous = allow;
    setAllow(checked);
    setIsSaving(true);
    setError(undefined);

    try {
      const client = new CommunityApi();
      const payload = _defaultsDeep({}, community, {
        children: { allow: false },
      });
      payload.children.allow = checked;
      await client.update(community.id, payload);
      window.location.reload();
    } catch (submitError) {
      if (submitError === "UNMOUNTED") {
        return;
      }

      setAllow(previous);
      const { message } = communityErrorSerializer(submitError);
      if (message) {
        setError(message);
      } else {
        setError(i18next.t("Unable to update subcollections setting."));
      }
      setIsSaving(false);
    }
  };

  return (
    <Form>
      <Message hidden={!hasError} negative>
        <Message.Content>{error}</Message.Content>
      </Message>

      <Header as="h2" size="small">
        {i18next.t("Subcollections")}
        <Header.Subheader className="mt-5">
          {i18next.t(
            "Control whether this collection can act as a parent for other collections."
          )}
        </Header.Subheader>
      </Header>

      <Form.Field>
        <Form.Checkbox
          toggle
          label={i18next.t("Allow other collections to be linked as subcollections")}
          checked={allow}
          disabled={isSaving}
          onChange={(_event, { checked }) => handleToggle(checked)}
        />
        <div className="helptext">
          {i18next.t(
            "When enabled, this collection can accept subcollection requests and a Browse menu appears. Subcollections may themselves accept further subcollections (multi-level nesting)."
          )}
        </div>
      </Form.Field>

      {allow && (
        <SubcollectionsNextSteps
          linkSubcollectionUrl={linkSubcollectionUrl}
          newSubcollectionUrl={newSubcollectionUrl}
        />
      )}
    </Form>
  );
}

CommunitySubcollectionsForm.propTypes = {
  community: PropTypes.object.isRequired,
};
