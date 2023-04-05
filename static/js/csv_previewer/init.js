/*
 * This file is part of Invenio.
 * Copyright (C) 2015-2019 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

requirejs(['js/csv_previewer/csv_d3js', 'js/csv_previewer/loader'], function(CSV_D3JS, Loader) {
  $(function () {
    $("[data-csv-source]").each(function () {
      CSV_D3JS.attachTo($(this));
    });
    $("[data-csv-target]").each(function () {
      Loader.attachTo($(this));
    });
  });
})
