import sys
import yaml


def remap(file, ty_maps, change_unmap_to_none=True):
    with open(file) as input:
        for line in input:
            line = line.strip()
            if len(line) == 0:
                print("")
                continue
            w, label = line.split("\t")
            if label == "O":
                label = "O"
            bio = label[0]
            if label[2:] in ty_maps:
                label = ty_maps[label[2:]]
                label = "%s-/%s" % (bio, label)
            else:
                if change_unmap_to_none:
                    label = "O"
            print("%s\t%s" % (w, label))


def main():
    file_name = sys.argv[1]
    ty_maps = sys.argv[2]
    cutn = True
    with open(ty_maps) as input:
        ty_maps = yaml.load(input.read())
    remap(file_name, ty_maps, cutn)


if __name__ == '__main__':
    main()
