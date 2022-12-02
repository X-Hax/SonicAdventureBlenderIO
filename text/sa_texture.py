from typing import List
import configparser
import os
import io


class SATextureFile:
    '''SA Tex File (.satex) Class Handler'''

    name: str
    text_name_array_name: str
    number: int
    texture_names: List[str]

    def __init__(self):
        self.name = ""
        self.text_name_array_name = ""
        self.number = 0
        self.texture_names = list()

    def fromIni(self, path):
        '''Loads .satex data into Blender.'''
        config = io.StringIO()
        filepath = os.path.abspath(path)
        print(filepath)

        if os.path.isfile(path):
            config.write('[Head]\n')
            config.write(open(filepath).read())
            config.seek(0, os.SEEK_SET)

            cp = configparser.ConfigParser()
            cp.read_file(config)
            s = "Head"
            self.name = cp.get(s, "Name")
            self.text_name_array_name = cp.get(s, "TexnameArrayName")
            self.number = cp.getint(s, "NumTextures")
            for i in range(self.number):
                name = cp.get(s, "TextureNames[" + str(i) + "]") + ".png"
                print(name)
                self.texture_names.append(name)
