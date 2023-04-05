/*
 * This file is part of Invenio.
 * Copyright (C) 2015-2019 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

var f = parent.document.getElementById('preview-iframe');
if (f) {
  var handleFullScreenClick = (function () {
    var isFullScreen = false;

    var pos = f.style.position,
        zIndex = f.style.zIndex,
        height = f.style.height,
        width = f.style.width,
        top = f.style.top,
        left = f.style.left,
        backgroundColor = f.style.backgroundColor;

    return function () {
      if (isFullScreen) {
        isFullScreen = false;
        f.style.position = pos;
        f.style.zIndex = zIndex;
        f.style.height = height;
        f.style.width = width;
        f.style.top = top;
        f.style.left = left;
        f.style.backgroundColor = backgroundColor;

        parent.document.body.style.overflow = "";
      } else {
        isFullScreen = true;
        f.style.position = "fixed";
        f.style.zIndex = 9999;
        f.style.height = "100%";
        f.style.width = "100%";
        f.style.top = 0;
        f.style.left = 0;
        f.style.backgroundColor="white";

        parent.document.body.style.overflow = "hidden";
      }
    };
  }());

  var fsbtn = f.contentDocument.getElementById('fullScreenMode');
  var secfsbtn = f.contentDocument.getElementById('secondaryFullScreenMode');
  if (fsbtn) fsbtn.addEventListener('click', handleFullScreenClick);
  if (secfsbtn) secfsbtn.addEventListener('click', handleFullScreenClick);
} else {
  var fsbtn = document.getElementById('fullScreenMode');
  var secfsbtn = document.getElementById('secondaryFullScreenMode');

  if (fsbtn) fsbtn.remove();
  if (secfsbtn) secfsbtn.remove();
}
