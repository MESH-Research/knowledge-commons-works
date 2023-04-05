/*
 * This file is part of Invenio.
 * Copyright (C) 2015-2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import d3 from "d3";
import flight from "flightjs";

function CSV_D3JS() {
  var CSV_D3JS;

  this.tabulate = function(data, target, columns) {
    var table = d3
      .select(target)
      .append("table")
      .classed({
        table: true,
        "table-hover": true,
        "table-bordered": true,
      });
    CSV_D3JS.thead = table.append("thead");
    CSV_D3JS.tbody = table.append("tbody");
    CSV_D3JS.columns = columns;
    CSV_D3JS.data = data;

    // append the header row
    CSV_D3JS.thead
      .append("tr")
      .selectAll("th")
      .data(CSV_D3JS.columns)
      .enter()
      .append("th")
      .text(function(column) {
        return column;
      });

    CSV_D3JS.next = 1;
    CSV_D3JS.chunk_size = 500;
    CSV_D3JS.chunks = Math.ceil(CSV_D3JS.data.length / CSV_D3JS.chunk_size);

    CSV_D3JS.loadNext(undefined, {
      id: CSV_D3JS.id,
    });
    if (CSV_D3JS.chunks > 1) {
      CSV_D3JS.trigger(document, "showLoader", {
        id: CSV_D3JS.id,
      });
    }

    return true;
  };

  this.loadNext = function(ev, data) {
    if (data.id === CSV_D3JS.id && CSV_D3JS.next <= CSV_D3JS.chunks) {
      // create a row for each object in the data chunk
      CSV_D3JS.tbody
        .selectAll("tr")
        .data(CSV_D3JS.data.slice(0, CSV_D3JS.next * CSV_D3JS.chunk_size))
        .enter()
        .append("tr")
        .selectAll("td")
        .data(function(row) {
          return CSV_D3JS.columns.map(function(column) {
            return { column: column, value: row[column] };
          });
        })
        .enter()
        .append("td")
        .text(function(d) {
          return d.value;
        });

      if (CSV_D3JS.next === CSV_D3JS.chunks) {
        CSV_D3JS.trigger(document, "hideLoader", {
          id: CSV_D3JS.id,
        });
      }
      CSV_D3JS.next += 1;
    }
  };

  this.after("initialize", function() {
    CSV_D3JS = this;
    CSV_D3JS.id = CSV_D3JS.node.id;

    var delimiter = CSV_D3JS.$node.data("csv-delimiter"),
      encoding = CSV_D3JS.$node.data("csv-encoding"),
      resource = CSV_D3JS.$node.data("csv-source"),
      dsv = d3.dsv(delimiter, "text/csv; charset=" + encoding);

    dsv(resource, function(data) {
      var col = Object.keys(data[0]);
      CSV_D3JS.tabulate(data, CSV_D3JS.node, col);
    });

    this.on(document, "loadNext", this.loadNext);
  });
}

export default flight.component(CSV_D3JS);
