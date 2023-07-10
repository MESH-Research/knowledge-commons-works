import React, { Component } from "react";

import { Input, Array } from "react-invenio-forms";
import { Grid, Form, Button, Icon } from "semantic-ui-react";

const newSeries = {
  series_title: "",
  series_volume: "",
};

export const SeriesField = ({
      fieldPath, // injected by the custom field loader via the `field` config property
      series_title,
      series_volume,
      icon,
      description,
      label,
    }) => {

    return (
      <>
        <Grid.Column width="8">
        <Input
            fieldPath={`${fieldPath}.series_title`}
            label={series_title.label}
            icon={series_title.icon}
            placeholder={series_title.placeholder}
            description={series_title.description}
        ></Input>
        </Grid.Column>
        <Grid.Column width="8">
        <Input
            fieldPath={`${fieldPath}.series_volume`}
            label={series_volume.label}
            icon={series_volume.icon}
            placeholder={series_volume.placeholder}
            description={series_volume.description}
        ></Input>
        </Grid.Column>
      </>
    );
}