package edu.illinois.cs.cogcomp.finer;

import edu.illinois.cs.cogcomp.core.datastructures.textannotation.*;
import edu.illinois.cs.cogcomp.finer.components.MentionDetecter;
import edu.illinois.cs.cogcomp.finer.components.TriggerWordDetecter;
import edu.illinois.cs.cogcomp.finer.components.TriggerWordFilter;
import edu.illinois.cs.cogcomp.finer.components.filters.QuotationFilter;
import edu.illinois.cs.cogcomp.finer.components.filters.TypeFilter;
import edu.illinois.cs.cogcomp.finer.components.mention.BasicMentionDetection;
import edu.illinois.cs.cogcomp.finer.components.trigger.BasicTriggerWordDetecter;
import edu.illinois.cs.cogcomp.finer.datastructure.FineNerType;
import net.sf.extjwnl.data.Synset;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Created by haowu4 on 1/15/17.
 */
public class FinerAnnotator {
    private MentionDetecter mentionDetecter = new BasicMentionDetection();
    private TriggerWordDetecter triggerWordDetecter = new BasicTriggerWordDetecter();
    private List<TriggerWordFilter> triggerWordFilters = Arrays.asList(
            new QuotationFilter(),
            new TypeFilter());
    private Map<String, List<Synset>> extractTypes;

    public FinerAnnotator(List<FineNerType> extractTypes) {
        this.extractTypes = new HashMap<>();
        for (FineNerType typeName : extractTypes) {
            this.extractTypes.put(typeName.getTypeName(), typeName
                    .getSenseDefs());
        }
    }

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
                        .filter(trigger -> triggerWordFilters.stream().allMatch(f -> f.filterTriggerWord(s, trigger, mention)))
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

    private Map<String, List<Synset>> getExtractTypes() {
        return extractTypes;
    }

}
