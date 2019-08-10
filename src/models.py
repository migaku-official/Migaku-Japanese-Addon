from aqt import mw
import os
from os.path import dirname, join
from anki.stdmodels import models
from anki.hooks import addHook
from shutil import copyfile
modelList = []
name = 'MIA Japanese'
fields = ['Expression',  'Meaning', 'Audio', 'Audio on Front']

front = '''<div class="tags">
例文{{#Tags}}｜{{/Tags}}{{Tags}}</span>
</div>
{{^Audio on Front}}<span class="expression-field">{{Expression}}</span>{{/Audio on Front}}
{{#Audio on Front}}{{#Audio}}<span class="expression-field">{{Audio}}</span>{{/Audio}}{{/Audio on Front}}
{{#Audio on Front}}{{^Audio}}<span class="expression-field">{{Expression}}</span>{{/Audio}}{{/Audio on Front}}
'''

back = '''<div class="tags">
例文{{#Tags}}｜{{/Tags}}{{Tags}}</span>
</div>
{{#Audio on Front}}<span class="expression-field">{{Audio}}</span><hr>{{/Audio on Front}}
<span class="expression-field">{{Expression}}</span>
{{^Audio on Front}}<hr>{{/Audio on Front}}
{{^Audio on Front}}<div class="meaning-field">{{Meaning}}</div>{{/Audio on Front}}
{{#Audio on Front}}<div class="meaning-field padded-top">{{Meaning}}</div>{{/Audio on Front}}
{{^Audio on Front}}{{Audio}}{{/Audio on Front}}
'''

style = '''
.card {
 font-size: 23px;
 text-align: left;
 color: black;
 background-color: #FFFAF0;
 font-family: yuumichou;
}

@font-face {
font-family: yuumichou;
src: url(_yumin.ttf);
}

.tags {
font-family: yuumichou;
color: #585858;
}

.expression-field{
font-size: 30px; 
}

.meaning-field{
font-size: 25px;
}

.padded-top{
padding-top: 15px;
}

'''


modelList.append([name, fields, front, back])
def addModels():
    if mw.addonManager.getConfig(__name__)['AddMIAJapaneseTemplate'].lower() != 'on':
        return
    for model in modelList:
        if not mw.col.models.byName(model[0]):
            modelManager = mw.col.models
            newModel = modelManager.new(model[0])
            for fieldName in model[1]:
                field = modelManager.newField(fieldName)
                modelManager.addField(newModel, field)
            template = modelManager.newTemplate('Sentence')
            template['qfmt'] = model[2]
            template['afmt'] = model[3]
            newModel['css'] = style
            modelManager.addTemplate(newModel, template)
            modelManager.add(newModel)
            moveFontToMediaDir('_yumin.ttf')

def moveFontToMediaDir(filename):
    src = join(dirname(__file__), filename)
    if os.path.exists(src): 
        path = join(mw.col.media.dir(), filename)
        if not os.path.exists(path): 
            copyfile(src, path)
        return True
    else:
        return False