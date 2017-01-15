package edu.illinois.cs.cogcomp.finer.components.filters;

import edu.illinois.cs.cogcomp.core.datastructures.ViewNames;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.Constituent;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.Sentence;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.View;
import edu.illinois.cs.cogcomp.finer.components.TriggerWordFilter;

/**
 * Created by haowu4 on 1/15/17.
 */
public class QuotationFilter implements TriggerWordFilter {

    @Override
    public boolean filterTriggerWord(Sentence sentence, Constituent
            triggerWord, Constituent mention) {
        int triggerStart = triggerWord.getStartSpan();
        int triggerEnd = triggerWord.getEndSpan();

        int mentionStart = mention.getStartSpan();
        int mentionEnd = mention.getEndSpan();

        if (mention.doesConstituentCover(triggerWord)) {
            return true;
        }

        for (int i = triggerEnd; i < mentionStart; i++) {
            String c = triggerWord.getTextAnnotation().getToken(i);
            if (c.equals("\"")) {
                return false;
            }
        }

        for (int i = mentionEnd; i < triggerStart; i++) {
            String c = triggerWord.getTextAnnotation().getToken(i);
            if (c.equals("\"")) {
                return false;
            }
        }

        return true;
    }
}
