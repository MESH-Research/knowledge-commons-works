// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 New York University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState, useRef } from "react";
import { useDrag, useDrop } from "react-dnd";
import { Button, Icon, Label, List, Ref } from "semantic-ui-react";
import { CreatibutorsItemForm } from "./CreatibutorsItemForm";
import PropTypes from "prop-types";
import _get from "lodash/get";
import { i18next } from "@translations/invenio_rdm_records/i18next";

const CreatibutorsFieldItem = ({
  addLabel,
  addCreatibutor,
  autocompleteNames,
  cancelLabel,
  creatibutorDown,
  creatibutorUp,
  creatibutorsLength,
  displayName,
  editLabel,
  fieldPath,
  fieldPathPrefix,
  focusAddButtonHandler,
  handleCloseForm,
  handleOpenForm,
  handleRemove,
  handleCancel,
  index,
  isNewItem,
  itemError,
  removeCreatibutor,
  moveCreatibutor,
  roleOptions,
  showEditForms,
  setShowEditForms,
  values,
}) => {
  console.log("CreatibutorsFieldItem index", index);

  const identifiersList = _get(
    values,
    `${fieldPathPrefix}.person_or_org.identifiers`,
    []
  );
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

  const renderRole = (role, roleOptions) => {
    if (role) {
      const friendlyRole =
        roleOptions.find(({ value }) => value === role)?.text ?? role;

      return <Label>{friendlyRole}</Label>;
    }
  };

  // TODO: Deprecate this function
  // function returnBottomError(error) {
  //   if (error && typeof error === "object") {
  //     return returnBottomError(error[Object.keys(error)[0]]);
  //   } else if (error && typeof error === "array") {
  //     firstError = returnBottomError(
  //       itemError.find((elem) => ![undefined, null].includes(elem))
  //     );
  //   }
  //   return error;
  // }
  // let firstError = returnBottomError(itemError);

  function getErrorMessages(itemErrors) {
    console.log("getErrorMessages itemErrors", itemErrors);
    let errorMessages = [];
    if ( typeof itemErrors === "array" ) {
      itemErrors.forEach((error) => {
        errorMessages.push(...getErrorMessages(error));
      });
    } else if ((typeof itemErrors === "object") && (Object.keys(itemErrors).length > 0)) {
      for ( const [key, value] of Object.entries(itemErrors)) {
        if (["object", "array"].includes(typeof value)) {
          errorMessages.push(...getErrorMessages(value));
        } else if (typeof value === "string") {
          errorMessages.push(value);
        };
      };
    };
    return errorMessages;
  };
  const errorMessages = !!itemError ? getErrorMessages(itemError) : [];

  // Initialize the ref explicitely

  console.log("CreatibutorsFieldItem showEditForms", showEditForms);

  drop(dropRef);

  return (
    <Ref innerRef={dropRef} key={index}>
      <List.Item
        key={index}
        className={
          hidden ? "deposit-drag-listitem hidden" : "deposit-drag-listitem"
        }
      >
        {!isNewItem && (
          <>
            <List.Content floated="right">
              <Button
                size="mini"
                primary
                type="button"
                onClick={() => {
                  showEditForms.includes(index)
                    ? handleCancel(removeCreatibutor, index)
                    : handleOpenForm(index)
                }}
                role="button"
              >
                {i18next.t(
                  showEditForms.includes(index) ? cancelLabel : editLabel
                )}
              </Button>
              <Button
                size="mini"
                type="button"
                onClick={() => handleRemove(removeCreatibutor, index)}
                icon="close"
                role="button"
                aria-label={i18next.t("Remove contributor")}
                negative
              />
              <Button
                size="mini"
                type="button"
                disabled={index === 0}
                onClick={() => creatibutorUp(moveCreatibutor, index)}
                icon="arrow up"
                role="button"
                aria-label={i18next.t("Move contributor up")}
              />
              <Button
                size="mini"
                type="button"
                disabled={index >= creatibutorsLength - 1}
                onClick={() => creatibutorDown(moveCreatibutor, index)}
                icon="arrow down"
                role="button"
                aria-label={i18next.t("Move contributor down")}
              />
            </List.Content>
            <Ref innerRef={drag}>
              <List.Icon name="bars" className="drag-anchor" />
            </Ref>
          </>
        )}
        <Ref innerRef={preview}>
          <>
            {!isNewItem && (
              <>
              <List.Content>
                <List.Description>
                  <span className="creatibutor">
                    {displayName}{" "}
                    {identifiersList.some((identifier) => identifier.scheme === "orcid") && (
                      <img
                        alt="ORCID logo"
                        className="inline-id-icon mr-5"
                        src="/static/images/orcid.svg"
                        width="16"
                        height="16"
                      />
                    )}
                    {identifiersList.some((identifier) => identifier.scheme === "ror") && (
                      <img
                        alt="ROR logo"
                        className="inline-id-icon mr-5"
                        src="/static/images/ror-icon.svg"
                        width="16"
                        height="16"
                      />
                    )}
                    {identifiersList.some((identifier) => identifier.scheme === "gnd") && (
                      <img
                        alt="GND logo"
                        className="inline-id-icon mr-5"
                        src="/static/images/gnd-icon.svg"
                        width="16"
                        height="16"
                      />
                    )}
                    {" "}
                    {renderRole(_get(values, `${fieldPathPrefix}.role`), roleOptions)}
                  </span>
                </List.Description>
              </List.Content>
              </>
            )}
            {showEditForms.includes(index) && (
              <CreatibutorsItemForm
                addCreatibutor={addCreatibutor}
                addLabel={addLabel}
                autocompleteNames={autocompleteNames}
                fieldPath={fieldPath}
                fieldPathPrefix={fieldPathPrefix}
                focusAddButtonHandler={focusAddButtonHandler}
                handleCancel={handleCancel}
                handleCloseForm={handleCloseForm}
                index={index}
                isNewItem={isNewItem}
                removeCreatibutor={removeCreatibutor}
                roleOptions={roleOptions}
                values={values}
              />
            )}
            {errorMessages.length > 0 && !showEditForms.includes(index) && (
              <Label pointing prompt>
                <List>
                  {errorMessages.map(e => <List.Item>{e}</List.Item>)}
                </List>
              </Label>
            )}
          </>
        </Ref>
      </List.Item>
    </Ref>
  );
};

CreatibutorsFieldItem.propTypes = {
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
