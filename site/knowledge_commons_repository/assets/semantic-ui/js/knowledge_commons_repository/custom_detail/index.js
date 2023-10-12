import React from "react";
import ReactDOM from "react-dom";
import { DetailContent } from "./sections/DetailContent";
import { RecordVersionsList } from "./components/RecordVersionList";

const detailMainDiv = document.getElementById('detail-main-content');

ReactDOM.render(
    <DetailContent
    community={JSON.parse(detailMainDiv.dataset.community)}
    citationStyles={JSON.parse(detailMainDiv.dataset.citationStyles)}
    citationStyleDefault={detailMainDiv.dataset.citationStyleDefault}
    customFieldsUi={JSON.parse(detailMainDiv.dataset.customFieldsUi)}
    doiBadgeUrl={detailMainDiv.dataset.doiBadgeUrl}
    externalResources={JSON.parse(detailMainDiv.dataset.externalResources)}
    files={JSON.parse(detailMainDiv.dataset.files)}
    isDraft={JSON.parse(detailMainDiv.dataset.isDraft)}
    isPreview={JSON.parse(detailMainDiv.dataset.isPreview)}
    hasPreviewableFiles={JSON.parse(detailMainDiv.dataset.hasPreviewableFiles) === 'true' ? true : false}
    iconsRor={detailMainDiv.dataset.iconsRor}
    iconsOrcid={detailMainDiv.dataset.iconsOrcid}
    iconsGnd={detailMainDiv.dataset.iconsGnd}
    iconsHcUsername={detailMainDiv.dataset.iconsHcUsername}
    landingUrls={JSON.parse(detailMainDiv.dataset.landingUrls)}
    mainSections={JSON.parse(detailMainDiv.dataset.mainSections)}
    permissions={JSON.parse(detailMainDiv.dataset.permissions)}
    previewFile={JSON.parse(detailMainDiv.dataset.previewFile)}
    previewFileUrl={detailMainDiv.dataset.previewFileUrl}
    record={JSON.parse(detailMainDiv.dataset.record)}
    sidebarSections={JSON.parse(detailMainDiv.dataset.sidebarSections)}
    totalFileSize={detailMainDiv.dataset.totalFileSize}
    // badge_png
    // badge_svg
    // breadcrumbs
    // current_theme_icons
    // currentMenu={JSON.parse(detailMainDiv.dataset.currentMenu)}
    // currentUser={JSON.parse(detailMainDiv.dataset.currentUser)}
    // currentUserprofile={JSON.parse(detailMainDiv.dataset.currentUserprofile)}
    // g={JSON.parse(detailMainDiv.dataset.g)}
    // jwt
    // jwt_token
    // request={JSON.parse(detailMainDiv.dataset.request)}
    // search_app_communities_config
    // search_app_communities_invitations_config
    // search_app_communities_members_config
    // search_app_communities_records_config
    // search_app_communities_requests_config
    />,
    detailMainDiv
);