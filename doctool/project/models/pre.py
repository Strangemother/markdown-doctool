"""Pre models act as representation for the _first_ step in processing the files.
Upon a scan of a target directory, the tool creates a project and discovers
all files within.

The PreCacheFile and assets are processed into File, Directory, then into
output models.

+ PreCacheFile files represent the _real_ dataset, without alteration

"""
from django.db import models
from trim import models as t_models
from django.db import models
from pathlib import Path
import os


class Project(models.Model):

    unique_name = t_models.chars(max_length=3000, nil=True)
    given_path = t_models.chars(max_length=3000)
    absolute_dir = t_models.chars(max_length=3000)
    parent = t_models.self_fk(nil=True)
    created, updated = t_models.dt_cu_pair()

    # _short_string = '"{self.name}" x{self.count}'
    def get_output_dir(self):

        rel_path = self.get_key('output_dir')
        if rel_path:
            rel_path = rel_path.value
        else:
            print('  No output_dir path for', self)
            return None
        # Resolve to absolute
        p = Path(rel_path)
        if p.is_absolute():
            return p
        p = Path(self.absolute_dir) / p
        # normalise
        p = Path(os.path.normpath(p))
        return p

    def get_keys(self, key):
        return self.precachekeyvalue_set.filter(key=key)

    def get_key(self, key):
        keys = self.get_keys(key)
        if keys.count() == 1:
            return keys.get()
        try:
            return keys.latest('updated')
        except PreCacheKeyValue.DoesNotExist:
            return None

    def __str__(self):
        return f'{self.__class__.__name__}({self.id}) {self.unique_name}'



class PreCacheKeyValue(models.Model):

    project = t_models.fk(Project)
    key = t_models.chars(max_length=3000, nil=True)
    value = t_models.json()
    created, updated = t_models.dt_cu_pair()

    def __str__(self):
        return f'{self.key}, {self.value}'


class PreCacheFile(models.Model):
    project = t_models.fk(Project)
    bulk_key = t_models.str_uuid()
    is_file = t_models.boolean_false()
    is_used = t_models.boolean_false()
    fullpath = t_models.chars(max_length=3000, help_text='the original path')
    rel_fullpath = t_models.chars(max_length=3000,
            help_text='the original path, relative to the project root')
    path = t_models.chars(max_length=3000,help_text='a posix path without the filename')
    rel_path = t_models.chars(max_length=3000,
        help_text='a posix path without the filename, relative to the root')
    anchor = t_models.chars(help_text='the original drive')
    filename  = t_models.chars(max_length=3000,
                            help_text='the filename with the suffix')
    stem  = t_models.chars(max_length=3000,
                            help_text='the filename without the suffix')
    suffix  = t_models.chars(max_length=3000,
                            help_text='The extension including the period')
    ext  = t_models.chars(max_length=3000,
                            help_text='The extension without the period')

    created, updated = t_models.dt_cu_pair()

    def read_text(self):
        return Path(self.fullpath).read_text()

