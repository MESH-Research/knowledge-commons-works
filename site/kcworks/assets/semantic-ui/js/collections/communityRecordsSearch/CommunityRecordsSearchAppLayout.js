import {
	SearchAppFacets,
	SearchAppResultsPane,
	SearchBar,
} from "@js/invenio_search_ui/components";
import { i18next } from "@translations/kcworks/i18next";
import React from "react";
import { Sort, buildUID, withState } from "react-searchkit";
import { Button, Container, Grid, Label, Icon } from "semantic-ui-react";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import PropTypes from "prop-types";

export const CommunityRecordsSearchAppLayout = ({
	config,
	appName,
	currentResultsState = {},
}) => {
	const [sidebarVisible, setSidebarVisible] = React.useState(false);
	const totalResults = currentResultsState.data?.total;
	const loading = currentResultsState.loading;

	return (
		<Container className="rel-pt-2">
			<Grid>
				<Grid.Row className="community-record-search-bar pb-10">
					<Grid.Column computer={12} tablet={16} mobile={16}>
						<SearchBar
							buildUID={buildUID}
							placeholder={i18next.t("Search records in collection...")}
						/>
					</Grid.Column>
					<Grid.Column
						width={4}
						className="computer widescreen large-monitor only"
					></Grid.Column>
				</Grid.Row>
				<Grid.Row
					verticalAlign="middle"
					className="community-record-search-options search-options-row pt-0"
				>
					<Grid.Column
						only="mobile tablet"
						mobile={2}
						tablet={1}
						className="pr-0"
					>
						<Button
							basic
							icon="sliders"
							onClick={() => setSidebarVisible(true)}
							aria-label={i18next.t("Filter results")}
						/>
					</Grid.Column>
					<Grid.Column mobile={10} tablet={6} computer={4}>
						<Sort
							values={config.sortOptions}
							label={(cmp) => (
								<>
									{/* <label className="mr-10">{i18next.t("Sort by")}</label> */}
									{cmp}
								</>
							)}
						/>
					</Grid.Column>
					<Grid.Column
						tablet={7}
						computer={8}
						mobile={4}
						textAlign="right"
						className="pl-0"
					>
						{!loading && totalResults > 0 && (
							<Label secondary>
								<Icon name="target" className="mobile only" />
								{totalResults.toLocaleString("en-US")}{" "}
								<span className="tablet computer widescreen large-monitor only">
									&nbsp;found
								</span>
							</Label>
						)}
					</Grid.Column>
					<Grid.Column
						width={4}
						className="computer widescreen large-monitor only"
					></Grid.Column>
				</Grid.Row>

				<Grid.Row>
					<Grid.Column mobile={16} tablet={16} computer={12}>
						<SearchAppResultsPane
							layoutOptions={config.layoutOptions}
							appName={appName}
						/>
					</Grid.Column>

					<GridResponsiveSidebarColumn
						width={4}
						open={sidebarVisible}
						onHideClick={() => setSidebarVisible(false)}
						// eslint-disable-next-line react/no-children-prop
						children={
							<>
								<h2 className="ui header mobile tablet only">
									{i18next.t("Search filters")}
								</h2>
								<SearchAppFacets aggs={config.aggs} appName={appName} />
							</>
						}
						computer={4}
						largeScreen={4}
						widescreen={4}
					/>
				</Grid.Row>
			</Grid>
		</Container>
	);
};

CommunityRecordsSearchAppLayout.propTypes = {
	config: PropTypes.object.isRequired,
	appName: PropTypes.string,
};

CommunityRecordsSearchAppLayout.defaultProps = {
	appName: "",
};

export const CommunityRecordsSearchAppLayoutWithState = withState(
	CommunityRecordsSearchAppLayout,
);
