*ActiveFields*:  This is where you specify which fields you want the add-on to function in.
The syntax is: "DisplayType;ProfileName;NoteType;CardType;FieldName;Side"
There are eight different display types: "kanji", "coloredkanji", "kanjireading", "coloredkanjireading", "hover", "coloredhover", "reading", and "coloredreading".
The Profile Name can be set to "all" to function on all profiles.
The Side can be set to "front", "back", or "both".

*AddMigakuJapaneseTemplate*: "on" or "off", tells the add-on whether to create the "Migaku Japanese" note type or not.

*AudioFields*: "FieldName;ExportType(;delimiter)"
The Field Name can be set to any field in your collection, if that field exists on a particular card then the audio link(s) will automatically be exported to that field. If you set Field Name to "clipboard" the link to the audio file(s) will be copied to the clipboard.
There are 3 export types "overwrite", "add", and "no".
"overwrite" will overwrite whatever is in the destination field.
"add" will add the audio link(s) to the field (a delimiter can be specified, the default delimiter is one line break "&lt;br&gt;", you could for example change the delimiter to something like "&lt;br&gt;Audio:")
The last option "no" will only add the audio link(s) to the field when it is empty.
If the "PitchGraphFields" field option is the same as the AudioFields option then the former's ExportType takes priority.

*AutoCssJsGeneration*: "on" or "off", tells the add-on whether or not to keep config options in sync with card template's CSS and Javascript. Leave this on unless you understand how to edit these areas yourself.

*BufferedOutput*: "on" or "off", tells the add-on whether to slowly load a card, this is for slower machines or for cards with a huge amount of text. This option is experimental and it is recommended that the user keeps text on their cards to a moderate length.

*ColorsHANOK*: These are the CSS colors for the five pitch accent types; "Heiban", "Atamadaka", "Nakadaka", "Odaka", and "Kifuku".

*DisplayShapes*: "on" or "off", tells add-on whether add shapes signifying a word's alternate pitch accents after a word on the "coloredkanji", "coloredreading", and "coloredkanjireading" Display Type options.

*FuriganaFontSize*: A number from 1 - 10, without parentheses, this is the font-size of the furigana relative to the size of the regular font. For example 4 is equal to 40% the size of the regular font, 10 is 100%.

*GraphOnHover*: "on" or "off", tells add-on whether to display pitch accent graphs on hover.

*Group:Kana;DictForm;Pitch;Audio;Graphs*: These are the export options for the "文" button. 
The syntax is on/off;on/off;on/off;on/off;on/off, each option can be toggle by setting it to "on" or "off"
Kana is whether to export the regular regular kana readings for a word.
DictForm is whether or not to export an adjective or verb's dictionary form, note that a dictionary form is necessary in order to display a pitch graph for verbs as pitch graphs for conjugations are not supported at the current time.

*HistoricalConversion*: "kanji", "kana", or "both", this option tells whether to convert the kanji, kana or both of a text to its historical variant. The conversion takes place real time when viewing a card, if you find your cards behaving sluggishly I would suggest that you turn this option off, modern devices should not have much issues with real time conversion for text of moderate length however.

*Individual:Kana;DictForm;Pitch;Audio;Graphs*: These are the export options for the "語" button, which exports an individual word. 
The syntax is on/off;on/off;on/off;on/off;on/off, each option can be toggle by setting it to "on" or "off"
Kana is whether to export the regular regular kana readings for a word.
DictForm is whether or not to export an adjective or verb's dictionary form, note that a dictionary form is necessary in order to display a pitch graph for verbs as pitch graphs for conjugations are not supported at the current time.

*KatakanaConversion*: "on" or "off", whether or not to convert your card's text to katakana.

*LookAhead*: a number without parentheses, telling how many characters should be searched when using the individual word exporting functionality.

*PitchGraphFields*: "FieldName;ExportType(;delimiter)"
The Field Name can be set to any field in your collection, if that field exists on a particular card then the pitch graph(s) will automatically be exported to that field. If you set Field Name to "clipboard" the pitch graph(s) will be copied to the clipboard, graphs copied to the clipboard must be pasted into a field's html template, this template can be reached by pressing "Ctrl-X" when clicked within a field.
There are 3 export types "overwrite", "add", and "no".
"overwrite" will overwrite whatever is in the destination field.
"add" will add the pitch graph(s) to the field (a delimiter can be specified, the default delimiter is one line break "<br>", you could for example change the delimiter to something like "<br>Audio:")
The last option "no" will only add the pitch graph(s) to the field when it is empty.
If the "PitchGraphFields" field option is the same as the AudioFields option then the former's ExportType takes priority.

*Profiles*: These are the profiles that the add-on will be active on.
When set to "all", the add-on will be active on all profiles.
A user can specify specific profiles with the following syntax: "Profile1" (, "Profile2" , "Profile3")

