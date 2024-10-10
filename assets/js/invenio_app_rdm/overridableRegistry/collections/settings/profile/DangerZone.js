/*
* This file is part of Knowledge Commons Works.
*   Copyright (C) 2024 Mesh Research.
*
* Knowledge Commons Works is based on InvenioRDM, and
* this file is based on code from InvenioRDM. InvenioRDM is
*   Copyright (C) 2020-2024 CERN.
*   Copyright (C) 2020-2024 Northwestern University.
*   Copyright (C) 2020-2024 T U Wien.
*
* InvenioRDM and Knowledge Commons Works are both free software;
* you can redistribute and/or modify them under the terms of the
* MIT License; see LICENSE file for more details.
*/

import { i18next } from "@translations/invenio_communities/i18next";
import React from "react";
import { Grid, Header, Segment } from "semantic-ui-react";
import { CommunityApi } from "@js/invenio_communities/api";
import { RenameCommunitySlugButton } from "@js/invenio_communities/settings/profile/RenameCommunitySlugButton";
import PropTypes from "prop-types";
import { DeleteCommunityModal } from "@js/invenio_communities/settings/profile/DeleteCommunityModal";

const DangerZone = ({ community, onError, permissions }) => {
  if (permissions.can_delete || permissions.can_rename) {
    return (
    <Grid.Row className="danger-zone">
      <Grid.Column as="section" width={16}>
        <Segment className="negative rel-mt-2">
          <Header as="h2" className="negative">
            {i18next.t("Danger zone")}
          </Header>
          <Grid>
            {permissions.can_rename && (
              <>
                <Grid.Column mobile={16} tablet={10} computer={12}>
                  <Header as="h3" size="small">
                    {i18next.t("Change identifier")}
                  </Header>
                  <p>
                    {i18next.t(
                      "Changing your collection's unique identifier can have unintended side effects."
                    )}
                  </p>
                </Grid.Column>
                <Grid.Column mobile={16} tablet={6} computer={4} floated="right">
                  <RenameCommunitySlugButton community={community} onError={onError} />
                </Grid.Column>
              </>
            )}
            {permissions.can_delete && (
              <>
                <Grid.Column mobile={16} tablet={10} computer={12} floated="left">
                  <Header as="h3" size="small">
                    {i18next.t("Delete collection")}
                  </Header>
                  <p>
                    {i18next.t(
                      "Once deleted, it will be gone forever. Please be certain."
                    )}
                  </p>
                </Grid.Column>
                <Grid.Column mobile={16} tablet={6} computer={4} floated="right">
                  <DeleteCommunityModal
                    community={community}
                    label={i18next.t("Delete collection")}
                    redirectURL="/collections"
                    onDelete={async () => {
                      const client = new CommunityApi();
                      await client.delete(community.id);
                    }}
                  />
                </Grid.Column>
              </>
            )}
          </Grid>
        </Segment>
      </Grid.Column>
    </Grid.Row>
    );
  } else {
    return null;
  }
};

DangerZone.propTypes = {
  community: PropTypes.object.isRequired,
  onError: PropTypes.func.isRequired,
  permissions: PropTypes.object.isRequired,
};

export { DangerZone };
