import React from 'react';
import { i18next } from '@translations/invenio_app_rdm/i18next';
import {
  Tab
} from 'semantic-ui-react'
import { DetailMainTab } from './DetailMainTab';
import { DetailRightSidebar } from './DetailRightSidebar';
import { Creatibutors } from '../components/Creatibutors';

const RecordTitle = ({title}) => {
    return (
      <section
        id="record-title-section"
        aria-label={i18next.t('Record title and creators')}
      >
        <h1 id="record-title"
          className="wrap-overflowing-text"
        >
          {title}
        </h1>
      </section>
    );
};

const DetailContent = ({citationStyles,
                        citationStyleDefault,
                        community,
                        customFieldsUi,
                        doiBadgeUrl,
                        externalResources,
                        files,
                        hasPreviewableFiles,
                        iconsRor,
                        iconsGnd,
                        iconsHcUsername,
                        iconsOrcid,
                        isDraft,
                        isPreview,
                        landingUrls,
                        mainSections,
                        record,
                        permissions,
                        previewFile,
                        previewFileUrl,
                        sidebarSections,
                        totalFileSize
                          }) => {
    const panes = mainSections.map(({title, sections}) => {
      return ({
        menuItem: title,
        render: () => (
        <Tab.Pane
          key={title}
        >
          <DetailMainTab
              additional_descriptions={record.ui.additional_descriptions ? record.ui.additional_descriptions : null}
              citationStyles={citationStyles}
              citationStyleDefault={citationStyleDefault}
              description={record.metadata.description}
              files={files}
              hasFiles={record.files.enabled}
              hasPreviewableFiles={hasPreviewableFiles}
              isPreview={isPreview}
              permissions={permissions}
              previewFile={previewFile}
              previewFileUrl={previewFileUrl}
              record={record}
              subSections={sections}
              totalFileSize={totalFileSize}
          />
        </Tab.Pane>
        )
      })
    });

    return (
      <>

        <article className="sixteen wide tablet eleven wide computer column main-record-content">
          <RecordTitle title={record.metadata.title} />
          <Creatibutors
            creators={record.ui.creators}
            contributors={record.ui.contributors}
            iconsRor={iconsRor}
            iconsGnd={iconsGnd}
            iconsHcUsername={iconsHcUsername}
            iconsOrcid={iconsOrcid}
            landingUrls={landingUrls}
          />
          <Tab panes={panes} />
        </article>
        <DetailRightSidebar
          citationStyles={citationStyles}
          citationStyleDefault={citationStyleDefault}
          community={community}
          doiBadgeUrl={doiBadgeUrl}
          isPreview={isPreview}
          record={record}
          sidebarSections={sidebarSections}
        />
      </>
    );
};

export {
    DetailContent
};