function wrapSelection(sel) {
    var range, html, wrapper;
    if (sel) {
        var wrapper = document.createElement("p");
        wrapper.classList.add('selection-wrapper')
        sel = window.getSelection();
        if(sel.toString().length < 2) return [sel.anchorNode, sel.anchorOffset, false,false];
        if (sel.getRangeAt && sel.rangeCount) {
            range = sel.getRangeAt(0);
            return [range.startContainer,range.startOffset, range.endContainer, range.endOffset];
        }
    }
}

function fetchIndividual() {
  const sel = window.getSelection();
  var cur = get_field(sel);
  var ogHTML = cur.innerHTML;
  var startCont, startOff, endCont, endOff;
  [startCont, startOff,endCont, endOff] = wrapSelection(sel);
  if(endCont){
    var offset = 0;
    if(startCont.isSameNode(endCont)) offset = 7;
    startCont.textContent = startCont.textContent.substring(0,startOff) + '--IND--' + startCont.textContent.substring(startOff);
    endCont.textContent = endCont.textContent.substring(0,endOff + offset) + '--IND--' + endCont.textContent.substring(endOff + offset);
  }else{
    startCont.textContent = startCont.textContent.substring(0,startOff) + '--IND--' + startCont.textContent.substring(startOff);
  }
  const newHTML = cur.innerHTML;
  cur.innerHTML = ogHTML;  
  return pycmd("individualJExport:||:||:" + newHTML + ':||:||:' +  currentField.id.substring(1) + ':||:||:' + currentNoteId);
}

try {
  fetchIndividual();
} catch (e) {
  alert(e);
}finally {
  if(cur){
    document.getElementsByClassName('origin-word-class')[0].classList.remove('origin-word-class');
    cur.innerHTML = ogHTML;
  }
}
