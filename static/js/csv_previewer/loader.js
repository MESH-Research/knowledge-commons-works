/*
 * This file is part of Invenio.
 * Copyright (C) 2015-2019 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
'use strict';

define(function(require) {

  var $ = require('node_modules/jquery/dist/jquery'),
      d3 = require('node_modules/d3/d3');

  return require('node_modules/flightjs/build/flight').component(Loader);

  function Loader() {
    var Loader;

    this.handleShowLoader = function (ev, data) {
      if (data.id === Loader.id){
        this.$node.show();
      }
    };

    this.handleHideLoader = function (ev, data) {
      if (data.id === Loader.id){
        this.$node.hide();
      }
    };

    this.after('initialize', function () {
      Loader = this;
      Loader.id = Loader.$node.data('csv-target');

      Loader.on(document, 'showLoader', Loader.handleShowLoader);
      Loader.on(document, 'hideLoader', Loader.handleHideLoader);
      Loader.on('click', function (ev) {
        ev.preventDefault();
        Loader.trigger(document, 'loadNext', {
          id: Loader.id
        });
      });

      Loader.$node.hide();
    });
  }

});
