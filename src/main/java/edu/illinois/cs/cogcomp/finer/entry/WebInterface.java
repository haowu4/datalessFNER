package edu.illinois.cs.cogcomp.finer.entry;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import edu.illinois.cs.cogcomp.annotation.AnnotatorException;
import edu.illinois.cs.cogcomp.annotation.BasicAnnotatorService;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.Constituent;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation
        .TextAnnotation;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation.View;
import edu.illinois.cs.cogcomp.finer.FinerAnnotator;
import edu.illinois.cs.cogcomp.finer.components.TriggerWordDetecter;
import edu.illinois.cs.cogcomp.finer.components.filters.QuotationFilter;
import edu.illinois.cs.cogcomp.finer.components.mention.BasicMentionDetection;
import edu.illinois.cs.cogcomp.utils.PipelineUtils;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import static edu.illinois.cs.cogcomp.utils.PipelineUtils.getPipeline;
import static spark.Spark.*;

/**
 * Created by haowu4 on 1/15/17.
 */
public class WebInterface {
    private static final Gson GSON = new GsonBuilder().create();
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

    private View annotate(String d) throws AnnotatorException {
        TextAnnotation ta = preprocessText(d);
        View finer = finerAnnotator.annotateByHypernymModel(ta);
        return finer;
    }

    private static WebInterface web;

    public static class AnnotationRequest {
        String text;
    }

    public static class Mention {
        int start;
        int end;
        Map<String, Double> label;

        public Mention(int start, int end, Map<String, Double> label) {
            this.start = start;
            this.end = end;
            this.label = label;
        }
    }

    public static class AnnotationResult {
        String[] tokens;
        List<Mention> wsds;
        List<Mention> mentions;
        List<Mention> triggers;

        public AnnotationResult(String[] tokens, List<Mention> wsds,
                                List<Mention> mentions, List<Mention>
                                        triggers) {
            this.tokens = tokens;
            this.wsds = wsds;
            this.mentions = mentions;
            this.triggers = triggers;
        }
    }

    public static AnnotationResult getResult(View view) {
        List<Mention> mentions = new ArrayList<>();
        List<Mention> triggers = new ArrayList<>();
        for (Constituent c : view) {
            if (c.getAttribute("type").equals("mention")) {
                mentions.add(new Mention(c.getStartSpan(), c.getEndSpan(), c
                        .getLabelsToScores()));
            } else {
                triggers.add(new Mention(c.getStartSpan(), c.getEndSpan(), c
                        .getLabelsToScores()));
            }
        }
        List<Mention> wsds = view.getTextAnnotation().getView("SENSE")
                .getConstituents().stream()
                .map(c -> new Mention(c.getStartSpan(), c.getEndSpan(), c
                        .getLabelsToScores())).collect(Collectors.toList());

        return new AnnotationResult(view.getTextAnnotation().getTokens(), wsds,
                mentions, triggers);
    }


    public static void main(String[] args) throws IOException,
            AnnotatorException {
//        BasicAnnotatorService processor = getPipeline();
        BasicMentionDetection mentionDetection = new BasicMentionDetection();
        TriggerWordDetecter triggerWordDetecter = null;
        QuotationFilter filter = new QuotationFilter();


        FinerAnnotator finerAnnotator = new FinerAnnotator(PipelineUtils
                .readFinerTypes(""));
        WebInterface webInterface = new WebInterface(null, finerAnnotator);

        externalStaticFileLocation("web");

        post("/annotate", (request, response) -> {
            String body = request.body();
            AnnotationRequest annotationRequest = GSON.fromJson(body,
                    AnnotationRequest.class);
            View v = webInterface.annotate(annotationRequest.text);
            return GSON.toJson(getResult(v));
        });
    }


}
