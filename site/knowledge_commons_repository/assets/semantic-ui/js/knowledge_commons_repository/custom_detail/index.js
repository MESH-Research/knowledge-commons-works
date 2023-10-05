import React from "react";
import ReactDOM from "react-dom";
import DetailMainContent from "./DetailMainContent";

const detailMainDiv = document.getElementById('detail-main-content');

ReactDOM.render(
    <DetailMainContent
    community={JSON.parse(detailMainDiv.dataset.community)}
    // currentMenu={JSON.parse(detailMainDiv.dataset.currentMenu)}
    // currentUser={JSON.parse(detailMainDiv.dataset.currentUser)}
    // currentUserprofile={JSON.parse(detailMainDiv.dataset.currentUserprofile)}
    customFieldsUi={JSON.parse(detailMainDiv.dataset.customFieldsUi)}
    externalResources={JSON.parse(detailMainDiv.dataset.externalResources)}
    files={JSON.parse(detailMainDiv.dataset.files)}
    // g={JSON.parse(detailMainDiv.dataset.g)}
    isDraft={JSON.parse(detailMainDiv.dataset.isDraft)}
    isPreview={JSON.parse(detailMainDiv.dataset.isPreview)}
    // badge_png
    // badge_svg
    // breadcrumbs
    // current_theme_icons
    // jwt
    // jwt_token
    record={JSON.parse(detailMainDiv.dataset.record)}
    // request={JSON.parse(detailMainDiv.dataset.request)}
    permissions={JSON.parse(detailMainDiv.dataset.permissions)}
    // search_app_communities_config
    // search_app_communities_invitations_config
    // search_app_communities_members_config
    // search_app_communities_records_config
    // search_app_communities_requests_config
    iconsRor={detailMainDiv.dataset.iconsRor}
    iconsOrcid={detailMainDiv.dataset.iconsOrcid}
    iconsGnd={detailMainDiv.dataset.iconsGnd}
    iconsHcUsername={detailMainDiv.dataset.iconsHcUsername}
    landingUrls={JSON.parse(detailMainDiv.dataset.landingUrls)}
    />,
    detailMainDiv
);