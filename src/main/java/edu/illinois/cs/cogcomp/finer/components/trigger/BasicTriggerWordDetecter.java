package edu.illinois.cs.cogcomp.finer.components.trigger;

import edu.illinois.cs.cogcomp.core.datastructures.textannotation.Constituent;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.Sentence;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.View;
import edu.illinois.cs.cogcomp.finer.components.TriggerWordDetecter;
import edu.illinois.cs.cogcomp.finer.datastructure.FineNerType;
import edu.illinois.cs.cogcomp.utils.WordNetUtils;
import net.sf.extjwnl.JWNLException;
import net.sf.extjwnl.data.Synset;

import java.util.List;
import java.util.Map;

/**
 * Created by haowu4 on 1/16/17.
 */
public class BasicTriggerWordDetecter implements TriggerWordDetecter {
    WordNetUtils wordNetUtils;

    public BasicTriggerWordDetecter() {
        try {
            wordNetUtils = WordNetUtils.getInstance();
        } catch (JWNLException e) {
            e.printStackTrace();
        }
    }

    @Override
    public List<Constituent> getTriggerWords(Sentence sentence, Map<String,
            List<Synset>> types) {
        View wsds = sentence.getView("SENSE");
        for (Constituent c : wsds.getConstituents()) {
            try {
                wordNetUtils.getTypeScores(c.getLabel(), types);
            } catch (JWNLException e) {
                e.printStackTrace();
            }
        }
        return null;
    }
}
