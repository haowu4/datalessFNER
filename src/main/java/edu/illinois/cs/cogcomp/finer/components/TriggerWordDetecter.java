package edu.illinois.cs.cogcomp.finer.components;

import edu.illinois.cs.cogcomp.core.datastructures.textannotation.Constituent;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.Sentence;
import edu.illinois.cs.cogcomp.finer.datastructure.FineNerType;

import java.util.List;

/**
 * Created by haowu4 on 1/15/17.
 */
public interface TriggerWordDetecter {
    List<Constituent> getTriggerWords(Sentence sentence, List<FineNerType>
            types);
}
