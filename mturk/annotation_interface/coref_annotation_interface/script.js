'use strict';


/*
Event defintion
 */
function Event(sender) {
    this._sender = sender;
    this._listeners = [];
}

Event.prototype = {
    attach : function (listener) {
        this._listeners.push(listener);
    },
    notify : function (args) {
        var index;

        for (index = 0; index < this._listeners.length; index += 1) {
            this._listeners[index](this._sender, args);
        }
    },
    forwardEvent : function (nextEvent) {
        // forwards this events notifications to the nextEvent
        this.attach((sender, args) => nextEvent.notify(args));
    }
};

/*
End of Event definition
 */

// ----------------------------------------------------------------------

/*
Co-ref Annotation Model
*/ 

class CAModel {
    constructor(docJson) {
        this.docJson = docJson;
        this._annotationDS = getCADS(docJson);
    }

    get numSentences() {
        return _.size(this.docJson.sentences);
    }

    checkValidIdxs(sIdx, eIdx) {
        return (!_.isUndefined(this._annotationDS[sIdx]) &&
                !_.isUndefined(this._annotationDS[sIdx][eIdx])); 
    }

    getAnnotation(sIdx, eIdx) {
        if (!this.checkValidIdxs(sIdx, eIdx)) return null;
        return this._annotationDS[sIdx][eIdx]; 
    }

    toPostString() {
        // implement later
    }
}

/*
End of Co-ref Annotation Model
 */

// ----------------------------------------------------------------------

/*
Co-ref Annotation View 
*/

const MarkStates = _.keyBy([
    'SELECTED',
    'UNSELECTED_NOTDONE',
    'UNSELECTED_DONE',
    'UNSELECTED_ERROR',
    'HIGHLIGHTED',
    'DISABLED'
], _.identity)

const markStateToClass = {
    [MarkStates.SELECTED]: 'selected',
    [MarkStates.UNSELECTED_NOTDONE]: '',
    [MarkStates.UNSELECTED_DONE]: 'done',
    [MarkStates.UNSELECTED_ERROR]: 'error',
    [MarkStates.HIGHLIGHTED]: 'highlighted',
    [MarkStates.DISABLED]: 'disabled',
};


class CAView {

    constructor(caModel) {
        this._caModel = caModel;

        this._$docRoot = $('div#doc-view');
        this._renderDocInNode(caModel.docJson, this._$docRoot);

        // initialize disabled
        this._$noref = $('#no-ref').attr('class', markStateToClass[MarkStates.DISABLED]);
        this._norefMark = {$node: this._$noref, prevState: MarkStates.DISABLED, state: MarkStates.DISABLED};

        this._marksDict = this._createMarksDict(this._$docRoot);

        this.markClicked = new Event(this);
        this._registerClicksOnMark(this._marksDict, this._norefMark);

        this.currentFocus = null;
    }

    _registerClicksOnMark(marksDict, norefMark) {
        _.each(marksDict, (nestedDict, sIdx) => {
            _.each(nestedDict, (mark, eIdx) => {
                mark.$node.on('click', () => {
                    console.log(mark);
                    this.markClicked.notify( 
                        {mark, sIdx: parseInt(sIdx), eIdx: parseInt(eIdx), isNoRef: false} );
                });
            })
        });

        norefMark.$node.on('click', () => this.markClicked.notify({mark: norefMark, isNoRef: true}));
    }

    get marksDict() {
        return this._marksDict;
    }

    _createMarksDict($node) {
        let marksDict = {};
        $node.find('mark[data-entity]').each( (index, markNode) => {
            let $markNode = $(markNode);
            let sIdx = parseInt($markNode.attr('sent-id'));
            let eIdx = parseInt($markNode.attr('ent-id'));

            if (!_.has(marksDict, sIdx)) marksDict[sIdx] = {};
            marksDict[sIdx][eIdx] = 
                {$node: $markNode, state: MarkStates.UNSELECTED_NOTDONE, prevState: MarkStates.UNSELECTED_NOTDONE};
        } );
        return marksDict;
    }

    _setMarkState(mark, state) {
        if (!_.includes(_.values(MarkStates), state)) return;
        mark.$node.attr('class', markStateToClass[state]);
        mark.prevState = mark.state;
        mark.state = state;
    }

    _restoreMarkState(mark) {
        mark.$node.attr('class', markStateToClass[mark.prevState]);
        [mark.state, mark.prevState] = [mark.prevState, mark.start];
    }

