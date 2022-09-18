from django.contrib import admin

from trim import admin as trims

from . import models

@trims.register(models.PreCacheFile)
class PreCacheFileAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'project',
        'rel_path',
        'filename',
        'stem',
        'ext',
        'is_file',
        'bulk_key',
        )


@trims.register(models.Directory)
class DirectoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'project',
        'files_count',
        'dirs_count',
        'rel_fullpath',
        'bulk_key',
        )

    def files_count(self, unit):
        return unit.files.count()

    def dirs_count(self, unit):
        return unit.dirs.count()


@trims.register(models.OutputDirectory)
class OutputDirectoryAdmin(DirectoryAdmin):
    list_display = (
        'pk',
        'files_count',
        'dirs_count',
        'rel_path',
        'bulk_key',
        )




@trims.register(models.File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'rel_path',
        'filename',
        'stem',
        'ext',
        'bulk_key',
        )


@trims.register(models.FileOutput)
class FileOutputAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'rel_path',
        'filename',
        'ext',
        'auto_build',
        )


@trims.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'unique_name',
        'given_path',
        'absolute_dir',
        'parent',
        )


trims.register_models(models, ignore=__name__)
