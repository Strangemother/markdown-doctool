from pathlib import Path
from project.models import Project


def create_project(d, parent_project=None):
    absolute_dir = Path(d).absolute()
    if absolute_dir.is_file():
        absolute_dir = absolute_dir.parent

    if absolute_dir.exists() is False:
        print(' .. No directory', absolute_dir)

    p, c = Project.objects.get_or_create(
        given_path=d,
        absolute_dir=absolute_dir,
        parent=parent_project
        )
    p._created_now = c
    print(f'Project {p}, {c}')
    return p