    _dullSentence(sIdx) {
        this._$docRoot.find(`#sentence-${sIdx}`).css('opacity', .3);
    }

    _unDullSentence(sIdx) {
        this._$docRoot.find(`#sentence-${sIdx}`).css('opacity', 1);
    }

    focusOnMark(sIdx, eIdx) {
        if (!_.isNil(this.currentFocus)) this.unFocus();

        // set all mentions to UNSELECTED_NOTDONE
        _.each(this.marksDict, (nestedDict, thatSIdx) => {
            _.each(nestedDict, (mark, thatEIdx) => {
                if (parseInt(thatSIdx) != sIdx || parseInt(thatEIdx) != eIdx)
                    this._setMarkState(mark, MarkStates.UNSELECTED_NOTDONE)
            })
        });


        // highlight a previous selected mark if any
        const reference = this._caModel.getAnnotation(sIdx, eIdx);
        if (reference.isSet()) {
            const mark = (reference.isNoRef)
                         ? this._norefMark
                         : this.marksDict[reference.sIdx][reference.eIdx];
            this._setMarkState(mark, MarkStates.HIGHLIGHTED);
        }
        if (this._norefMark.state != MarkStates.HIGHLIGHTED)
            this._setMarkState(this._norefMark, MarkStates.UNSELECTED_NOTDONE);


        // disable marks in all the following sentences
        _.each(_.range(sIdx + 1, this._caModel.numSentences), (thatSIdx) => {
            this._dullSentence(thatSIdx);
            _.each(this.marksDict[thatSIdx], (mark) => this._setMarkState(mark, MarkStates.DISABLED))
        });


        // in the current sentence highlight marks before the current mark
        // and disable the ones which follow
        _.each(this.marksDict[sIdx], (mark, thatEIdx) => {
            if (thatEIdx > eIdx) this._setMarkState(mark, MarkStates.DISABLED)
        });
        this._setMarkState(this.marksDict[sIdx][eIdx], MarkStates.SELECTED);

        this.currentFocus = {sIdx, eIdx};
    }

    unFocus() {
        if (_.isNil(this.currentFocus)) return;
        
        _.each(this.marksDict, (nestedDict, sIdx) => {
            _.each(nestedDict, (mark, eIdx) => {
                const nextState = (this._caModel.getAnnotation(sIdx, eIdx).isSet())
                                  ? MarkStates.UNSELECTED_DONE : MarkStates.UNSELECTED_NOTDONE;
                this._setMarkState(mark, nextState);
            })
        });

        this._setMarkState(this._norefMark, MarkStates.DISABLED);

        _.each(_.range(parseInt(this.currentFocus.sIdx) + 1, this._caModel.numSentences),
               (sIdx) => this._unDullSentence(sIdx)
        );

        this.currentFocus = null;
    }

   //--------  doc load utilities ------------

    _getSentenceHTMLElement(sentence, sIdx) {
        // return string constructed with tokens and spaces in [start, end)
        const getTextFromSpanForTokenSpaces = (tsps, st, end) => 
            _(tsps).slice(st, end).reduce((acc, tsp) => (acc + tsp[0] + tsp[1]), '');

        const wrapTextInMark = (text, eIdx) => 
            (`<mark data-entity ent-id="${eIdx}" sent-id="${sIdx}">${text}</mark>`);

        // tuples of tokens, spaces ( => zip(tokens, spaces) )
        const tokenSpaces = _.isUndefined(sentence.spaces) ? 
            _.map(sentence.tokens, (t) => [t, " "]) :
            _.zip(sentence.tokens, sentence.spaces);

        const getTextFromSpan = _.partial(getTextFromSpanForTokenSpaces, tokenSpaces);

        const sentLen = tokenSpaces.length;
        const ents = sentence.ents;

        const sentNode = document.createElement('div');
        // now populate sentNode with sentence contents by iterating through ents
        if (ents.length == 0)
            sentNode.innerText = getTextFromSpan(0, sentLen);
        else {
            let sentInnerHTML = "";
            let lastEntEnd = 0;
            _.each(ents, (ent, eIdx) => {
                // add text before the entity
                sentInnerHTML += getTextFromSpan(lastEntEnd, ent.start);
                sentInnerHTML += wrapTextInMark(getTextFromSpan(ent.start, ent.end), eIdx);
                lastEntEnd = ent.end;
            });
            // add text after the last entity
            sentInnerHTML += getTextFromSpan(lastEntEnd, sentLen);
            sentNode.innerHTML = sentInnerHTML;
        }
        return sentNode;
    }

