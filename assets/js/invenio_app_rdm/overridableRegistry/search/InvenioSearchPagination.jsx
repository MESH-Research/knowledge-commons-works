// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
// Copyright (C) 2025 KTH Royal Institute of Technology.
// Customized for Knowledge Commons Works
// Copyright (C) 2024 Mesh Research.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { Pagination, ResultsPerPage } from "react-searchkit";
import { Grid } from "semantic-ui-react";

export const InvenioSearchPagination = ({
	paginationOptions,
	total,
	perPageId,
}) => {
	const { maxTotalResults, resultsPerPage } = paginationOptions;
	return (
		<Grid.Row verticalAlign="middle">
			<Grid.Column
				className="computer tablet large-monitor only"
				width={3}
			></Grid.Column>
			<Grid.Column
				className="computer tablet large-monitor only pl-0 pr-0"
				width={10}
				textAlign="center"
			>
				<Pagination
					options={{
						showFirst: false,
						showLast: false,
						maxTotalResults,
					}}
				/>
			</Grid.Column>
			<Grid.Column
				className="mobile only pl-0 pr-0"
				width={16}
				textAlign="center"
			>
				<Pagination
					options={{
						boundaryRangeCount: 1,
						showFirst: false,
						showLast: false,
						maxTotalResults,
					}}
				/>
			</Grid.Column>
			<Grid.Column
				className="computer tablet large-monitor only pl-0"
				textAlign="right"
				width={3}
			>
				<ResultsPerPage values={resultsPerPage} perPageId={perPageId} />
			</Grid.Column>
			<Grid.Column
				className="mobile only rel-mt-2"
				textAlign="center"
				width={16}
			>
				<ResultsPerPage values={resultsPerPage} perPageId={perPageId} />
			</Grid.Column>
		</Grid.Row>
	);
};
