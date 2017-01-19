package edu.illinois.cs.cogcomp.util;

import org.apache.commons.lang3.StringUtils;

import java.io.*;
import java.util.List;

/**
 * Created by haowu on 4/1/16.
 */
public class Eval {


    /**
     * confMatrix[i][j] is the number of time that we label i to gold label j.
     * @param confMatrix
     */
    public static void evaluate(int[][] confMatrix) {
        int numOfClass = confMatrix.length;
        double[] colSums = new double[numOfClass];
        double[] rowSums = new double[numOfClass];
        for (int i = 0; i <numOfClass; i++) {
            for (int j = 0; j < numOfClass; j++) {
                rowSums[i] += confMatrix[i][j];
                colSums[j] += confMatrix[i][j];
            }
        }

        double[] precisions = new double[numOfClass];
        double[] recalls = new double[numOfClass];
        double[] f1s = new double[numOfClass];
    }

    public static void printConfusionMatrix(int[][] confMat, String[] labels ,int padSize){
        System.out.println("Confusion Matrix : " );

        System.out.print(StringUtils.rightPad(" ", padSize));
        System.out.print("\t");
        for (int i = 0; i < labels.length; i++) {
            System.out.print(StringUtils.rightPad(labels[i], padSize));
            System.out.print("\t");
        }
        System.out.print("\n");
        for (int i = 0; i < labels.length; i++) {
            System.out.print(StringUtils.rightPad(labels[i], padSize));
            System.out.print("\t");
            for (int j = 0; j < labels.length; j++) {
                System.out.print(StringUtils.rightPad(confMat[i][j] + "", padSize));
                System.out.print("\t");
            }
            System.out.print("\n");
        }
    }

    public static void writeDataToFileForEvaluation(int[] gold,int[] pred, String filename)
        throws FileNotFoundException, UnsupportedEncodingException {
        PrintWriter writer = new PrintWriter(filename, "UTF-8");
        for(int x : gold){
            writer.print(x + "");
            writer.print(" ");
        }
        writer.print("\n");
        for(int x : pred){
            writer.print(x+"");
            writer.print(" ");
        }
        writer.close();

    }

    public static void writeDataToFileForEvaluation(List<Integer> gold,List<Integer> pred, String filename)
        throws FileNotFoundException, UnsupportedEncodingException {
        PrintWriter writer = new PrintWriter(filename, "UTF-8");
        for(int x : gold){
            writer.print(x + "");
            writer.print(" ");
        }
        writer.print("\n");
        for(int x : pred){
            writer.print(x + "");
            writer.print(" ");
        }
        writer.close();
    }

    public static void evalFile(String fileName){

        try {
            Runtime r = Runtime.getRuntime();

            Process p = r.exec(new String[]{"python", "scripts/evaluate.py", fileName});
            BufferedReader in =
                new BufferedReader(new InputStreamReader(p.getInputStream()));
            String inputLine;
            while ((inputLine = in.readLine()) != null) {
                System.out.println(inputLine);
            }
            in.close();

            // Print erro message, if any
            in =
                new BufferedReader(new InputStreamReader(p.getErrorStream()));
            while ((inputLine = in.readLine()) != null) {
                System.err.println(inputLine);
            }
            in.close();

        } catch (IOException e) {
            System.out.println(e);
        }
    }
}