    _getDocHTMLNode(docJson) {
        // listItem template
        const sentTmpl = document.getElementById('sentence-template');
        let $group = $('<div>', {'class': 'list-group'});

        const _this = this;
        _.each(docJson['sentences'], (sentence, sIdx) => {
            let $sc = $(sentTmpl.content.cloneNode(true));
            $sc.find('div.sentence-content')
                .append(_this._getSentenceHTMLElement(sentence, sIdx));
            $sc.find('span.sentence-list-index').text(parseInt(sIdx)+1)

            let $li = $('<div>', {'class': 'list-group-item'}).
                append($sc).attr('id', 'sentence-'+sIdx);
            $group.append($li);
        });
        return $group[0];
    }

    _renderDocInNode(docJson, $node) {
        var docHtml = this._getDocHTMLNode(docJson);
        $node.append(docHtml);
    }

}

/*
End of Co-ref Annotation View 
*/

// ----------------------------------------------------------------------


/*
Co-ref Annotation Controller
*/

class CAController {

    constructor(caModel, caView) {
        this._caModel = caModel;
        this._caView = caView;

        this._attachListenersToView(caView);
    }

    _attachListenersToView(caView) {
        caView.markClicked.attach(this._onMarkClick.bind(this));
    }

    _onMarkClick(sender, args) {
        console.log(`received click from (${args.sIdx}, ${args.eIdx})`);

        const mark = args.mark;
        console.log(mark);
        // currently no focused
        if (_.isNil(this._caView.currentFocus)) {
            if (args.isNoRef) return;
            this._caView.focusOnMark(args.sIdx, args.eIdx);
        }
        else {
            const currentFocus = this._caView.currentFocus;
            // if focused and click from a disabled mark
            if (mark.state == MarkStates.DISABLED) return;
            // clicked on the selected mark
            if (args.sIdx == currentFocus.sIdx && args.eIdx == currentFocus.eIdx) {
                this._caView.unFocus();
                return;
            }

            if (args.isNoRef)
                this._caModel.getAnnotation(currentFocus.sIdx, currentFocus.eIdx)
                    .setReference(true)
            else
                this._caModel.getAnnotation(currentFocus.sIdx, currentFocus.eIdx)
                    .setReference(false, args.sIdx, args.eIdx)
            this._caView.unFocus();
            return;
        }
    }

}

/*
End of Co-ref Annotation Controller
 */

// ----------------------------------------------------------------------

/*
Utils
 */

class Reference {
    constructor() {
        this.isNoRef = null;
        if (arguments.length > 0) this.setReference(arguments);
    }

    setReference(isNoRef, sIdx, eIdx) {
        this.isNoRef = isNoRef;
        this.sIdx = (isNoRef) ? undefined : sIdx;
        this.eIdx = (isNoRef) ? undefined : eIdx;
    }

    isSet() {
        return !_.isNil(this.isNoRef);
    }
}


// CADS - Co-ref Annotation Data Structure
function getCADS(docJson) {
    var docAnnots = {};
    _.each(docJson['sentences'], (sentence, sIdx) => {
        if (sentence.ents.length > 0) {
            docAnnots[sIdx] = {};
            _.each(sentence.ents, (ent, eIdx) => {
                docAnnots[parseInt(sIdx)][parseInt(eIdx)] = new Reference();
            });
        }
    });
    return docAnnots;
}


// ----------------------------------------------------------------------



function getDocument(url='../sample_doc.json') {
    return $.ajax({
        url: url,
        dataType: 'json'
    }).then(
        (response) => {
            // sort ents in each sentece by start
            _.each(response['sentences'], function(sentence) {
                sentence.ents.sort(function(e1, e2) {
                    return e1.start - e2.start});
            });
            // validate data and not load if incorrect
            return response;
        },
        () => null
    );
}


var caModel, caView, caController;
var debug = {};
$(document).ready( function() {
    let docPromise = getDocument();

    $.when( docPromise ).then(
        ( docJson ) => {
            caModel = new CAModel(docJson);
            caView = new CAView(caModel);
            caController = new CAController(caModel, caView);
            // $('#submit-button').on('click', () => submit('http://localhost:8000', taModel, taView, taController));
        },
        () => { 
            //error handling if figer data is not loaded
        }
    );
});