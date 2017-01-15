package edu.illinois.cs.cogcomp.finer.entry;

import edu.illinois.cs.cogcomp.annotation.AnnotatorException;
import edu.illinois.cs.cogcomp.annotation.BasicAnnotatorService;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation
        .TextAnnotation;

/**
 * Created by haowu4 on 1/15/17.
 */
public class WebInterface {
    private BasicAnnotatorService bas;

    private TextAnnotation preprocessText(String d) throws AnnotatorException {
        return bas.createAnnotatedTextAnnotation("", "", d);
    }

    private String annotate(String d) throws AnnotatorException {
        TextAnnotation ta = preprocessText(d);
        throw new RuntimeException("Not implemented");
    }

}
