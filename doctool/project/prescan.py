from pathlib import Path
from django.apps import apps
from uuid import uuid4
from project.models import Project
import json
from .create import create_project


def pre_scan(project, **options):
    """Initial fileset from the first presentation
    """
    ps = PreScanner(project, **options)
    ps.cache_files()
    ps.cache_generate_models()
    ps.cache_save_models()
    return ps


def run_pre_scanners(pre_scanners):
    """Given a list of pre-scanners, deduce the configuration points from the
    files and edit the scanner.

    The scanner may be
        a config file pointer
        a directory with a config
        a directory of docs
        a directory of docs with a config for more.
    """
    # Find all configs.
    for scanner in pre_scanners:
        scanner.cache_find_configs()


class Config(object):

    def cache_find_configs(self):
        """find all the config files from the files
        """
        print('cache_find_configs', self)
        PreCacheFile = apps.get_model('project.PreCacheFile')
        files = PreCacheFile.objects.filter(
            bulk_key=self.bulk_key,
            )
        fn = self.get_config_filenames()
        exts = self.get_config_extensions()
        confs = files.filter(
                stem__in=fn,
                ext__in=exts)

        print('Discovered confs', confs.count())

        for conf in confs.all():
            self.unpack_conf(conf)

    def unpack_conf(self, conf):
        # Read the config.
        content = json.loads(conf.read_text())
        for key in content:
            name = f'unpack_config_{key}'
            data = content[key]
            if hasattr(self, name):
                getattr(self, name)(data, conf)
            else:
                self.unpack_conf_unknown(key, data, conf)
        self.project.save()

    def unpack_conf_unknown(self, key, data, conf):
        PreCacheKeyValue = apps.get_model('project.PreCacheKeyValue')
        print('unpack_conf_unknown', key)
        PreCacheKeyValue.objects.create(
            key=key,
            value=data,
            project=self.project
            )

    def unpack_config_name(self, data, conf):
        self.project.unique_name = data

    def unpack_config_melt(self, data, conf):
        for _path in data:
            p = create_project(_path, self.project)
            files = self.cache_files(Path(_path))
            _models = self.cache_generate_models(files, p)
            self.cache_save_models(_models)

    def get_config_filenames(self):
        return ['config']

    def get_config_extensions(self):
        return ['json', 'yaml', 'toml']


class Shaping(object):

    def cache_generate_models(self, files=None, project=None):
        r = ()
        PreCacheFile = apps.get_model('project.PreCacheFile')
        models = self.model_shape(files or self.files, project)
        for d in models:
            m = PreCacheFile(**d)
            r += (m, )

        self.models = r
        return r

    def model_shape(self, files, project=None):
        """convert each file to an object shape ready for model insertion.
        """
        res = ()
        str_uuid = self.bulk_key
        pr = self.project if project is None else project

        project_path = Path(pr.absolute_dir)

        for file in files:
            d = self.shape_file(file)
            d['project'] = pr
            fullpath = Path(d['fullpath'])
            d['rel_fullpath'] = fullpath.relative_to(project_path).as_posix()
            d['rel_path'] = Path(d['rel_fullpath']).parent.as_posix()
            d['bulk_key'] = str_uuid
            res += (d,)
        return res

    def shape_file(self, file):
        d = {
            'fullpath': str(file.as_posix()),
            'filename': file.name,
            'is_file': file.is_file(),
            'path': str(file.parent),
            'anchor': file.anchor,
            'stem': file.stem,
            'suffix': file.suffix,
            'ext': file.suffix[1:],
        }
        return d

    def cache_save_models(self, models=None):
        PreCacheFile = apps.get_model('project.PreCacheFile')
        inserts = PreCacheFile.objects.bulk_create(
            models or self.models,
            # using='precache'
            )
        print(f'Insert count: {len(inserts)}')


class PreScanner(Config, Shaping):

    def __init__(self, project, **options):
        self.project = project
        self.options = options
        self.files = ()
        self.bulk_key = str(uuid4())

    def cache_files(self, path=None, pattern=None):
        _files = self.get_everything_list(path, pattern)
        self.files += _files
        return _files

    def get_bulked(self):
        PreCacheFile = apps.get_model('project.PreCacheFile')
        return PreCacheFile.objects.filter(bulk_key=self.bulk_key)

    def get_everything_list(self, path=None, pattern=None):
        """Return all target files and folders within the root directory.
        This should return "everything" the generator should see, including
        asset directories.
        """
        path = path or self.get_root_path()
        print('  Getting files at:', path)
        all_files = path.glob(pattern or self.get_file_discovery_pattern())
        return tuple(all_files)

    def get_root_path(self):
        """Return the base dir of the config files.

        return config "docs_dir" or the original path of the config file.
        """
        return Path(self.project.absolute_dir)

    def get_file_discovery_pattern(self):
        return '**/*'
