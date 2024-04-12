// This file is part of InvenioCommunities
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import { InvenioAdministrationCommunitiesApi } from "./api";
import { DateTime } from "luxon";

import React, { Component } from "react";
import PropTypes from "prop-types";
import { withCancel } from "react-invenio-forms";
import { Header, Table, Loader, Modal } from "semantic-ui-react";
import { DateFormatter, BoolFormatter } from "@js/invenio_administration";
import { ErrorMessage } from "@js/invenio_communities/members/components/ErrorMessage";
import { i18next } from "@translations/invenio_communities/i18next";

export class FeatureModal extends Component {
  constructor(props) {
    super(props);
    this.state = { featuredList: undefined, loading: false, error: undefined };
  }

  componentDidMount() {
    this.fetchData();
  }

  fetchData = async () => {
    const { resource } = this.props;
    try {
      this.setState({ loading: true });
      const cancellableFetch = withCancel(
        InvenioAdministrationCommunitiesApi.getFeatured(resource.links.featured)
      );
      const featuredList = await cancellableFetch.promise;
      this.setState({ loading: false, featuredList: featuredList.data });
    } catch (e) {
      console.error(e);
      this.setState({ error: e, loading: false });
    }
  };

  render() {
    const { featuredList, loading, error } = this.state;
    const { children, modalOpen } = this.props;
    const now = DateTime.now();

    return (
      <Modal role="dialog" open={modalOpen}>
        <Modal.Content>
          <Header as="h2">{i18next.t("Planned features")}</Header>
          {loading && <Loader active={loading} />}
          {error && <ErrorMessage id="featured-community-errors" error={error} />}
          {!loading && !error && (
            <Table celled striped collapsing>
              <Table.Header>
                <Table.Row>
                  <Table.HeaderCell>{i18next.t("Start date")}</Table.HeaderCell>
                  <Table.HeaderCell>{i18next.t("Active")}</Table.HeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {featuredList?.hits?.hits.map((row) => {
                  const startDate = DateTime.fromISO(row.start_date);
                  return (
                    <Table.Row key={row.id}>
                      <Table.Cell
                        key={row.id}
                        data-label={row.id}
                        className="word-break-all"
                      >
                        <DateFormatter value={row.start_date} />
                      </Table.Cell>
                      <Table.Cell textAlign="center">
                        <BoolFormatter
                          icon="star"
                          color="yellow"
                          value={startDate <= now}
                        />
                      </Table.Cell>
                    </Table.Row>
                  );
                })}
              </Table.Body>
            </Table>
          )}
        </Modal.Content>
        {children}
      </Modal>
    );
  }
}

FeatureModal.propTypes = {
  resource: PropTypes.object.isRequired,
  children: PropTypes.node.isRequired,
  modalOpen: PropTypes.bool,
};

FeatureModal.defaultProps = {
  modalOpen: false,
};
