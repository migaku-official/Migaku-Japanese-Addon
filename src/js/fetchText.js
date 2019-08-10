function fetchText() {
  const sel = window.getSelection();
  const field = get_field(sel);
  const text = field.innerHTML;
  pycmd("textToJReading:||:||:" + text + ':||:||:' +  currentField.id.substring(1) + ':||:||:' + currentNoteId);

  
}
try {
  fetchText();
} catch (e) {
  alert(e);
}
