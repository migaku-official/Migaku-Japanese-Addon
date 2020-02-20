function insertHTMLToField(newHTML, ordinal) {
  const sel = window.getSelection();
  const field = document.getElementById('f' + ordinal);
  selectAllFieldNodes(field, sel);
  selectText(field, sel);
  setFormat("inserthtml", newHTML.trim());

}
try {

  insertHTMLToField("%s", "%s");
} catch (e) {
  alert(e);
}
