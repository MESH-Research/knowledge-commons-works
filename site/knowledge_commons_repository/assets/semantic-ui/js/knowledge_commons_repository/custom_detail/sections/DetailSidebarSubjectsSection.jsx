import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Keywords } from "../components/Keywords";
import { SubjectHeadings } from "../components/Subjects";

function DetailSidebarSubjectsSection({ record, showKeywords = true, show }) {
  const subjects = record.metadata.subjects;
  console.log("****DetailSidebarSubjectsSection record", subjects);

  const subjectHeadings = subjects?.filter((subject) => !!subject.scheme);
  const subjectLabels = subjectHeadings?.map(({ subject }) =>
    subject.toLowerCase()
  );

  const keywords = subjects
    ?.filter((subject) => !subject.scheme)
    ?.map(({ subject }) => subject)
    ?.concat(record.custom_fields["kcr:user_defined_tags"])
    ?.filter((keyword) => !subjectLabels.includes(keyword?.toLowerCase()));
  console.log("****DetailSidebarSubjectsSection keywords", keywords);

  // const groupedSubjects = subjectHeadings?.reduce((groups, subject) => {
  //   if (!groups[subject.scheme]) {
  //     groups[subject.scheme] = [];
  //   }
  //   groups[subject.scheme].push(subject);
  //   return groups;
  // }, {});

  return (
    <>
      {subjectHeadings?.length ? (
        <div
          id="subjects"
          className={`sidebar-container ${show}`}
          aria-label={i18next.t("Record subject headings")}
        >
          <h2 className="ui medium top attached header mt-0">
            {i18next.t("Subjects")}
          </h2>
          <SubjectHeadings
            passedClassNames="ui bottom attached segment rdm-sidebar pr-0 pt-0"
            subjectHeadings={subjectHeadings}
            keywords={keywords}
            showKeywords={showKeywords}
          />
        </div>
      ) : (
        ""
      )}
    </>
  );
}

export { DetailSidebarSubjectsSection };
