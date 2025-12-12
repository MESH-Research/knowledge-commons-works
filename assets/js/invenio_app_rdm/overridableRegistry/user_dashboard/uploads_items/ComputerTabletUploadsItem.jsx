/*
 * This file is part of Knowledge Commons Works.
 *   Copyright (C) 2024 Mesh Research.
 *
 * Knowledge Commons Works is based on InvenioRDM, and
 * this file is based on code from InvenioRDM. InvenioRDM is
 *   Copyright (C) 2020-2024 CERN.
 *   Copyright (C) 2020-2024 Northwestern University.
 *   Copyright (C) 2020-2024 T U Wien.
 *
 * InvenioRDM and Knowledge Commons Works are both free software;
 * you can redistribute and/or modify them under the terms of the
 * MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/kcworks/i18next";
import React from "react";
import PropTypes from "prop-types";
import _truncate from "lodash/truncate";
import _get from "lodash/get";
import { Button, Grid, Icon, Item, Label } from "semantic-ui-react";
import { SearchItemCreators } from "@js/invenio_app_rdm/utils";
import { CompactStats } from "../../search/records_list_item_components/CompactStats";
import { DisplayPartOfCommunities } from "../../search/records_list_item_components/DisplayPartOfCommunities";

i18next.options.interpolation.escapeValue = false;

const ComputerTabletUploadsItem = ({
	result,
	editRecord,
	statuses,
	access,
	uiMetadata,
}) => {
	const { accessStatusId, accessStatus, accessStatusIcon } = access;
	const {
		descriptionStripped,
		title,
		creators,
		subjects,
		publicationDate,
		resourceType,
		createdDate,
		version,
		versions,
		isPublished,
		viewLink,
		publishingInformation,
		filters,
		allVersionsVisible,
		numOtherVersions,
	} = uiMetadata;

	console.log("result", result);

	const icon = isPublished ? (
		<Icon name="check" className="positive" />
	) : (
		<Icon name="upload" className="negative" />
	);
	const uniqueViews = _get(result, "stats.all_versions.unique_views", 0);
	const uniqueDownloads = _get(
		result,
		"stats.all_versions.unique_downloads",
		0,
	);
	console.log("i18next instance:", i18next);
	console.log("i18next options:", i18next.options);
	console.log("i18next version:", i18next.version);
	return (
		<Item key={result.id} className="search-result flex">
			{/* <div className="status-icon mr-10">
        <Item.Content verticalAlign="top">
          <div className="status-icon mt-5">{icon}</div>
        </Item.Content>
      </div> */}
			<Item.Content>
				{/* FIXME: Uncomment to enable themed banner */}
				{/* <DisplayVerifiedCommunity communities={result.parent?.communities} /> */}
				<Item.Extra className="labels-actions">
					{result.status in statuses && (
						<Label
							horizontal
							size="small"
							icon={icon}
							className={statuses[result.status].color}
						>
							{statuses[result.status].title}
						</Label>
					)}
					{result.status === "published" && result.is_draft === true ? (
						<Label
							horizontal
							size="small"
							icon={icon}
							className={statuses["draft"].color}
						>
							{statuses["draft"].title} changes
						</Label>
					) : null}
					<span className="status-icon ml-5 mt-5">{icon}</span>
					<Button
						compact
						size="small"
						floated="right"
						onClick={() => editRecord()}
						labelPosition="left"
						icon="edit"
						content={i18next.t("Edit")}
					/>
				</Item.Extra>
				<Item.Header as="h2">
					<a href={viewLink}>{title}</a>
				</Item.Header>
				<Item className="creatibutors">
					<Icon name={`${creators.length === 1 ? "user" : "users"}`} />{" "}
					<SearchItemCreators creators={creators} othersLink={viewLink} />
				</Item>
				<Item.Description>
					{_truncate(descriptionStripped, { length: 350 })}
				</Item.Description>
				<Item.Extra className="item-footer ui grid">
					<Grid.Column
						mobile={16}
						tablet={11}
						computer={11}
						className="item-footer-left"
					>
						{subjects.map((subject) => (
							<Label key={subject.title_l10n} size="tiny">
								{subject.title_l10n}
							</Label>
						))}
						<p>
							<Label horizontal size="small" className="">
								{publicationDate} ({version})
							</Label>
							<Label horizontal size="small" className="">
								{resourceType}
							</Label>
							<Label
								horizontal
								size="small"
								className={`basic access-status ${accessStatusId}`}
							>
								{accessStatusIcon && <Icon name={accessStatusIcon} />}
								{accessStatus}
							</Label>
							{/* {createdDate && publishingInformation && " | "} */}
						</p>

						{publishingInformation && (
							<p>
								{i18next.t("Published in:")} {publishingInformation}
							</p>
						)}

						{!allVersionsVisible && versions.index > 1 && (
							<p>
								<b>
									{i18next.t("{{count}} more versions exist for this record", {
										count: numOtherVersions,
									})}
								</b>
							</p>
						)}

						<DisplayPartOfCommunities
							communities={result.parent?.communities}
						/>
					</Grid.Column>

					<Grid.Column
						mobile={16}
						tablet={5}
						computer={5}
						className="item-footer-right"
					>
						{result.is_draft === false ? (
							<small>
								<CompactStats
									uniqueViews={uniqueViews}
									uniqueDownloads={uniqueDownloads}
								/>
							</small>
						) : null}
						{createdDate && (
							<small className="created-date">
								{i18next.t("Uploaded on {{uploadDate}}", {
									uploadDate: createdDate,
								})}
							</small>
						)}
					</Grid.Column>
				</Item.Extra>
			</Item.Content>
		</Item>
	);
};

ComputerTabletUploadsItem.propTypes = {
	result: PropTypes.object.isRequired,
	editRecord: PropTypes.func.isRequired,
	statuses: PropTypes.object.isRequired,
	access: PropTypes.object.isRequired,
	uiMetadata: PropTypes.object.isRequired,
};

export { ComputerTabletUploadsItem };
