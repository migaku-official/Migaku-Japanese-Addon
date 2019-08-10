function insertHTML(newHTML) {
  const sel = window.getSelection();
  const field = get_field(sel);
  field.innerHTML = '';
  setFormat("inserthtml", newHTML.trim());

}
try {

  insertHTML("%s");
} catch (e) {
  alert(e);
}
