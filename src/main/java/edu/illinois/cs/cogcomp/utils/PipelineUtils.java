package edu.illinois.cs.cogcomp.utils;

import edu.illinois.cs.cogcomp.annotation.AnnotatorException;
import edu.illinois.cs.cogcomp.annotation.AnnotatorServiceConfigurator;
import edu.illinois.cs.cogcomp.annotation.BasicAnnotatorService;
import edu.illinois.cs.cogcomp.core.utilities.configuration.Configurator;
import edu.illinois.cs.cogcomp.core.utilities.configuration.ResourceManager;
import edu.illinois.cs.cogcomp.finer.datastructure.FineNerType;
import edu.illinois.cs.cogcomp.pipeline.main.PipelineFactory;
import edu.illinois.cs.cogcomp.wsd.annotators.WordSenseAnnotator;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Properties;

/**
 * Created by haowu4 on 1/15/17.
 */
public class PipelineUtils {
    public static BasicAnnotatorService getPipeline() throws IOException,
            AnnotatorException {
        Properties props = new Properties();
        props.setProperty("usePos", Configurator.TRUE);
        props.setProperty("useLemma",
                Configurator.FALSE);
        props.setProperty("useShallowParse",
                Configurator.TRUE);

        props.setProperty("useNerConll",
                Configurator.TRUE);
        props.setProperty("useNerOntonotes",
                Configurator.TRUE);
        props.setProperty("useStanfordParse",
                Configurator.FALSE);
        props.setProperty("useStanfordDep",
                Configurator.TRUE);

        props.setProperty("useSrlVerb",
                Configurator.FALSE);
        props.setProperty("useSrlNom",
                Configurator.FALSE);
        props.setProperty(
                "throwExceptionOnFailedLengthCheck",
                Configurator.FALSE);
        props.setProperty(
                "useJson",
                Configurator.FALSE);
        props.setProperty(
                "isLazilyInitialized",
                Configurator.TRUE);
//        props.setProperty(
//                PipelineConfigurator.USE_SRL_INTERNAL_PREPROCESSOR.key,
//                Configurator.FALSE);


        props.setProperty(AnnotatorServiceConfigurator.DISABLE_CACHE.key,
                Configurator.FALSE);
        props.setProperty(AnnotatorServiceConfigurator.CACHE_DIR.key,
                "/tmp/cache");
        props.setProperty(
                AnnotatorServiceConfigurator.THROW_EXCEPTION_IF_NOT_CACHED.key,
                Configurator.FALSE);
        props.setProperty(
                AnnotatorServiceConfigurator.FORCE_CACHE_UPDATE.key,
                Configurator.FALSE);

        String embeddingFile =
                "/home/haowu4/data/autoextend/GoogleNews-vectors" +
                        "-negative300.combined_500k.txt";

        if (!new File(embeddingFile).exists()) {
            embeddingFile =
                    "";
        }

        props.setProperty(
                "wsd-word-embedding-file", embeddingFile
        );

        embeddingFile =
                "/home/haowu4/data/autoextend/synset_embeddings_300.txt";

        if (!new File(embeddingFile).exists()) {
            embeddingFile =
                    "";
        }

        props.setProperty(
                "wsd-sense-embedding-file",
                embeddingFile);

        embeddingFile =
                "/home/haowu4/data/autoextend/word_pos_to_synsets.txt";

        if (!new File(embeddingFile).exists()) {
            embeddingFile =
                    "";
        }

        props.setProperty(
                "wsd-sense-mapping-file", embeddingFile
        );

        ResourceManager resourceManager = new ResourceManager(props);
        WordSenseAnnotator wsd = new WordSenseAnnotator("", new String[]{""},
                resourceManager);

        BasicAnnotatorService processor = PipelineFactory
                .buildPipeline(new ResourceManager(props));
        processor.addAnnotator(wsd);

        return processor;
    }

    public static List<FineNerType> readFinerTypes(String file){
        throw new RuntimeException("Not implemented..");
    }

}
