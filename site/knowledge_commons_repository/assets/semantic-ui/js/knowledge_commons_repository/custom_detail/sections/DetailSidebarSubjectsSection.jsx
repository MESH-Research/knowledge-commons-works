import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { SubjectHeadings } from "../components/Subjects";

function DetailSidebarSubjectsSection({ record }) {
  const subjects = record.metadata.subjects;
  console.log("****DetailSidebarSubjectsSection record", subjects);

  const keywords = subjects?.filter((subject) => !subject.scheme);
  console.log("****DetailSidebarSubjectsSection keywords", keywords);

  const subjectHeadings = subjects?.filter((subject) => !!subject.scheme);

  const groupedSubjects = subjectHeadings?.reduce((groups, subject) => {
    if (!groups[subject.scheme]) {
      groups[subject.scheme] = [];
    }
    groups[subject.scheme].push(subject);
    return groups;
  }, {});
  console.log(
    "****DetailSidebarSubjectsSection groupedSubjects",
    groupedSubjects
  );

  return (
    <>
      {subjectHeadings?.length ? (
        <div
          id="subjects"
          className="sidebar-container"
          aria-label={i18next.t("Record subject headings")}
        >
          <h2 className="ui medium top attached header mt-0">
            {i18next.t("Subjects")}
          </h2>
          <SubjectHeadings
            passedClassNames="ui bottom attached segment rdm-sidebar pr-0 pt-0"
            subjectHeadings={subjectHeadings}
          />
          {keywords.length ? (
            <>
              <h2 className="ui heading tiny">User-defined Keywords</h2>
              <SubjectHeadings
                passedClassNames="ui bottom attached segment rdm-sidebar pr-0 pt-0"
                subjectHeadings={keywords}
              />
            </>
          ) : (
            ""
          )}
        </div>
      ) : (
        ""
      )}
    </>
  );
}

export { DetailSidebarSubjectsSection };
