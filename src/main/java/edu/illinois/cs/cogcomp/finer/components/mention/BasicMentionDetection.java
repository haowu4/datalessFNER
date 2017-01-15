package edu.illinois.cs.cogcomp.finer.components.mention;

import edu.illinois.cs.cogcomp.core.datastructures.ViewNames;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.Constituent;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.Sentence;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.View;
import edu.illinois.cs.cogcomp.finer.components.MentionDetecter;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by haowu4 on 1/15/17.
 */
public class BasicMentionDetection implements MentionDetecter {
    @Override
    public List<Constituent> getMentionCandidates(Sentence sentence) {
        List<Constituent> ret = new ArrayList<>();
        View ner = sentence.getView(ViewNames.NER_CONLL);
        for (Constituent c : ner.getConstituents()) {
            ret.add(new Constituent("mention", "finer-mention", c
                    .getTextAnnotation
                            (), c.getStartSpan(), c.getEndSpan()));
        }
        return ret;
    }
}
