from __future__ import print_function


def build(output_file, files):
    with open(output_file, 'w') as out:
        for f_idx, f in enumerate(files):
            print("F{f_idx}: {0.name}".format(f, **locals()), file=out)

            if f.includes is not None:
                for i_idx, i in enumerate(f.includes):
                    print("    I{i_idx}: {0.type}: {0.name}".format(
                        i, **locals()), file=out)
