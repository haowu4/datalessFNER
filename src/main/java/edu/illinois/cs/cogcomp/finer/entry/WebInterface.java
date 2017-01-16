package edu.illinois.cs.cogcomp.finer.entry;

import edu.illinois.cs.cogcomp.annotation.AnnotatorException;
import edu.illinois.cs.cogcomp.annotation.BasicAnnotatorService;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation
        .TextAnnotation;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.View;
import edu.illinois.cs.cogcomp.finer.FinerAnnotator;

/**
 * Created by haowu4 on 1/15/17.
 */
public class WebInterface {
    private BasicAnnotatorService bas;
    private FinerAnnotator finerAnnotator;

    public WebInterface(BasicAnnotatorService bas, FinerAnnotator
            finerAnnotator) {
        this.bas = bas;
        this.finerAnnotator = finerAnnotator;
    }

    private TextAnnotation preprocessText(String d) throws AnnotatorException {
        return bas.createAnnotatedTextAnnotation("", "", d);
    }

    private String annotate(String d) throws AnnotatorException {
        TextAnnotation ta = preprocessText(d);
        View finer = finerAnnotator.annotateByHypernymModel(ta);

        throw new RuntimeException("Not implemented");
    }

    public static void main(String[] args) {

    }
}
