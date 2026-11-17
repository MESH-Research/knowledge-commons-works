// Part of Knowledge Commons Works
// Copyright (C) 2023-2026, MESH Research
//
// Knowledge Commons Works is an instance of InvenioRDM, which is
// Copyright (c) 2019-2026, CERN
//
// Knowledge Commons Works and InvenioRDM are both free software;
// You can redistribute and/or modify them under the terms of the
// MIT License; see LICENSE file for more details.

import React from "react";
import { Message } from "semantic-ui-react";

import { EDITING_STEP } from "./common";

const GuestCollectionSelector = ({
  checkingCollections,
  checkError,
  matchedCollections,
  selectedGuestCollection,
  setEditingStep,
  showAll = true,
  showHeading = true,
  updateGlobusState,
}) => {
  return (
    <>
      {showHeading && <h5 className="ui dividing header">Your Guest Collections</h5>}
      {checkingCollections ? (
        <div className="ui active centered inline loader m-rel-2"></div>
      ) : checkError ? (
        <Message negative>{checkError}</Message>
      ) : matchedCollections && matchedCollections.length > 0 ? (
        <div
          className="grouped fields"
          style={{
            maxHeight: "350px",
            overflowY: "auto",
          }}
        >
          {matchedCollections.map((mc) => (
            <div className="field" key={mc.id}>
              <div className="ui radio checkbox">
                <input
                  id={`radio-mc-${mc.id}`}
                  type="radio"
                  name="matched_guest_collection"
                  checked={selectedGuestCollection === mc.id}
                  onChange={() => {
                    updateGlobusState({ guest_collection_id: mc.id });
                    setEditingStep(EDITING_STEP.NONE);
                  }}
                  style={{ cursor: "pointer" }}
                />
                <label htmlFor={`radio-mc-${mc.id}`} style={{ cursor: "pointer" }}>
                  <strong>{mc.display_name || "Unnamed Collection"}</strong>
                  <br />
                  <span style={{ fontSize: "0.85em", color: "gray" }}>{mc.id}</span>
                </label>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <Message warning>No guest collections found on this mapped collection.</Message>
      )}
    </>
  );
};

export { GuestCollectionSelector };
