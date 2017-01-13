package edu.illinois.cs.cogcomp.preprocessing.worker;

import edu.illinois.cs.cogcomp.annotation.AnnotatorException;
import edu.illinois.cs.cogcomp.annotation.AnnotatorServiceConfigurator;
import edu.illinois.cs.cogcomp.annotation.BasicAnnotatorService;
import edu.illinois.cs.cogcomp.core.utilities.configuration.Configurator;
import edu.illinois.cs.cogcomp.core.utilities.configuration.ResourceManager;
import edu.illinois.cs.cogcomp.pipeline.common.PipelineConfigurator;
import edu.illinois.cs.cogcomp.pipeline.main.PipelineFactory;

import java.io.IOException;
import java.util.Properties;

/**
 * Created by haowu4 on 1/10/17.
 */
public class Worker {
    private BasicAnnotatorService processor;

    public Worker() throws IOException, AnnotatorException {
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
}
