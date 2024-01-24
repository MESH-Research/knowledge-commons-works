// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 New York University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import _get from "lodash/get";
import React, { useState, useRef } from "react";
import { useDrag, useDrop } from "react-dnd";
import { Button, Icon, Label, List, Ref } from "semantic-ui-react";
import { CreatibutorsModal, CreatibutorsItemForm } from "./CreatibutorsModal";
import PropTypes from "prop-types";

const CreatibutorsFieldItem = ({
  compKey,
  creatibutorDown,
  creatibutorUp,
  creatibutorsLength,
  itemError,
  index,
  replaceCreatibutor,
  removeCreatibutor,
  moveCreatibutor,
  addLabel,
  editLabel,
  initialCreatibutor,
  displayName,
  roleOptions,
  schema,
  autocompleteNames,
  parentFieldPath,
  showEditForms,
  setShowEditForms,
}) => {
  const dropRef = useRef(null);
  // eslint-disable-next-line no-unused-vars
  const [_, drag, preview] = useDrag({
    item: { index, type: "creatibutor" },
  });
  const [{ hidden }, drop] = useDrop({
    accept: "creatibutor",
    hover(item, monitor) {
      if (!dropRef.current) {
        return;
      }
      const dragIndex = item.index;
      const hoverIndex = index;

      // Don't replace items with themselves
      if (dragIndex === hoverIndex) {
        return;
      }

      if (monitor.isOver({ shallow: true })) {
        moveCreatibutor(dragIndex, hoverIndex);
        item.index = hoverIndex;
      }
    },
    collect: (monitor) => ({
      hidden: monitor.isOver({ shallow: true }),
    }),
  });

  const handleFormClose = () => {
    setShowEditForms(showEditForms.filter((elem) => elem !== compKey));
  };

  const handleFormOpen = () => {
    setShowEditForms([...showEditForms, compKey]);
  };

  const renderRole = (role, roleOptions) => {
    if (role) {
      const friendlyRole =
        roleOptions.find(({ value }) => value === role)?.text ?? role;

      return <Label>{friendlyRole}</Label>;
    }
  };

  function returnBottomError(error) {
    if (error && typeof error === "object") {
      return returnBottomError(error[Object.keys(error)[0]]);
    } else if (error && typeof error === "array") {
      firstError = returnBottomError(
        itemError.find((elem) => ![undefined, null].includes(elem))
      );
    }
    return error;
  }
  let firstError = returnBottomError(itemError);
  console.log("firstError", firstError);

  // Initialize the ref explicitely
  drop(dropRef);
  return (
    <Ref innerRef={dropRef} key={compKey}>
      <List.Item
        key={compKey}
        className={
          hidden ? "deposit-drag-listitem hidden" : "deposit-drag-listitem"
        }
      >
        <List.Content floated="right">
          <Button
            size="mini"
            primary
            type="button"
            onClick={
              showEditForms.includes(compKey)
                ? handleFormClose
                : handleFormOpen
            }
            role="button"
          >
            {i18next.t(showEditForms.includes(compKey) ? "Cancel" : "Edit")}
          </Button>
          <Button
            size="mini"
            type="button"
            onClick={() => removeCreatibutor(index)}
            icon="close"
            role="button"
            aria-label={i18next.t("Remove contributor")}
            negative
          />
          <Button
            size="mini"
            type="button"
            disabled={index === 0}
            onClick={() => creatibutorUp(index)}
            icon="arrow up"
            role="button"
            aria-label={i18next.t("Move contributor up")}
          />
          <Button
            size="mini"
            type="button"
            disabled={index >= creatibutorsLength - 1}
            onClick={() => creatibutorDown(index)}
            icon="arrow down"
            role="button"
            aria-label={i18next.t("Move contributor down")}
          />
        </List.Content>
        <Ref innerRef={drag}>
          <List.Icon name="bars" className="drag-anchor" />
        </Ref>
        <Ref innerRef={preview}>
          <>
            <List.Content>
              <List.Description>
                <span className="creatibutor">
                  {_get(
                    initialCreatibutor,
                    "person_or_org.identifiers",
                    []
                  ).some((identifier) => identifier.scheme === "orcid") && (
                    <img
                      alt="ORCID logo"
                      className="inline-id-icon mr-5"
                      src="/static/images/orcid.svg"
                      width="16"
                      height="16"
                    />
                  )}
                  {_get(
                    initialCreatibutor,
                    "person_or_org.identifiers",
                    []
                  ).some((identifier) => identifier.scheme === "ror") && (
                    <img
                      alt="ROR logo"
                      className="inline-id-icon mr-5"
                      src="/static/images/ror-icon.svg"
                      width="16"
                      height="16"
                    />
                  )}
                  {_get(
                    initialCreatibutor,
                    "person_or_org.identifiers",
                    []
                  ).some((identifier) => identifier.scheme === "gnd") && (
                    <img
                      alt="GND logo"
                      className="inline-id-icon mr-5"
                      src="/static/images/gnd-icon.svg"
                      width="16"
                      height="16"
                    />
                  )}
                  {displayName}{" "}
                  {renderRole(initialCreatibutor?.role, roleOptions)}
                </span>
              </List.Description>
              {firstError && (
                <Label pointing="left" prompt>
                  {firstError.scheme
                    ? firstError.scheme
                    : "Invalid identifiers"}
                </Label>
              )}
            </List.Content>
            {firstError && (
              <Label pointing="above" prompt>
                {firstError}
              </Label>
            )}
            {showEditForms.includes(compKey) && (
              <CreatibutorsItemForm
                addLabel={addLabel}
                autocompleteNames={autocompleteNames}
                editLabel={editLabel}
                handleModalClose={handleFormClose}
                initialCreatibutor={initialCreatibutor}
                modalAction="edit"
                onCreatibutorChange={(selectedCreatibutor) => {
                  replaceCreatibutor(index, selectedCreatibutor);
                }}
                parentFieldPath={parentFieldPath}
                roleOptions={roleOptions}
                schema={schema}
              />
            )}
          </>
        </Ref>
      </List.Item>
    </Ref>
  );
};

CreatibutorsFieldItem.propTypes = {
  compKey: PropTypes.string.isRequired,
  identifiersError: PropTypes.array,
  index: PropTypes.number.isRequired,
  replaceCreatibutor: PropTypes.func.isRequired,
  removeCreatibutor: PropTypes.func.isRequired,
  moveCreatibutor: PropTypes.func.isRequired,
  addLabel: PropTypes.node,
  editLabel: PropTypes.node,
  initialCreatibutor: PropTypes.object.isRequired,
  displayName: PropTypes.string,
  roleOptions: PropTypes.array.isRequired,
  schema: PropTypes.string.isRequired,
  autocompleteNames: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
};

export { CreatibutorsFieldItem };
