import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Message, Statistic, Table, Popup, Icon } from "semantic-ui-react";
import { formatBytes } from "../util";

function StatsPopup({ number }) {
  // number[0] is truncated; number[1] is raw localized

  return number[0] != number[1] ? (
    <Popup
      trigger={
        <span
          className="compact-number"
          aria-label={i18next.t("See the full number")}
        >
          {number[0]}
        </span>
      }
      content={number[1]}
      position="top center"
      size="mini"
      flowing
    />
  ) : (
    number[0]
  );
}

function Analytics({
  hasFiles,
  localizedStats,
  record,
  showDecimalSizes,
  show,
}) {
  const all_versions = record?.stats?.all_versions;
  const this_version = record?.stats?.this_version;
  console.log("****Analytics record", record);
  console.log("****Analytics localizedStats", localizedStats);
  // Each value below is an array: [0] truncated localized value,
  // [1] non-truncated localized value
  const {
    all_versions_unique_downloads,
    this_version_unique_downloads,
    all_versions_unique_views,
    this_version_unique_views,
    all_versions_data_volume,
    this_version_data_volume,
  } = !!record.stats
    ? localizedStats
    : { undefined, undefined, undefined, undefined, undefined, undefined };
  const formattedDataVolumeAll = all_versions
    ? formatBytes(all_versions.data_volume)
    : undefined;
  const [formattedDataVolumeNum, formattedDataVolumeUnits] =
    formattedDataVolumeAll ? formattedDataVolumeAll.split(" ") : ["", ""];

  return (
    <div className={show}>
      {!record.stats ? (
        <Message>
          No statistics have been generated yet for this work. Check back later.
        </Message>
      ) : (
        <>
          <Statistic.Group size="small">
            <Statistic>
              <Statistic.Value>{all_versions_unique_views[1]}</Statistic.Value>
              <Statistic.Label>
                <Icon name="eye" />
                {i18next.t("Views")}
              </Statistic.Label>
            </Statistic>
            {hasFiles && (
              <>
                <Statistic>
                  <Statistic.Value>
                    {all_versions_unique_downloads[1]}
                  </Statistic.Value>
                  <Statistic.Label>
                    <Icon name="download" />
                    {i18next.t("Downloads")}
                  </Statistic.Label>
                </Statistic>
                <Statistic>
                  <Statistic.Value>{formattedDataVolumeNum}</Statistic.Value>
                  <Statistic.Label>
                    <Icon name="database" />
                    <span className="units">{formattedDataVolumeUnits}</span>
                    {` ${i18next.t("Downloaded")}`}
                  </Statistic.Label>
                </Statistic>
              </>
            )}
          </Statistic.Group>

          <Table id="record-statistics" definition fluid>
            <Table.Header>
              <Table.Row>
                <Table.HeaderCell />
                <Table.HeaderCell textAlign="right">
                  {i18next.t("All versions")}
                </Table.HeaderCell>
                <Table.HeaderCell textAlign="right">
                  {i18next.t("This version")}
                </Table.HeaderCell>
              </Table.Row>
            </Table.Header>

            <Table.Body>
              <Table.Row>
                <Table.Cell collapsing>
                  {i18next.t("Total views")}
                  <Popup
                    content={i18next.t(
                      "Times this work's page has been visited. Multiple visits by the same user within one hour are counted as a single view. Visits by robots (bots) are excluded."
                    )}
                    size="mini"
                    inverted
                    trigger={
                      <Icon
                        name="question circle"
                        aria-label={i18next.t("More info")}
                        size="small"
                      />
                    }
                  />
                </Table.Cell>
                <Table.Cell
                  data-label={i18next.t("All versions")}
                  textAlign="right"
                >
                  <StatsPopup number={all_versions_unique_views} />
                </Table.Cell>
                <Table.Cell
                  data-label={i18next.t("This version")}
                  textAlign="right"
                >
                  <StatsPopup number={this_version_unique_views} />
                </Table.Cell>
              </Table.Row>
              {hasFiles && (
                <>
                  <Table.Row>
                    <Table.Cell collapsing>
                      {i18next.t("Total downloads")}
                      <Popup
                        content={i18next.t(
                          "Times this work's files have been downloaded. For works with multiple files, this counts each file download separately. Repeated downloads of the same file by the same user are not counted if they occur within one hour."
                        )}
                        size="mini"
                        inverted
                        trigger={
                          <Icon
                            name="question circle"
                            aria-label={i18next.t("More info")}
                            size="small"
                          />
                        }
                      />
                    </Table.Cell>
                    <Table.Cell
                      data-label={i18next.t("All versions")}
                      textAlign="right"
                    >
                      <StatsPopup number={all_versions_unique_downloads} />
                    </Table.Cell>
                    <Table.Cell
                      data-label={i18next.t("This version")}
                      textAlign="right"
                    >
                      <StatsPopup number={this_version_unique_downloads} />
                    </Table.Cell>
                  </Table.Row>
                  <Table.Row collapsing>
                    <Table.Cell>
                      {i18next.t("Total download volume")}
                      <Popup
                        content={i18next.t(
                          "Total volume of all file downloads for this work. This excludes double clicks and downloads made by robots (bots)."
                        )}
                        size="mini"
                        inverted
                        trigger={
                          <Icon
                            name="question circle"
                            aria-label={i18next.t("More info")}
                            size="small"
                          />
                        }
                      />
                    </Table.Cell>
                    {/* FIXME: use showBinarySizes flag to control display */}
                    <Table.Cell
                      data-label={i18next.t("All versions")}
                      textAlign="right"
                    >
                      {formatBytes(all_versions.data_volume)}
                    </Table.Cell>
                    <Table.Cell
                      data-label={i18next.t("This version")}
                      textAlign="right"
                    >
                      {formatBytes(this_version.data_volume)}
                    </Table.Cell>
                  </Table.Row>
                </>
              )}
            </Table.Body>
          </Table>

          <p className="text-muted">
            <a href="/help/statistics">
              {i18next.t("More info on how stats are collected")}...
            </a>
          </p>
        </>
      )}
    </div>
  );
}

