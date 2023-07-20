// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021-2022 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { Image } from "react-invenio-forms";
import { connect } from "react-redux";
import { Button, Icon } from "semantic-ui-react";
// import { changeSelectedCommunity } from "../../state/actions";
import { CommunitySelectionModal } from "@js/invenio_rdm_records";

export const changeSelectedCommunity = (community) => {
  return async (dispatch) => {
    dispatch({
      type: "SET_COMMUNITY",
      payload: { community },
    });
  };
};

const CommunityFieldComponent = ({community=undefined,
                         changeSelectedCommunity,
                         imagePlaceholderLink,
                         showCommunitySelectionButton,
                         disableCommunitySelectionButton,
                        }) => {

    const [ modalOpen, setModalOpen ] = useState();

    return (
        <>
            <h4 for="" class="field-label-class invenio-field-label">
                <Icon name="users" />
                Resource type
            </h4>
            {community ? (
              <>
                <div className="page-subheader-element">
                  <Image
                    size="tiny"
                    className="community-header-logo"
                    src={community.links?.logo || imagePlaceholderLink} // logo is undefined when new draft and no selection
                    fallbackSrc={imagePlaceholderLink}
                  />
                </div>
                <div className="page-subheader-element flex align-items-center">
                  {community.metadata.title}
                </div>
              </>
            ) : (
              <div className="page-subheader-element">
                {i18next.t(
                  "Select a community where you want your record to be published."
                )}
              </div>
            )}

            <div className="community-field-element rel-ml-1">
              {showCommunitySelectionButton && (
                <>
                  <CommunitySelectionModal
                    onCommunityChange={(community) => {
                      changeSelectedCommunity(community);
                      setModalOpen(false);
                    }}
                    onModalChange={(value) => setModalOpen(value)}
                    modalOpen={modalOpen}
                    chosenCommunity={community}
                    displaySelected
                    trigger={
                      <Button
                        className="community-field-button"
                        disabled={disableCommunitySelectionButton}
                        onClick={() => this.setState({ modalOpen: true })}
                        primary
                        name="setting"
                        type="button"
                        content={
                          community
                            ? i18next.t("Change")
                            : i18next.t("Select a community")
                        }
                      />
                    }
                  />
                  {community && (
                    <Button
                      basic
                      className="community-field-button ml-5"
                      onClick={() => changeSelectedCommunity(null)}
                      content={i18next.t("Remove")}
                      icon="close"
                      disabled={disableCommunitySelectionButton}
                    />
                  )}
                </>
              )}
            </div>
        </>
    )
}

CommunityFieldComponent.propTypes = {
  imagePlaceholderLink: PropTypes.string.isRequired,
  community: PropTypes.object,
  disableCommunitySelectionButton: PropTypes.bool.isRequired,
  showCommunitySelectionButton: PropTypes.bool.isRequired,
  showCommunityHeader: PropTypes.bool.isRequired,
  changeSelectedCommunity: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => ({
  community: state.deposit.editorState.selectedCommunity,
  disableCommunitySelectionButton:
    state.deposit.editorState.ui.disableCommunitySelectionButton,
  showCommunitySelectionButton:
    state.deposit.editorState.ui.showCommunitySelectionButton,
  showCommunityHeader: state.deposit.editorState.ui.showCommunityHeader,
});

const mapDispatchToProps = (dispatch) => ({
  changeSelectedCommunity: (community) => dispatch(changeSelectedCommunity(community)),
});

export const CommunityField = connect(
  mapStateToProps,
  mapDispatchToProps
)(CommunityFieldComponent);
