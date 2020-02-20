function insertHTML(newHTML) {
  const sel = window.getSelection();
  const field = get_field(sel);
  selectAllFieldNodes(field, sel);
  setFormat("inserthtml", newHTML.trim());

}
try {

  insertHTML("%s");
} catch (e) {
  alert(e);
}