export { Analytics };

// {% macro stats_popup(number) %}
//   {% if number|truncate_number(max_value=10_000_000) != number|localize_number %}
//   <div>
//     <span
//       tabindex="0"
//       role="button"
//       class="popup-trigger compact-number"
//       aria-expanded="false"
//       aria-label="{{ _('See the full number') }}"
//       data-variation="mini"
//     >
//       {{ number|truncate_number(max_value=10_000_000) }}
//     </span>
//     <p role="tooltip" class="popup-content ui flowing popup transition hidden">
//       {{ number|localize_number }}
//     </p>
//   </div>
//   {% else %}
//     {{ number|truncate_number(max_value=10_000_000) }}
//   {% endif %}
// {% endmacro %}

{
  /* <div class="ui tiny two statistics rel-mt-1">
  {% set all_versions = record.stats.all_versions %}
  {% set this_version = record.stats.this_version %}

  <div class="ui statistic">
    <div class="value">{{ all_versions.unique_views|compact_number(max_value=1_000_000) }}</div>
    <div class="label">
      <i aria-hidden="true" class="eye icon"></i>
      {{ _("Views") }}
    </div>
  </div>

  <div class="ui statistic">
    <div class="value">{{ all_versions.unique_downloads|compact_number(max_value=1_000_000) }}</div>
    <div class="label">
      <i aria-hidden="true" class="download icon"></i>
      {{ _("Downloads") }}
    </div>
  </div>
</div>

<div class="ui container rel-mt-2 centered">
  <table id="record-statistics" class="ui definition table fluid">
    <thead>
      <tr>
        <th></th>
        <th class="right aligned">{{ _("All versions") }}</th>
        <th class="right aligned">{{ _("This version") }}</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          {{ _("Views") }}
          <i
            tabindex="0"
            role="button"
            style="position:relative"
            class="popup-trigger question circle small icon"
            aria-expanded="false"
            aria-label="{{ _('More info') }}"
            data-variation="mini inverted"
          >
          </i>
          <p role="tooltip" class="popup-content ui flowing popup transition hidden">
            {{ _('Total views') }}
          </p>
        </td>
        <td data-label="{{_('All versions')}}" class="right aligned">{{ stats_popup(all_versions.unique_views) }}</td>
        <td data-label="{{_('This version')}}" class="right aligned">{{ stats_popup(this_version.unique_views) }}</td>
      </tr>
      <tr>
        <td>
          {{ _("Downloads") }}
          <i
            tabindex="0"
            role="button"
            style="position:relative"
            class="popup-trigger question circle small icon"
            aria-expanded="false"
            aria-label="{{ _('More info') }}"
            data-variation="mini inverted"
          >
          </i>
          <p role="tooltip" class="popup-content ui flowing popup transition hidden">
            {{ _('Total downloads') }}
          </p>
        </td>
        <td data-label="{{_('All versions')}}" class="right aligned">{{ stats_popup(all_versions.unique_downloads) }}</td>
        <td data-label="{{_('This version')}}" class="right aligned">{{ stats_popup(this_version.unique_downloads) }}</td>
      </tr>
      <tr>
        <td>
          {{ _("Data volume") }}
          <i
            tabindex="0"
            role="button"
            style="position:relative"
            class="popup-trigger question circle small icon"
            aria-expanded="false"
            aria-label="{{ _('More info') }}"
            data-variation="mini inverted"
          >
          </i>
          <p role="tooltip" class="popup-content ui flowing popup transition hidden">
            {{ _('Total data volume') }}
          </p>
        </td>
        {%- set binary_sizes = not config.APP_RDM_DISPLAY_DECIMAL_FILE_SIZES %}

        <td data-label="{{_('All versions')}}" class="right aligned">{{ all_versions.data_volume|filesizeformat(binary=binary_sizes) }}</td>
        <td data-label="{{_('This version')}}" class="right aligned">{{ this_version.data_volume|filesizeformat(binary=binary_sizes) }}</td>
      </tr>
    </tbody>
  </table>


  <p class="text-muted">
    <a href="/help/statistics">{{ _("More info on how stats are collected.") }}...</a>
  </p>
</div> */
}
