from pathlib import Path
from django.utils.text import slugify
from collections import defaultdict

from django.apps import apps

class ProcessorRegister(object):
    def __init__(self):
        self.units = ()

    def append(self, cls):
        self.units += (cls,)

    def process_file(self, file):
        all_fields = set()
        for unit in self.units:
            # e.g. project.processors.MarkdownFileProcessor
            if unit.process_file_test(file):
                fields = unit.process_file(file)
                if fields is not None:
                    all_fields.update(fields)
        return all_fields

    def render_live_model(self, model, encoding=None):
        # res = ()
        for unit in self.units:
            if unit.render_live_model_test(model):
                # e.g. project.processors.MarkdownFileProcessor
                content = unit.render_live_model(model, encoding)
                return content
                # res += (content,)
        # return res
        return f"No renderer for model {model}"


procs = ProcessorRegister()


def render_live_model(model, encoding=None):
    return procs.render_live_model(model, encoding)


class Processor(object):
    """A Processor acts as the core reader for analyzed files.

    In its current form this class is a Mixin for `products.analyze.Analyze`
    and called upon during a `run_all` call.
    """
    def __init__(self, scanner):
        self.scanner = scanner
        self.md_count = 0

    def process_contents(self):
        """The output content is in place - render all the file contents into
        subsections of contents, ready for writing.
        """
        files = self.get_output_files()
        all_fields = set()
        for file in files:
            fields = self.process_file(file)
            if fields is not None:
                all_fields.update(fields)
        FileOutput = apps.get_model('project.FileOutput')
        if len(all_fields) == 0:
            print(' .! Cannot update FileOutput models without fields.')
            return
        FileOutput.objects.bulk_update(files, all_fields)

    def process_file(self, file):
        """
        The primary entry point to read the contents of a file.
        such as concatenating data parts and generating word bags.
        """
        if file.auto_build is False:
            # skip for now
            return

        return procs.process_file(file)

    def get_output_files(self):
        FileOutput = apps.get_model('project.FileOutput')
        return FileOutput.objects.filter(
                bulk_key=self.scanner.bulk_key
            )

class FileProcessor(object):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        procs.append(cls())


