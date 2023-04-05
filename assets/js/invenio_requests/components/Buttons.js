// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import { i18next } from "@translations/invenio_requests/i18next";
import React, { useEffect } from "react";
import { Button } from "semantic-ui-react";

// components for most common actions, used in other modules, not explicitly in invenio-requests

export const SaveButton = (props) => (
  <Button
    icon="save"
    labelPosition="left"
    positive
    size="mini"
    content={i18next.t("Save")}
    {...props}
  />
);

export const RequestDeclineButton = ({
  onClick,
  loading,
  ariaAttributes,
  size,
  className,
}) => {
  return (
    <Button
      icon="cancel"
      labelPosition="left"
      content={i18next.t("Decline")}
      onClick={onClick}
      loading={loading}
      disabled={loading}
      negative
      size={size}
      className={className}
      {...ariaAttributes}
    />
  );
};

export const RequestAcceptButton = ({
  onClick,
  requestType,
  loading,
  ariaAttributes,
  size,
  className,
}) => {
  const requestIsCommunitySubmission = requestType === "community-submission";
  const buttonText = requestIsCommunitySubmission
    ? i18next.t("Accept and publish")
    : i18next.t("Accept");
  return (
    <Button
      icon="checkmark"
      labelPosition="left"
      content={buttonText}
      onClick={onClick}
      positive
      loading={loading}
      disabled={loading}
      size={size}
      className={className}
      {...ariaAttributes}
    />
  );
};

export const CancelButton = React.forwardRef((props, ref) => {
  useEffect(() => {
    ref?.current?.focus();
  }, []);

  return (
    <Button
      ref={ref}
      icon="cancel"
      labelPosition="left"
      content={i18next.t("Cancel")}
      size="mini"
      {...props}
    />
  );
});

export const RequestCancelButton = ({
  onClick,
  loading,
  ariaAttributes,
  size,
  content=i18next.t("Cancel request"),
  className,
  negative=true
}) => {
  return (
    <Button
      icon="cancel"
      labelPosition="left"
      content={content}
      onClick={onClick}
      loading={loading}
      disabled={loading}
      size={size}
      negative={negative}
      className={className}
      {...ariaAttributes}
    />
  );
};
