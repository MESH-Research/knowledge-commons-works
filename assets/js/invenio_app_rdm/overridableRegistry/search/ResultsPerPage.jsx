/*
 * This file is part of React-SearchKit.
 * Copyright (C) 2018-2022 CERN.
 * Customized for Knowledge Commons Works
 * Copyright (C) 2024 Mesh Research.
 *
 * React-SearchKit and Knowledge Commons Works are free software; you
 * can redistribute and/or modify them
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import PropTypes from "prop-types";
import React from "react";
import { withState } from "react-searchkit";
import { Dropdown } from "semantic-ui-react";
import { i18next } from "@translations/kcworks/i18next";

const ResultsPerPageComponent = ({
	values,
	perPageId,
	selectOnNavigation,
	showWhenOnlyOnePage,
	/* Redux from withState */
	currentQueryState,
	currentResultsState,
	updateQueryState,
}) => {
	const loading = currentResultsState.loading;
	const currentSize = currentQueryState.size;
	const totalResults = currentResultsState.data.total;

	const onChange = (value) => {
		if (value === currentSize) return;
		updateQueryState({ size: value });
	};

	const options = values.map((value) => ({
		key: value.text,
		text: value.text,
		value: value.value,
	}));

	const dropdownId = `results-per-page-${perPageId || "default"}`;
	const labelId = `${dropdownId}-label`;

	return loading ||
		currentSize === -1 ||
		!(showWhenOnlyOnePage
			? totalResults > 0
			: totalResults > currentSize) ? null : (
		<div className="invenio-search results-per-page">
			<Dropdown
				id={dropdownId}
				inline
				compact
				options={options}
				value={currentSize}
				onChange={(_, { value }) => onChange(value)}
				aria-labelledby={labelId}
				selectOnNavigation={selectOnNavigation}
			/>
			<label id={labelId} htmlFor={dropdownId} className="ml-5">
				<span className="mobile only">{i18next.t("results")} </span>
				{i18next.t("/ page")}
			</label>
		</div>
	);
};

ResultsPerPageComponent.propTypes = {
	values: PropTypes.array.isRequired,
	label: PropTypes.func,
	perPageId: PropTypes.string,
	selectOnNavigation: PropTypes.bool,
	showWhenOnlyOnePage: PropTypes.bool,
	/* Redux from withState */
	currentQueryState: PropTypes.object.isRequired,
	currentResultsState: PropTypes.object.isRequired,
	updateQueryState: PropTypes.func.isRequired,
};

ResultsPerPageComponent.defaultProps = {
	label: (cmp) => cmp,
	overridableId: "",
	selectOnNavigation: false,
	showWhenOnlyOnePage: true,
};

const ResultsPerPage = withState(ResultsPerPageComponent);

export default ResultsPerPage;
