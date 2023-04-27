function setFontSize(n) {
  document.body.style.fontSize = n + "px";
}

function setLeftAndRightMargin(margin) {
  // Sets l and r margin to "margin"
  document.body.style.marginLeft = 10 * margin + "px";
  document.body.style.marginRight = 10 * margin + "px";
}

function canScroll(el, scrollAxis) {
  if (0 === el[scrollAxis]) {
    el[scrollAxis] = 1;
    if (1 === el[scrollAxis]) {
      el[scrollAxis] = 0;
      return true;
    }
  } else {
    return true;
  }
  return false;
}

function isScrollableX(el) {
  return (
    el.scrollWidth > el.clientWidth &&
    canScroll(el, "scrollLeft") &&
    "hidden" !== getComputedStyle(el).overflowX
  );
}

function isScrollableY(el) {
  return (
    el.scrollHeight > el.clientHeight &&
    canScroll(el, "scrollTop") &&
    "hidden" !== getComputedStyle(el).overflowY
  );
}

function isScrollable(el) {
  return isScrollableX(el) || isScrollableY(el);
}

function fitImages() {
  // fits images into page
  var images = document.getElementsByTagName("img");
  for (var i = 0; i < images.length; i++) {
    images[i].style.maxWidth = "100%";
    images[i].style.maxHeight = "100vh";
    images[i].style.width = "auto";
    images[i].style.height = "auto";
  }
}
fitImages();

new QWebChannel(qt.webChannelTransport, function (channel) {
  var content = channel.objects.content;

  // set contents font size and margin to page
  setFontSize(content.fontSize_);
  setLeftAndRightMargin(content.margin_);

  // connect event listeners
  content.fontSizeChanged.connect(setFontSize);
  content.marginSizeChanged.connect(setLeftAndRightMargin);
  // content.pageChange.connect();
});
