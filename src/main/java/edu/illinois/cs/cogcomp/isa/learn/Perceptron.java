package edu.illinois.cs.cogcomp.isa.learn;

import edu.illinois.cs.cogcomp.isa.math.DenseVector;
import edu.illinois.cs.cogcomp.isa.math.SparseVector;

import java.util.List;

/**
 * Created by hao on 1/19/17.
 */
public class Perceptron implements Model {

    private DenseVector weight;
    private float learnRate;

    @Override
    public void fit(List<Example> exampleList) {
        for (Example e : exampleList) {
            int v = predict(e.x);
            if (e.y != v) {
                for (SparseVector.Entry entry : e.x.entries) {
                    weight.vs[entry.i] += (learnRate * entry.v * (e.y - v));
                }
            }
        }
    }

    @Override
    public int predict(SparseVector v) {
        return weight.dot(v) > 0 ? 1 : 0;
    }
}
