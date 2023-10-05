import React from "react";
import i18next from "i18next";
import Creatibutors from "./components/Creatibutors";

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


const DetailMainContent = ({community,
                            customFieldsUi,
                            externalResources,
                            files,
                            isDraft,
                            isPreview,
                            record,
                            request,
                            permissions,
                            iconsRor,
                            iconsGnd,
                            iconsHcUsername,
                            iconsOrcid,
                            landingUrls}) => {
    return (
      <>
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
      </>
    );
};

export default DetailMainContent;