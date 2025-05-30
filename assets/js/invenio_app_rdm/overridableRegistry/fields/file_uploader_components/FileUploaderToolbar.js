// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2021 Graz University of Technology.
// Copyright (C)      2022 TU Wien.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { useFormikContext } from "formik";
import React from "react";
import {
  Header,
  Checkbox,
  Grid,
  Icon,
  Label,
  List,
  Popup,
} from "semantic-ui-react";
import { humanReadableBytes } from "react-invenio-forms";
import { i18next } from "@translations/i18next";
import PropTypes from "prop-types";
import Overridable from "react-overridable";

// NOTE: This component has to be a function component to allow
//       the `useFormikContext` hook.
export const FileUploaderToolbar = (props) => {
  const {
    filesList,
    filesSize,
    filesEnabled,
    showMetadataOnlyToggle,
    quota,
    decimalSizeDisplay,
  } = props;
  const { setFieldValue } = useFormikContext();

  const handleOnChangeMetadataOnly = () => {
    setFieldValue("files.enabled", !filesEnabled);
    setFieldValue("access.files", "public");
  };

  return (
    <Overridable
      id="ReactInvenioDeposit.FileUploaderToolbar.layout"
      filesList={filesList}
      filesSize={filesSize}
      filesEnabled={filesEnabled}
      showMetadataOnlyToggle={showMetadataOnlyToggle}
      quota={quota}
      decimalSizeDisplay={decimalSizeDisplay}
      handleOnChangeMetadataOnly={handleOnChangeMetadataOnly}
    >
      <>
        {showMetadataOnlyToggle && (
          <Grid.Column
            verticalAlign="middle"
            floated="left"
            mobile={16}
            tablet={6}
            computer={6}
          >
            <Overridable
              id="ReactInvenioDeposit.FileUploaderToolbar.MetadataOnlyToggle.container"
              filesList={filesList}
              filesEnabled={filesEnabled}
              showMetadataOnlyToggle={showMetadataOnlyToggle}
              handleOnChangeMetadataOnly={handleOnChangeMetadataOnly}
            >
              <List horizontal>
                <List.Item>
                  <Checkbox
                    label={i18next.t("Metadata-only record")}
                    onChange={handleOnChangeMetadataOnly}
                    disabled={filesList.length > 0}
                    checked={!filesEnabled}
                  />
                </List.Item>
                <List.Item>
                  <Popup
                    trigger={
                      <Icon
                        name="question circle outline"
                        className="neutral"
                      />
                    }
                    content={i18next.t("Disable files for this record")}
                    position="top center"
                  />
                </List.Item>
              </List>
            </Overridable>
          </Grid.Column>
        )}
        <Overridable
          id="ReactInvenioDeposit.FileUploaderToolbar.FileList.container"
          filesList={filesList}
          filesSize={filesSize}
          filesEnabled={filesEnabled}
          quota={quota}
          decimalSizeDisplay={decimalSizeDisplay}
        >
          {filesEnabled && (
            <Grid.Column
              mobile={16}
              tablet={16}
              computer={16}
              className="storage-col justify-space-between"
            >
              {/* <Header size="tiny" className="mr-10">
                {i18next.t("Storage available")}
              </Header> */}
                  <Label
                    image
                    {...(humanReadableBytes(filesSize, decimalSizeDisplay) ===
                    humanReadableBytes(quota.maxStorage, decimalSizeDisplay)
                      ? { color: "warning" }
                      : { color: "primary" })}
                    className="basic"
                  >
                    <Icon name="pie chart" />
                    {humanReadableBytes(
                      quota.maxStorage - filesSize,
                      decimalSizeDisplay
                    )}{" "}
                    {i18next.t("of")}{" "}
                    {humanReadableBytes(quota.maxStorage, decimalSizeDisplay)}
                    <Label.Detail>{" storage left for this work"}</Label.Detail>
                  </Label>
                  <Label
                    {...(filesList.length === quota.maxFiles
                      ? { color: "warning" }
                      : { color: "primary" })}
                    image
                    className="basic"
                  >
                    <Icon name="zip" />
                    {i18next.t(`{{remaining}} out of {{maxfiles}}`, {
                      remaining: quota.maxFiles - filesList.length,
                      maxfiles: quota.maxFiles,
                    })}
                    <Label.Detail>{i18next.t(`max files left`)}</Label.Detail>
                  </Label>
            </Grid.Column>
          )}
        </Overridable>
      </>
    </Overridable>
  );
};

FileUploaderToolbar.propTypes = {
  filesList: PropTypes.array,
  filesSize: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  filesEnabled: PropTypes.bool.isRequired,
  quota: PropTypes.object,
  decimalSizeDisplay: PropTypes.bool,
  showMetadataOnlyToggle: PropTypes.bool,
};

FileUploaderToolbar.defaultProps = {
  filesList: undefined,
  filesSize: undefined,
  quota: undefined,
  decimalSizeDisplay: false,
  showMetadataOnlyToggle: true,
};
