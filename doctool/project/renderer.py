"""The entrance tool to help with generating Projects.

    from project.renderer import cli_render_all
    cli_render_all(*args, **kwargs)

"""
import os
from pathlib import Path
from django.apps import apps
from uuid import uuid4
from project.models import Project
import json

from . import prescan
from . import analyze
from . import models
from . import create


def cli_render_all(*args, **options):
    paths = options['paths']
    ps = ()
    for d in paths:
        p = create.create_project(d)
        ps += (p, )
    return render_all(ps, **options)


def render_all(projects, *args, **options):
    """Given one or more projects and the arguments and kwargs given through
    the cli, perform all steps to render the docs.
    """
    pres = ()
    for pr in projects:
        ps = prescan.pre_scan(pr, **options)
        pres += (ps, )

    print('Render', projects)
    # configure reads the prescanned files and
    # unpacks the configs - merging any waiting pre-merges.
    prescan.run_pre_scanners(pres)
    # analyze the precaches, to the content analysis.
    analyzers = analyze_pre_scanners(pres)
    # index - Read the neat File types to produce the rendered output
    # render
    render_out(analyzers)
    # write out


def analyze_pre_scanners(pre_scanners):
    """For each prescan, analyze the content and perform the changes
    to render File units.

    + Plug missing files
    + Renames and rebrands
    + moves and plugs etc..

    Essentially this point remaps and creates tidy file and
    directory units for the next step, indexing.
    """
    azs = ()
    for scanner in pre_scanners:
        print('analyze_pre_scanner', scanner)
        az = analyze.analyze_pre_scanner(scanner)
        azs += (az, )

    return azs


def render_out(analyzers):
    print('Rendering out', analyzers)
    rs = ()
    for analyzer in analyzers:
        r = Renderer(analyzer)
        r.render_out()
        rs += (r, )
    return rs


class Renderer(object):

    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.output_dir = None
        self.allow_overwrite = False

    def render_out(self):
        print('render all')
        bulk_key = self.analyzer.scanner.bulk_key
        od = self.create_output_dir()
        if od is None:
            print('No output dir')
            return

        self.output_dir = od
        files = models.FileOutput.objects.filter(
            auto_build=True,
            bulk_key=bulk_key,
            )

        maps ={
            'missed': (),
            'created': (),
        }
        for file in files:
            dest_path = self.render_file(file)
            key = ['created', 'missed'][int(dest_path is None)]
            maps[key] += (dest_path,)

        print('Created', len(maps['created']))
        print('Missed', len(maps['missed']))

    def create_output_dir(self):
        dest = self.analyzer.scanner.project.get_output_dir()
        if dest is None:
            print(' No output directory for', self)
            return None
        if not dest.exists():
            os.makedirs(dest)
        assert dest.exists()
        return dest

    def render_file(self, file):
        """Given a outputfile object, render the content into the destination.
        """
        out_path = file.get_destination_fullpath(self.output_dir)

        if out_path.exists() and (self.allow_overwrite == False):
            print('.. file exists', out_path)
            return out_path

        ext = file.ext
        if ext is None:
            return self.render_file_unknown(ext)

        name = f'render_file_{ext}'
        if hasattr(self, name):
            return getattr(self, name)(file)

        return self.render_file_generic(file)

    def render_file_unknown(self, file):
        """A file with the extenstion of None.
        This is likely a sim file.
        """
        return None # self.render_file_generic(file)

    def x_render_file_md(self, file):
        """Create a HTML file from a markdown file.
        """
        out_path = file.get_destination_fullpath(self.output_dir)
        out_path.with_suffix('html')

    def render_file_generic(self, file):
        """A Filename extenstion without a file capture function, such as .woff
        Handle the entry as required and return the utput path if any.
        """
        return

        # out_path = file.get_destination_fullpath(self.output_dir)

        # if out_path.exists():
        #     print('.. file exists', out_path)
        #     return out_path

        # try:
        #     out_path.write_text('')
        # except FileNotFoundError:
        #     # Nested file, parent is missing.
        #     os.makedirs(out_path.parent)
        #     out_path.write_text('')
        # return out_path
