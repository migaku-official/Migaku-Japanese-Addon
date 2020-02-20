function removeBracketsFromSel(text) {
  if (text === "") return "";
  let pattern2 = /(\[sound:[^\]]+?\])|(?:\[\d*\])/g;
  if(!/\[[^\[]*?\]/.test(text))return text;
  let pattern = /<[^<]*?>/g;
  let matches = false;
  if (pattern.test(text)){
    matches = text.match(pattern)
    for (x in matches){
        text = text.replace(matches[x], '---NEWLINE___')
    }   
  }
  let matches2 = false;
  if (pattern2.test(text)){
    matches2 = text.match(pattern2)
    for (x in matches2){
        text = text.replace(matches2[x], '---SOUNDREF___')
    }   
  }

  text = cleanUpSpaces(text);
  if(matches){
    for (x in matches){
      text = text.replace( '---NEWLINE___', matches[x])
    } 
  }
  text = text.replace(/\[[^\[]*?\]/g, "");
  if(matches2){
    for (x in matches2){
      text = text.replace( '---SOUNDREF___', matches2[x])
    } 

  }
  return text;

}

function cleanUpSpaces(text){
      return text.replace(/ /g, '');
}

function wrapSelection(sel) {
    var range, html, wrapper;
    if (sel) {
        var wrapper = document.createElement("p");
        wrapper.classList.add('selection-wrapper')
        sel = window.getSelection();
        if(sel.toString().length < 2) return;
        if (sel.getRangeAt && sel.rangeCount) {
            range = sel.getRangeAt(0);
            return [range.startContainer,range.startOffset, range.endContainer, range.endOffset];
        }
    }
}

function selBrackDelete() {
  const sel = window.getSelection();
  var cur = get_field(sel);
  ogHtml = cur.innerHTML;
  var startCont, startOff, endCont, endOff;
  [startCont, startOff,endCont, endOff] = wrapSelection(sel);
  var offset = 0;
  if(startCont.isSameNode(endCont)) offset = 7;
  startCont.textContent = startCont.textContent.substring(0,startOff) + '--IND--' + startCont.textContent.substring(startOff);
  endCont.textContent = endCont.textContent.substring(0,endOff + offset) + '--IND--' + endCont.textContent.substring(endOff + offset);
  const range =  sel.toString().length;
  var selectedText = cur.innerHTML.match(/--IND--.+--IND--/)[0];
  var removedText = removeBracketsFromSel(selectedText);
  removedText = removedText.replace(/--IND--/g, '');
  const html= cur.innerHTML.replace(selectedText, removedText);
  cur.innerHTML = ogHtml;
  selectAllFieldNodes(cur, sel);
  setFormat("inserthtml", html);

}
try {
  selBrackDelete();
} catch (e) {
  alert(e);
}