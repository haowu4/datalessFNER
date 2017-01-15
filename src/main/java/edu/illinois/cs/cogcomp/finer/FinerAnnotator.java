package edu.illinois.cs.cogcomp.finer;

import edu.illinois.cs.cogcomp.core.datastructures.textannotation.*;
import edu.illinois.cs.cogcomp.finer.components.MentionDetecter;
import edu.illinois.cs.cogcomp.finer.components.TriggerWordDetecter;
import edu.illinois.cs.cogcomp.finer.components.TriggerWordFilter;
import edu.illinois.cs.cogcomp.finer.datastructure.FineNerType;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Created by haowu4 on 1/15/17.
 */
public class FinerAnnotator {
    private MentionDetecter mentionDetecter;
    private TriggerWordDetecter triggerWordDetecter;
    private TriggerWordFilter triggerWordFilter;
    List<FineNerType> extractTypes;


    /**
     * @param ta Input TextAnnotation object should have POS, chunker,
     *           NER-conll,
     *           NER-ontonote, and WSD views.
     * @return Fine grain entity annotation.
     */
    public View annotateByHypernymModel(TextAnnotation ta) {

        View finer = new SpanLabelView("FINER-wordnet", ta);

        for (final Sentence s : ta.sentences()) {
            List<Constituent> triggers = triggerWordDetecter.getTriggerWords(s,
                    getExtractTypes());

            for (Constituent c : triggers) {
                c.addAttribute("type", "trigger");
                finer.addConstituent(c);
            }

            List<Constituent> mentions = mentionDetecter.getMentionCandidates
                    (s);

            for (Constituent c : mentions) {
                c.addAttribute("type", "mention");
                finer.addConstituent(c);
            }

            for (final Constituent mention : mentions) {
                List<Constituent> survivedTriggerWords = triggers.stream()
                        .filter(trigger -> triggerWordFilter
                                .filterTriggerWord(s, trigger, mention))
                        .collect(Collectors.toList());
                for (Constituent trigger : survivedTriggerWords) {
                    finer.addRelation(new Relation("triggering", trigger,
                            mention,
                            1.0));
                }
            }
        }
        return finer;
    }

    private List<FineNerType> getExtractTypes() {
        return extractTypes;
    }

}
