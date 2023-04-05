// This file is part of InvenioCommunities
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import { InvenioAdministrationCommunitiesApi } from "./api";
import { ErrorMessage } from "@js/invenio_communities/members/components/ErrorMessage";
import _get from "lodash/get";
import { DateTime } from "luxon";

import React, { Component } from "react";
import PropTypes from "prop-types";
import { withCancel } from "react-invenio-forms";
import { Header, Table, Loader } from "semantic-ui-react";
import {
  DeleteModalTrigger,
  DateFormatter,
  BoolFormatter,
} from "@js/invenio_administration";
import { i18next } from "@translations/invenio_communities/i18next";

export class FeaturedEntries extends Component {
  constructor(props) {
    super(props);
    this.state = { featuredList: undefined, loading: false, error: undefined };
  }

  componentDidMount() {
    this.fetchData();
  }

  fetchData = async () => {
    const { data } = this.props;
    try {
      this.setState({ loading: true });
      const cancellableFetch = withCancel(
        InvenioAdministrationCommunitiesApi.getFeatured(data.links.featured)
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
    const { data } = this.props;
    const now = DateTime.now();

    return (
      <>
        <Header as="h2">{i18next.t("Planned features")}</Header>
        {loading && <Loader active={loading} />}
        {error && <ErrorMessage error={error} />}
        {!loading && !error && (
          <Table celled striped collapsing>
            <Table.Header>
              <Table.HeaderCell>{i18next.t("Start date")}</Table.HeaderCell>
              <Table.HeaderCell>{i18next.t("Active")}</Table.HeaderCell>
              <Table.HeaderCell>{i18next.t("Actions")}</Table.HeaderCell>
            </Table.Header>
            <Table.Body>
              {featuredList?.hits?.hits.map((row) => {
                const deleteEndpoint = `${_get(data, "links.featured")}/${row.id}`;
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
                    <Table.Cell>
                      <BoolFormatter
                        icon="star"
                        color="yellow"
                        value={startDate <= now}
                      />
                    </Table.Cell>
                    <Table.Cell>
                      <DeleteModalTrigger
                        title={`feature of ${data.slug} `}
                        resourceName={data.slug}
                        resource={data}
                        successCallback={this.fetchData}
                        apiEndpoint={deleteEndpoint}
                      />
                    </Table.Cell>
                  </Table.Row>
                );
              })}
            </Table.Body>
          </Table>
        )}
      </>
    );
  }
}

FeaturedEntries.propTypes = {
  data: PropTypes.object.isRequired,
};
