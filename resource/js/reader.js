new QWebChannel(qt.webChannelTransport, function (channel) {
  var content = channel.objects.content;

  // set contents font size and margin to page
  setFontSize(content.fontSize_);
  setLeftAndRightMargin(content.margin_);

  // connect event listeners
  content.fontSizeChanged.connect(setFontSize);
  content.marginSizeChanged.connect(setLeftAndRightMargin);
});

function setFontSize(n) {
  document.body.style.fontSize = n + "px";
}

function setLeftAndRightMargin(margin) {
  // Sets l and r margin to "margin"
  document.body.style.marginLeft = 10 * margin + "px";
  document.body.style.marginRight = 10 * margin + "px";
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

// function changeBackGroundColor(color) {
//   // change background color
//   document.body.style.background = color;
// }

// function changeColor(color) {
//   // change color of text
//   document.body.style.color = color;
// }

// function incrementFontSize(n) {
//   var currentSize = parseFloat(document.body.style.fontSize);
//   setFontSize(currentSize + n);
// }

// function setFontSize(n) {
//   document.body.style.fontSize = n + "px";
// }

// function setLeftAndRightMargin(margin) {
//   // Sets l and r margin to "margin"
//   document.body.style.marginLeft = margin + "px";
//   document.body.style.marginRight = margin + "px";
// }

// function incrementLeftAndRightMargin(n) {
//   // increaments l and r by "n"
//   var currentLeftMargin = parseInt(document.body.style.marginLeft) || 0;
//   var currentRightMargin = parseInt(document.body.style.marginRight) || 0;
//   setLeftAndRightMargin(currentLeftMargin + n);
// }
// function fitImages() {
//   // fits images into page
//   var images = document.getElementsByTagName("img");
//   for (var i = 0; i < images.length; i++) {
//     images[i].style.maxWidth = "100%";
//     images[i].style.maxHeight = "100vh";
//     images[i].style.width = "auto";
//     images[i].style.height = "auto";
//   }
// }
// fitImages();
