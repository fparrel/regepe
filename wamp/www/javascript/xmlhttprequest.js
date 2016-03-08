// Provide the XMLHttpRequest class for IE 5.x-6.x:
// Other browsers (including IE 7.x-8.x) ignore this
//   when XMLHttpRequest is predefined
if (typeof XMLHttpRequest == "undefined") {
  XMLHttpRequest = function () {
    try { return new ActiveXObject("Msxml2.XMLHTTP.6.0"); }
      catch (e1) {}
    try { return new ActiveXObject("Msxml2.XMLHTTP.3.0"); }
      catch (e2) {}
    try { return new ActiveXObject("Msxml2.XMLHTTP"); }
      catch (e3) {}
    try { return new ActiveXObject("Microsoft.XMLHTTP"); }
      catch (e4) {}
    throw new Error("This browser does not support XMLHttpRequest.");
  };
}
