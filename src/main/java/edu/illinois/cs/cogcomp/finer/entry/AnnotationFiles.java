package edu.illinois.cs.cogcomp.finer.entry;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;
import edu.illinois.cs.cogcomp.annotation.AnnotatorException;
import edu.illinois.cs.cogcomp.annotation.BasicAnnotatorService;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation
        .TextAnnotation;

import edu.illinois.cs.cogcomp.core.utilities.SerializationHelper;
import edu.illinois.cs.cogcomp.finer.FinerAnnotator;
import edu.illinois.cs.cogcomp.preprocessing.dumper.Dumper;
import edu.illinois.cs.cogcomp.utils.PipelineUtils;
import net.sf.extjwnl.JWNLException;
import org.mapdb.DB;
import org.mapdb.DBMaker;
import org.mapdb.HTreeMap;
import org.mapdb.Serializer;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;

import static edu.illinois.cs.cogcomp.utils.PipelineUtils.getPipeline;

/**
 * Created by haowu4 on 1/17/17.
 */
public class AnnotationFiles {
    public static class AnnotationFilesParameters {
        @Parameter(names = "-input")
        public String input;
        @Parameter(names = "-output")
        public String output;
        @Parameter(names = "-limit")
        public int limit = 50000;
    }

    private AnnotationFilesParameters parameters;
    DB db;
    HTreeMap<String, byte[]> store;
    BasicAnnotatorService processor;
    FinerAnnotator finerAnnotator;

    public AnnotationFiles(AnnotationFilesParameters parameters) {
        this.parameters = parameters;
    }

    public void init() throws IOException, AnnotatorException, JWNLException {
        processor = getPipeline();
        finerAnnotator = new FinerAnnotator(PipelineUtils
                .readFinerTypes("resources/type_to_wordnet_senses.txt"));

        db = DBMaker
                .fileDB(String.format("%s_%d", parameters.output, 0))
                .closeOnJvmShutdown()
                .make();

        store = db.hashMap("annotated")
                .keySerializer(Serializer.STRING)
                .valueSerializer(Serializer.BYTE_ARRAY)
                .createOrOpen();
    }

    int counter = 0;

    public void annotateAndSave(String id, String text) throws
            Exception {
        TextAnnotation ta = processor.createAnnotatedTextAnnotation("", id,
                text);
        finerAnnotator.addView(ta);
        if (ta.getView("FINER").getConstituents().isEmpty()) {
            return;
        }

        String json = SerializationHelper.serializeToJson(ta);
        store.put(id, gzip(json));

    }

    private static String ungzip(byte[] bytes) throws Exception {

        InputStreamReader isr = new InputStreamReader(new GZIPInputStream(new
                ByteArrayInputStream(bytes)), StandardCharsets.UTF_8);

        StringWriter sw = new StringWriter();

        char[] chars = new char[1024];

        for (int len; (len = isr.read(chars)) > 0; ) {
            sw.write(chars, 0, len);
        }
        return sw.toString();

    }


    private static byte[] gzip(String s) throws Exception {

        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        GZIPOutputStream gzip = new GZIPOutputStream(bos);
        OutputStreamWriter osw = new OutputStreamWriter(gzip,
                StandardCharsets.UTF_8);

        osw.write(s);
        osw.close();
        return bos.toByteArray();

    }

    public void startProcess() {
        try (BufferedReader br = new BufferedReader(new FileReader(parameters
                .input))) {
            String line;
            int lineCounter = 0;
            while ((line = br.readLine()) != null) {
                lineCounter++;
                annotateAndSave(lineCounter + "", line);

                System.out.println(String.format("L" +
                        "ine processed with " +
                        "annotation %d/%d \r", counter, lineCounter));
                if (lineCounter > parameters.limit) {
                    db.commit();
                    store.close();
                    db.close();
                    System.out.println(String.format("L" +
                            "ine processed with " +
                            "annotation %d/%d \n", counter, lineCounter));
                    System.out.println("Finished ");
                    System.exit(0);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }

    }


    public static void main(String[] args) throws JWNLException,
            AnnotatorException, IOException {
        AnnotationFilesParameters parameters = new AnnotationFilesParameters();

        new JCommander(parameters).parse(args);
        System.out.println(parameters);
        AnnotationFiles gd = new AnnotationFiles(parameters);
        gd.init();
        gd.startProcess();
    }
}
