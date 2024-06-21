import { i18next } from "@translations/invenio_communities/i18next";

export const memberVisibilityTypes = [
  {
    name: "public",
    visible: true,
    title: i18next.t("Public"),
    description: i18next.t("Your community membership is visible to everyone."),
  },
  {
    name: "hidden",
    visible: false,
    title: i18next.t("Hidden"),
    description: i18next.t(
      "Your community membership is only visible to other members of the community."
    ),
  },
];
