"""Out models represent the _last step_ in the processing of all content.
These models contain the finalised content to write, knowing the tool has processed
the File and Directory models into FileOutput and OutputDirectory types.

The output pages and files are these output models. And when presenting should
be a finished (parsed) version of all File types.

+ Output models represent _to be written_ given File models.
+ They can be altered before write
+ Other FileOutputs and OutputDirectory models use these to process associates
"""
from django.db import models
from trim import models as t_models
from django.db import models
from pathlib import Path
import os

from .. import processors as proj_processors

UNDEFINED = {}


class FileOutput(models.Model):
    """An association of the sim data for rendering; This information may
    be edited by any process and is generated during the analyze phase.
    """
    project = t_models.fk('project.Project', nil=True)
    file = t_models.o2o('project.File', nil=True)
    rel_path = t_models.chars(max_length=3000)
    filename  = t_models.chars(max_length=3000)
    menu_label = t_models.chars(max_length=200)
    ext  = t_models.chars(max_length=3000)

    auto_build = t_models.boolean_false(help_text='Flag true to convert during parsing.')
    sim_file = t_models.boolean_false()

    bulk_key = t_models.str_uuid()
    created, updated = t_models.dt_cu_pair()

    def __str__(self):
        ext = self.ext or '*'
        return (f"{self.__class__.__name__}({self.id})"
                f"{self.rel_path}/{self.filename}.{ext}")

    def label(self):
        """Return a string for the menu label. This may be a friendly name or
        the filename.
        """
        return self.menu_label or self.filename

    def is_labeled(self):
        return self.menu_label is not None

    is_labelled = is_labeled

    def get_destination_fullpath(self, output_dir='.'):
        ss = Path(output_dir) / self.rel_path / self.filename
        return ss.with_suffix(f".{self.ext}")

    @property
    def siblings(self):
        return self.children.exclude(pk=self.pk)

    @property
    def children(self):
        d = self.directory
        if d:
            return self.directory.files.all()
        return self.outputdirectory_set.none()

    @property
    def directory(self):
        r = self.outputdirectory_set.last()
        return r

    def raw_content(self, encoding=None):

        if self.file:
            return self.file.read_text(encoding)
        if self.sim_file:
            return "Sim file (no real file)"

    def rendered_content(self, encoding=None):
        return proj_processors.render_live_model(self, encoding)

    def get_kv(self, key=None, default=UNDEFINED):
        r = self.file.get_kv(key)
        if default is UNDEFINED:
            return r
        if r.count() == 0:
            return default
        return r.get()['value']

    def kv_set(self):
        return self.file.get_kv()



class OutputDirectory(models.Model):
    """A set of directories for the output files - generated after the
    meta data has arranged the FileOutputs.
    """
    project = t_models.fk('project.Project', nil=True)
    stem = t_models.chars(max_length=300,)
    rel_path = t_models.chars(max_length=3000,
            help_text='the original path, relative to the project root')
    # parent = t_models.fk_self(related_name='upper')
    dirs = t_models.m2m_self(symmetrical=False)
    files = t_models.m2m(FileOutput)
    bulk_key = t_models.str_uuid()
    created, updated = t_models.dt_cu_pair()

    def get_parent(self):
        """Given the internal path, step_up into the relpath parent and
        return an object.
        """
        rel_path = str(Path(self.rel_path).parent.as_posix())
        ps = self.__class__.objects.filter(
                bulk_key=self.bulk_key,
                rel_path=rel_path
            )
        try:
            return ps.get()
        except self.__class__.DoesNotExist:
            return None

    @property
    def directory(self):
        return self.outputdirectory_set.last()

    def label(self):
        return self.stem or self.rel_path

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}) {self.rel_path}"

