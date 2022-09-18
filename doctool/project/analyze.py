from pathlib import Path
from django.utils.text import slugify
from collections import defaultdict

from . import models, processors
import markdown2

# lowercase
README_NAMES = (
    'readme',
)

def analyze_pre_scanner(pre_scanner):
    """Analyze the prescanned files and return a
    analysed file set.

    tasks:

    + Create File units
    + plug missing files
        + Index files for Directories
        + content pages (lists)
    + index images
    + Collect assets
    + process text
    + write cross references
    """
    analyze = Analyze(pre_scanner)
    analyze.run_all()
    return analyze


class FileGen(object):
    def generate_fileset(self):
        """Read the scanner models and convert to
        Files and Dirs
        """
        # find all files in scanner uuid
        # perform early excludes
        prefiles = self.scanner.get_bulked()
        self.generate_files(prefiles)
        self.generate_directories(prefiles)
        self.bind_directories()

    def generate_files(self, prefiles):
        print('generate_fileset, Reading', prefiles.count())
        File = models.File

        fs = ()
        keys = (
            'project',
            'bulk_key',
            # 'is_file',
            'rel_fullpath',
            'rel_path',
            'filename',
            'stem',
            'ext',
        )
        # produce files
        us = ()
        for prefile in prefiles.filter(is_file=True):
            copies = {k: getattr(prefile, k) for k in keys}
            prefile.is_used = True
            us += (prefile,)
            f = File(**copies)
            fs += (f,)

        File.objects.bulk_create(fs, batch_size=900)
        models.PreCacheFile.objects.bulk_update(us, fields=['is_used'])

    def generate_directories(self, prefiles):
        dkeys= (
            'project',
            'bulk_key',
            'rel_fullpath',
            # 'parent',
            # 'dirs',
            # 'files',
            )
        drs = ()
        # produce dirs.
        for prefile in prefiles.filter(is_file=False):
            copies = {k: getattr(prefile, k) for k in dkeys}
            dr = models.Directory(**copies)
            drs += (dr,)
            # add files.
            prefile.is_used = True

        models.Directory.objects.bulk_create(drs, batch_size=900)

    def bind_directories(self):
        File = models.File
        drs = models.Directory.objects.filter(bulk_key=self.scanner.bulk_key)
        # Apply dir m2ms
        for dr in drs:
            relp = dr.rel_fullpath

            dr.files.add(*File.objects.filter(rel_path=relp))
            # Apply to parent
            parents = models.Directory.objects.filter(
                rel_fullpath=str(Path(dr.rel_fullpath).parent.as_posix()),
                bulk_key=dr.bulk_key
                )

            if parents.count() == 1:
                dr.parent = parents.get()

            for parent in parents:
                parent.dirs.add(dr)
                parent.save()
            dr.save()


