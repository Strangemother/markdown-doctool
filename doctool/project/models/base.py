"""The base product models "File" and "Directory" serve as the _middle step_
when processing all the precached files. These represent the current state of
all files, connected to the (pre) project, built from the PreCacheFile

+ File and Directory models represent _markers_ or pointers to produce an output
  file.
+ They may be created by pre file dicovery, or programmatically

"""
from django.db import models
from trim import models as t_models
from django.db import models
from pathlib import Path
import os


class File(models.Model):
    project = t_models.fk('project.Project')
    rel_path = t_models.chars(max_length=3000,
        help_text='a posix path without the filename, relative to the root')
    rel_fullpath = t_models.chars(max_length=3000,
            help_text='the original path, relative to the project root')
    filename  = t_models.chars(max_length=3000,
                            help_text='the filename with the suffix')
    stem  = t_models.chars(max_length=3000,
                            help_text='the filename without the suffix')
    ext  = t_models.chars(max_length=3000,
                            help_text='The extension without the period')
    bulk_key = t_models.str_uuid()
    created, updated = t_models.dt_cu_pair()

    # encoding = 'utf-8'

    def read_text(self, encoding=None):
        a = Path(self.project.absolute_dir)
        c = a / self.rel_fullpath
        return c.read_text(encoding)# or self.encoding)

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}) {self.rel_fullpath}"

    def get_kv(self, key=None):
        r = self.filekeyvalue_set.all().values('key', 'value')
        if key is not None:
            r = r.filter(key=key)
        return r


class Directory(models.Model):

    project = t_models.fk('project.Project')
    bulk_key = t_models.str_uuid()
    rel_fullpath = t_models.chars(max_length=3000,
            help_text='the original path, relative to the project root')
    parent = t_models.fk_self(related_name='upper')
    dirs = t_models.m2m_self(symmetrical=False)
    files = t_models.m2m(File)

    created, updated = t_models.dt_cu_pair()

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}) {self.rel_fullpath}"


class FileKeyValue(models.Model):

    file = t_models.fk(File)
    key = t_models.chars(max_length=3000, nil=True)
    value = t_models.json()
    created, updated = t_models.dt_cu_pair()

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}) {self.file} {self.key}"
