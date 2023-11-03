import React from "react";
import ReactDOM from "react-dom";
import { DetailContent } from "./sections/DetailContent";

const detailMainDiv = document.getElementById('detail-main-content');

ReactDOM.render(
    <DetailContent
    backPage={detailMainDiv.dataset.backPage}
    community={JSON.parse(detailMainDiv.dataset.community)}
    citationStyles={JSON.parse(detailMainDiv.dataset.citationStyles)}
    citationStyleDefault={detailMainDiv.dataset.citationStyleDefault}
    currentUserId={detailMainDiv.dataset.currentUserId}
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
    identifierSchemes={JSON.parse(detailMainDiv.dataset.identifierSchemes)}
    isPreviewSubmissionRequest={JSON.parse(detailMainDiv.dataset.isPreviewSubmissionRequest)}
    landingUrls={JSON.parse(detailMainDiv.dataset.landingUrls)}
    localizedStats={JSON.parse(detailMainDiv.dataset.localizedStats)}
    mainSections={JSON.parse(detailMainDiv.dataset.mainSections)}
    permissions={JSON.parse(detailMainDiv.dataset.permissions)}
    defaultPreviewFile={JSON.parse(detailMainDiv.dataset.defaultPreviewFile)}
    previewFileUrl={detailMainDiv.dataset.previewFileUrl}
    record={JSON.parse(detailMainDiv.dataset.record)}
    recordExporters={JSON.parse(detailMainDiv.dataset.recordExporters)}
    showDecimalSizes={JSON.parse(detailMainDiv.dataset.showDecimalSizes)}
    showRecordManagementMenu={JSON.parse(detailMainDiv.dataset.showRecordManagementMenu)}
    sidebarSectionsLeft={JSON.parse(detailMainDiv.dataset.sidebarSectionsLeft)}
    sidebarSectionsRight={JSON.parse(detailMainDiv.dataset.sidebarSectionsRight)}
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