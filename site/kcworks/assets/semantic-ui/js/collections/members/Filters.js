import _upperFirst from "lodash/upperFirst";
import { i18next } from "@translations/invenio_communities/i18next";

export class Filters {
  constructor(configRoles) {
    this.configRoles = configRoles;
  }
  /*
   * Serializes a filter to be processed by ES
   * @param {String} type Name of the filter type in ES
   * @param {String} labelName Name of the label to be displayed
   * @param {Array.<{key: String, label: String}>} values The values as ES produce them
   */
  serializeFilter(type, labelName, values) {
    return { [type]: { buckets: values, label: labelName } };
  }

  getRoles() {
    const values = [];
    this.configRoles.forEach((role) => {
      values.push({ key: role.name, label: role.title });
    });
    return this.serializeFilter("role", "Role", values);
  }

  getVisibility() {
    const values = [
      { key: "true", label: "Public" },
      { key: "false", label: "Hidden" },
    ];
    return this.serializeFilter("visibility", "Visibility", values);
  }

  getStatus() {
    // This are the values that allow to filter for archived invitations
    const values = [
      { key: "submitted", label: i18next.t("Submitted") },
      { key: "accepted", label: i18next.t("Accepted") },
      { key: "declined", label: i18next.t("Declined") },
      { key: "cancel", label: i18next.t("Cancel") },
      { key: "expired", label: i18next.t("Expired") },
    ];
    return this.serializeFilter("status", "Status", values);
  }

  getInvitationFilters() {
    const statusFilters = this.getStatus();
    const rolesFilters = this.getRoles();
    return { ...rolesFilters, ...statusFilters };
  }

  getMembersFilters() {
    const visibilityFilters = this.getVisibility();
    const rolesFilters = this.getRoles();
    return { ...rolesFilters, ...visibilityFilters };
  }

  getHumanReadableVisibility(value) {
    return value === "true" ? "Public" : "Hidden";
  }

  getDisplayValue(filter) {
    const filterType = _upperFirst(filter[0]);
    let filterValue = _upperFirst(filter[1]);
    if (filter[0] === "visibility") {
      filterValue = this.getHumanReadableVisibility(filter[1]);
    }
    return `${filterType}: ${filterValue}`;
  }
}
