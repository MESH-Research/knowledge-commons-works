/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
 * Copyright (C) 2021-2023 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import React, { useState } from "react";
import Dropzone from "react-dropzone";
import { humanReadableBytes } from "react-invenio-forms";
import { Image } from "react-invenio-forms";
import { Button, Divider, Header, Icon, Message } from "semantic-ui-react";
import { CommunityApi } from "../../api";
import { DeleteButton } from "./DeleteButton";
import PropTypes from "prop-types";

function noCacheUrl(url) {
  const result = new URL(url);
  const randomValue = new Date().getMilliseconds() * 5;
  result.searchParams.set("no-cache", randomValue.toString());
  return result.toString();
}

const LogoUploader = ({ community, defaultLogo, hasLogo, onError, logoMaxSize }) => {
  /* State */
  // props initilization is fine since original props don't change after
  // initial mounting.
  const [logoUrl, logoSetUrl] = useState(community.links.logo);
  const [logoUpdated, logoSetUpdated] = useState(false);
  const [logoExists, logoSetExists] = useState(hasLogo);

  // Nicer naming
  const logoDefault = defaultLogo;

  let dropzoneParams = {
    preventDropOnDocument: true,
    onDropAccepted: async (acceptedFiles) => {
      const file = acceptedFiles[0];

      try {
        const client = new CommunityApi();
        await client.updateLogo(community.id, file);

        const logoUrlNoCache = noCacheUrl(logoUrl);
        logoSetUrl(logoUrlNoCache);
        logoSetUpdated(true);
        logoSetExists(true);
      } catch (error) {
        onError(error);
      }
    },
    onDropRejected: (rejectedFiles) => {
      // TODO: show error message when files are rejected e.g size limit
      console.error(rejectedFiles[0].errors);
    },
    multiple: false,
    noClick: true,
    noDrag: true,
    noKeyboard: true,
    disabled: false,
    maxFiles: 1,
    maxSize: 5000000, // 5Mb limit
    accept: ".jpeg,.jpg,.png",
  };

  const deleteLogo = async () => {
    const client = new CommunityApi();
    await client.deleteLogo(community.id);

    const logoUrlNoCache = noCacheUrl(logoUrl);
    logoSetUrl(logoUrlNoCache);
    logoSetUpdated(true);
    logoSetExists(false);
  };

  return (
    <Dropzone {...dropzoneParams}>
      {({ getRootProps, getInputProps, open: openFileDialog }) => (
        <>
          <span {...getRootProps()}>
            <input {...getInputProps()} />
            <Header as="h2" size="small" className="mt-0">
              {i18next.t("Profile picture")}
            </Header>
            <Image
              /* Change in key will cause a remounting. */
              key={logoUrl}
              src={logoUrl}
              fallbackSrc={logoDefault}
              loadFallbackFirst
              fluid
              wrapped
              rounded
              className="community-logo settings"
            />

            <Divider hidden />
          </span>

          <Button
            fluid
            icon
            labelPosition="left"
            type="button"
            onClick={openFileDialog}
            className="rel-mt-1 rel-mb-1"
          >
            <Icon name="upload" />
            {i18next.t("Upload new picture")}
          </Button>
          <label className="helptext">
            {i18next.t("File must be smaller than {{fileSize}}", {
              fileSize: humanReadableBytes(logoMaxSize, true),
            })}
          </label>
          {logoExists && (
            <DeleteButton
              id="delete-picture-button"
              label={i18next.t("Delete picture")}
              confirmationMessage={
                <Header as="h2" size="medium">
                  {i18next.t("Are you sure you want to delete this picture?")}
                </Header>
              }
              onDelete={deleteLogo}
              onError={onError}
            />
          )}
          {logoUpdated && (
            <Message
              info
              icon="warning circle"
              size="small"
              content={i18next.t(
                "It may take a few moments for changes to be visible everywhere"
              )}
            />
          )}
        </>
      )}
    </Dropzone>
  );
};

LogoUploader.propTypes = {
  community: PropTypes.object.isRequired,
  defaultLogo: PropTypes.string.isRequired,
  hasLogo: PropTypes.bool.isRequired,
  onError: PropTypes.func.isRequired,
  logoMaxSize: PropTypes.number.isRequired,
};

export default LogoUploader;
