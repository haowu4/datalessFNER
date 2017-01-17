package edu.illinois.cs.cogcomp;

import edu.illinois.cs.cogcomp.annotation.AnnotatorException;
import edu.illinois.cs.cogcomp.annotation.AnnotatorServiceConfigurator;
import edu.illinois.cs.cogcomp.annotation.BasicAnnotatorService;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation
        .TextAnnotation;
import edu.illinois.cs.cogcomp.core.utilities.configuration.Configurator;
import edu.illinois.cs.cogcomp.core.utilities.configuration.ResourceManager;
import edu.illinois.cs.cogcomp.pipeline.main.PipelineFactory;
import edu.illinois.cs.cogcomp.wsd.annotators.WordSenseAnnotator;

import java.io.File;
import java.io.IOException;
import java.util.Properties;

import static edu.illinois.cs.cogcomp.utils.PipelineUtils.getPipeline;

/**
 * Created by haowu4 on 1/15/17.
 */
public class FinerSystemTest {

    public static void main(String[] args) throws IOException,
            AnnotatorException {
        String sentence = "Not content with bringing Rocky back to cinema " +
                "screens , another Stallone character Vietnam vet " +
                "John Rambo is coming out of hibernation , 19 years after " +
                "the third film in the series .";

        BasicAnnotatorService processor = getPipeline();

        TextAnnotation ta = processor.createAnnotatedTextAnnotation("", "",
                sentence);


    }
}
