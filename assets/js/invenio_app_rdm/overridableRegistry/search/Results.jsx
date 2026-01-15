/*
 * This file is part of Invenio.
 * Copyright (C) 2020 CERN.
 * Copyright (C) 2021 Graz University of Technology.
 * Customized for Knowledge Commons Works
 * Copyright (C) 2024 Mesh Research.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import Overridable from "react-overridable";
import React, { useContext } from "react";
import { ResultsMultiLayout, ResultsList, ResultsGrid } from "react-searchkit";
import { Grid } from "semantic-ui-react";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components/context";
import { InvenioSearchPagination } from "./InvenioSearchPagination";

const Results = ({ currentResultsState = {} }) => {
	const { total } = currentResultsState.data;
	const { sortOptions, layoutOptions, paginationOptions, buildUID } =
		useContext(SearchConfigurationContext);
	const multipleLayouts = layoutOptions.listView && layoutOptions.gridView;
	return (
		(total || null) && (
			<Grid relaxed>
				{/* Top pagination */}
				<InvenioSearchPagination
					paginationOptions={paginationOptions}
					perPageId="top-pager"
				/>

				{/* Results list */}
				<Grid.Row>
					<Grid.Column>
						{multipleLayouts ? (
							<ResultsMultiLayout />
						) : layoutOptions.listView ? (
							<ResultsList />
						) : (
							<ResultsGrid />
						)}
					</Grid.Column>
				</Grid.Row>

				{/* Bottom pagination */}
				<InvenioSearchPagination
					paginationOptions={paginationOptions}
					perPageId="bottom-pager"
				/>
			</Grid>
		)
	);
};
export { Results };
