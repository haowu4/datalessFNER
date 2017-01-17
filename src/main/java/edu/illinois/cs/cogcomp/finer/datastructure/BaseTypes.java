package edu.illinois.cs.cogcomp.finer.datastructure;

/**
 * Created by hao on 1/17/17.
 */
public class BaseTypes {
    public static final String PERSON = "PERSON";
    public static final String LOCATION = "LOCATION";
    public static final String ORGANIZATION = "ORGANIZATION";
    public static final String OTHER = "OTHER";

    public static boolean typeMatches(String finerType, String baseTypes) {
        String base = finerType;
        if (finerType.contains(".")) {
            base = finerType.split("\\.")[0];
        }

        boolean isPerson = base.equals("person");
        if (isPerson) {
            return baseTypes.equals(PERSON);
        }
        boolean isLoc = base.equals("location");
        if (isLoc) {
            return baseTypes.equals(LOCATION);

        }
        boolean isOrg = base.equals("organization");
        if (isOrg) {
            return baseTypes.equals(ORGANIZATION);
        }

        if (baseTypes.equals(OTHER)) {
            return true;
        }

        return false;
    }
}