class Analyze(FileGen, processors.Processor):
    def __init__(self, scanner):
        self.scanner = scanner
        self.md_count = 0
        self.md2 = None
        self.encoding = 'utf-8'

    def run_all(self):


        # find all files in scanner uuid
        # perform early excludes
        self.generate_fileset()
        # Read meta data, and apply any changes.
        self.build_keyvalue_models()
        # write file and dir references
        # write nested dir connections
        self.build_output_models()

        # Add missing dir index file references
        # add contents indicies pages
        self.plug_output_gaps()

        ## with all the target files referenced
        # we read file contents and do data recombobulation.
        self.process_contents()
        ## This produces structures assigned back to the file reference,
        # including text clones, file assets and other stuff.

        ## At this point and final cross references is done
        # producing many file-parts, attached to files.
        # Each file is associated to a directory, its prescan, and any meta.

        # This is all passed to the future 'render' stage...

    def get_files(self):
        return models.File.objects.filter(
                bulk_key=self.scanner.bulk_key
            )

    def build_keyvalue_models(self):
        """Create file key values through the read_file meta collection.
        """
        files = self.get_files()

        print('Process', files.count(), 'files')
        fkvs = ()
        FileKeyValue = models.FileKeyValue

        for file in files:
            dd = self.read_file(file)
            for k, v in dd.items():
                fkv = FileKeyValue(
                        file=file,
                        key=k,
                        value=v,
                    )
                fkvs += (fkv, )
        FileKeyValue.objects.bulk_create(fkvs)
        # dirs = models.Directory.objects.filter(
        #         bulk_key=self.scanner.bulk_key
        #     )

    def read_file(self, file):
        name = f'read_file_{file.ext}'
        meta = {}
        if hasattr(self, name):
            meta = getattr(self, name)(file)
        # Check for baked meta locations
        return meta

    def read_file_md(self, file):
        self.md_count += 1
        mm = self.get_reader(True)
        try:
            text = mm.convert(file.read_text(self.encoding))
        except UnicodeDecodeError as err:
            print(' -- File Failed', file)
            print(err)
            return {}
        d = mm.metadata
        d.update(md_count=self.md_count)
        return d

    def get_reader(self, clean=False):
        if self.md2 is None:
            self.md2 = markdown2.Markdown(extras=['metadata', 'toc'])
        if clean is True:
            self.md2.reset()
        return self.md2

    def build_output_models(self):
        """Iterate the files to process the output values
        such as output filename, title, directory etc.
        """
        fos = ()
        files = self.get_files()
        for file in files:
            fo = self.create_fileoutput(file)
            fo.bulk_key = self.scanner.bulk_key
            fos += (fo, )

        models.FileOutput.objects.bulk_create(fos)
        # Filter for file output rel_paths (disctict)
        # generate output dirs for all.
        #
        dirs = defaultdict(tuple)
        for fo in fos:
            dirs[fo.rel_path] += (fo,)
        # Now we have all the directories and their children.
        OutputDirectory = models.OutputDirectory
        ods = ()
        for dir_path, fileoutputs in dirs.items():
            od = OutputDirectory(
                    project=self.scanner.project,
                    rel_path=dir_path,
                    bulk_key=self.scanner.bulk_key,
                    stem=Path(dir_path).stem,
                )
            ods += (od,)
        OutputDirectory.objects.bulk_create(ods)

        # Now reloop and append files.
        for dir_path, fileoutputs in dirs.items():
            od = OutputDirectory.objects.get(
                    rel_path=dir_path,
                    bulk_key=self.scanner.bulk_key
                )
            od.files.add(*fileoutputs)
            parent = od.get_parent()
            if parent is not None:
                parent.dirs.add(od)
            # od.save()

    def create_fileoutput(self, file):
        """Create the position record for ther associated file.
        At this point we can "move" the file, rename it, and change it ext.
        """

        ext_map = {
            'md': 'html'
        }

        ext = ext_map.get(file.ext, None)
        auto_build = ext is not None
        stem = file.stem
        opts = {
            'file': file,
            'project': file.project,
            'rel_path': file.rel_path,
            'filename': slugify(stem),
            'ext': file.ext,
            'auto_build': auto_build,
        }

        # rename 'readme' of a dir, to 'index'
        ## Add missing index files.
        if stem.lower() in README_NAMES:
            # Test the position of the _real_ file.
            _dir = file.directory_set.first()
            index_exists = _dir.files.filter(stem__iexact='index').exists()

            if index_exists is False:
                # rebrand
                opts['filename'] = 'index'

        return models.FileOutput(**opts)

    def plug_output_gaps(self):
        """Look at all output directorys, and ensure each has:

        + an index
        + a content list.
        """
        bulk_key = self.scanner.bulk_key
        dirs = (models.OutputDirectory.objects
                        .filter(bulk_key=bulk_key))

        fos = ()
        for _dir in dirs:
            has_index = _dir.files.filter(filename__iexact='index').exists()
            if not has_index:
                fo = self.create_index_file(_dir)
                fos += (fo, )
            has_content = _dir.files.filter(filename__iexact='content').exists()
            if not has_content:
                fo = self.create_content_file(_dir)
                fos += (fo, )

        models.FileOutput.objects.bulk_create(fos)

    def create_index_file(self, _dir):
        print('Create index file.', _dir)
        bulk_key = self.scanner.bulk_key
        fo = models.FileOutput(
            rel_path=_dir.rel_path,
            project=self.scanner.project,
            filename='index',
            # ext='md',
            auto_build=True,
            sim_file=True,
            bulk_key=bulk_key,
            )
        return fo

    def create_content_file(self, _dir):
        print('Create content file.', _dir)
        bulk_key = self.scanner.bulk_key
        fo = models.FileOutput(
            rel_path=_dir.rel_path,
            project=self.scanner.project,
            filename='content',
            # ext='md',
            auto_build=True,
            sim_file=True,
            bulk_key=bulk_key,
            )
        return fo

