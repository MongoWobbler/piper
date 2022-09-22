#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import piper.config as pcfg
import piper.core
import piper.core.dcc as dcc
import piper.core.pythoner as python
import piper.unrealpy.metadata as metadata


def openInDCC():
    """
    Opens the selected asset in its source DCC if it has any.

    Returns:
        (list): Metadata with source DCC, relative source path, piper_node, and export method.
    """
    app, source_path, piper_node, export_method = metadata.get()
    app.open(source_path)

    return app, source_path, piper_node, export_method


def reexport(single=False):
    """
    Re-exports the selected assets by looking up its source file and DCC in the metadata.

    Returns:
        (dictionary): Data that was used to reexport files.
    """
    if single:
        app, source_path, piper_node, export_method = metadata.get()
        app.export(source_path, piper_node, export_method)

        return app, source_path, piper_node, export_method

    i = 0
    dcc_names = metadata.getByDCC(absolute_path=True)
    directory = piper.core.getTempDirectory()
    json_file = directory + '/' + pcfg.export_file_name
    python.writeJson(json_file, dcc_names)

    for dcc_name, data in dcc_names.items():
        app = dcc.mapping[dcc_name]()
        app.exportFromJSON(json_file)
        i += len(data)

    # clean up temp files
    os.remove(json_file)
    piper.core.deleteTempDirectory()

    print(f'Finished Exporting {str(i)} files from {len(list(dcc_names.keys()))} DCCs')
    return dcc_names
