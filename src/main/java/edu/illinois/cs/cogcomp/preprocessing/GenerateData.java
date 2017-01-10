package edu.illinois.cs.cogcomp.preprocessing;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;
import edu.illinois.cs.cogcomp.annotation.AnnotatorException;
import edu.illinois.cs.cogcomp.annotation.AnnotatorServiceConfigurator;
import edu.illinois.cs.cogcomp.annotation.BasicAnnotatorService;
import edu.illinois.cs.cogcomp.core.datastructures.textannotation
        .TextAnnotation;
import edu.illinois.cs.cogcomp.core.utilities.SerializationHelper;
import edu.illinois.cs.cogcomp.core.utilities.configuration.Configurator;
import edu.illinois.cs.cogcomp.core.utilities.configuration.ResourceManager;
import edu.illinois.cs.cogcomp.curator.CuratorDataStructureInterface;
import edu.illinois.cs.cogcomp.pipeline.common.PipelineConfigurator;
import edu.illinois.cs.cogcomp.pipeline.main.PipelineFactory;
import edu.illinois.cs.cogcomp.thrift.base.Labeling;
import edu.illinois.cs.cogcomp.thrift.curator.Record;
import org.apache.commons.io.FileUtils;
import org.apache.thrift.TDeserializer;
import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.mapdb.DB;
import org.mapdb.DBMaker;
import org.mapdb.HTreeMap;
import org.mapdb.Serializer;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.util.List;
import java.util.Properties;

import static edu.illinois.cs.cogcomp.utils.StringUtils.pad;


/**
 * Created by haowu4 on 1/10/17.
 */
public class GenerateData {


    public static class GenerateDataParameter {
        @Parameter(names = {"-f", "-folder"}, description = "Folder " +
                "location that contains the list of Records")
        String recordFolders;
        @Parameter(names = {"-l", "-filelist"}, description = "List of " +
                "files.")
        String fileLists;
        @Parameter(names = {"-o", "-output"}, description = "Output location.")
        String output;
    }

    private GenerateDataParameter parameter;
    private BasicAnnotatorService processor;

    public GenerateData(GenerateDataParameter parameter) throws IOException,
            AnnotatorException {
        this.parameter = parameter;
        Properties props = new Properties();

        props.setProperty(PipelineConfigurator.USE_POS.key,
                Configurator.TRUE);
        props.setProperty(PipelineConfigurator.USE_LEMMA.key,
                Configurator.TRUE);
        props.setProperty(PipelineConfigurator.USE_SHALLOW_PARSE.key,
                Configurator.TRUE);

        props.setProperty(PipelineConfigurator.USE_NER_CONLL.key,
                Configurator.TRUE);
        props.setProperty(PipelineConfigurator.USE_NER_ONTONOTES.key,
                Configurator.TRUE);
        props.setProperty(PipelineConfigurator.USE_STANFORD_PARSE.key,
                Configurator.FALSE);
        props.setProperty(PipelineConfigurator.USE_STANFORD_DEP.key,
                Configurator.TRUE);

        props.setProperty(PipelineConfigurator.USE_SRL_VERB.key,
                Configurator.FALSE);
        props.setProperty(PipelineConfigurator.USE_SRL_NOM.key,
                Configurator.FALSE);
        props.setProperty(
                PipelineConfigurator.THROW_EXCEPTION_ON_FAILED_LENGTH_CHECK.key,
                Configurator.FALSE);
        props.setProperty(
                PipelineConfigurator.USE_JSON.key,
                Configurator.FALSE);
        props.setProperty(
                PipelineConfigurator.USE_LAZY_INITIALIZATION.key,
                Configurator.FALSE);
        props.setProperty(
                PipelineConfigurator.USE_SRL_INTERNAL_PREPROCESSOR.key,
                Configurator.FALSE);


        props.setProperty(AnnotatorServiceConfigurator.DISABLE_CACHE.key,
                Configurator.TRUE);
        props.setProperty(AnnotatorServiceConfigurator.CACHE_DIR.key,
                "/tmp/aswdtgffasdfasd");
        props.setProperty(
                AnnotatorServiceConfigurator.THROW_EXCEPTION_IF_NOT_CACHED.key,
                Configurator.FALSE);
        props.setProperty(
                AnnotatorServiceConfigurator.FORCE_CACHE_UPDATE.key,
                Configurator.TRUE);

        processor = PipelineFactory
                .buildPipeline(new ResourceManager(props));
    }

    private DB db;
    private HTreeMap<String, String> map;
    int conuter = 0;

    public void createNewMap() {
        if (conuter > 0) {
            db.commit();
            map.close();
            db.close();
        }


        db = DBMaker
                .fileDB(String.format("%s_%d.db", parameter.output, conuter))
                .closeOnJvmShutdown()
                .make();

        map = db.hashMap("ta")
                .keySerializer(Serializer.STRING)
                .valueSerializer(Serializer.STRING)
                .createOrOpen();
        conuter++;

    }

    public void processFiles() {

        createNewMap();

        List<String> files = null;
        try {
            files = FileUtils.readLines(new File(parameter.fileLists),
                    Charset.defaultCharset());
        } catch (IOException e) {
            e.printStackTrace();
        }

        int fileCounter = 0;
        int length = files.size();
        int fileCounterNonReset = 0;

        System.out.println("Start processing " + length + " files");

        for (String file : files) {
            fileCounterNonReset++;

            System.out.printf("Processed document %s/%s\r",
                            pad(Integer.toString(fileCounterNonReset),
                                    9, ' '),
                            pad(Integer.toString(length), 9, ' '));

            Record r = null;
            try {
                File input = new File(parameter.recordFolders, file);

                r = deserializeRecord(FileUtils.readFileToByteArray(input));
            } catch (TException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }

            Labeling token = r.getLabelViews().get("tokens");
            TextAnnotation ta = CuratorDataStructureInterface
                    .getTextAnnotationFromRecord
                            (parameter.recordFolders, file, r, token, r
                                    .getLabelViews()
                                    .get("sentences"));

            try {
                ta = processor.annotateTextAnnotation(ta, false);
            } catch (AnnotatorException e) {
                e.printStackTrace();
            }


            String json = SerializationHelper.serializeToJson(ta);
            map.put(file, json);
            fileCounter++;
            if (fileCounter == 30000) {
                fileCounter = 0;
                createNewMap();
            }
        }
        db.commit();
        map.close();
        db.close();
    }

    public static Record deserializeRecord(byte[] bytes) throws IOException,
            TException {
        Record obj = new Record();
        TDeserializer td = new TDeserializer(new TBinaryProtocol.Factory());
        td.deserialize(obj, bytes);
        return obj;
    }


    public static void main(String[] args) throws IOException,
            AnnotatorException, TException {

        GenerateDataParameter parameters = new GenerateDataParameter();

        if (args.length == 0) {
            new JCommander(parameters).usage();
            System.exit(1);
        }

        new JCommander(parameters).parse(args);

        GenerateData gd = new GenerateData(parameters);
        gd.processFiles();
    }
}
