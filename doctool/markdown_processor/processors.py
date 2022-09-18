from project.processors import FileProcessor


import markdown
from . import md2l

from django.utils.text import slugify


class _MD(md2l.Markdown):

    def preprocess(self, text):
        return text

    def postprocess(self, text):
        return text


class MarkdownFileProcessor(FileProcessor):
    exts = ['md']
    default_encoding = 'utf-8'

    def process_file_test(self, file):
        return file.ext in self.exts

    def get_encoding(self, file):
        return self.default_encoding

    def process_file(self, file):
        """Inspect the contents of the file.
        This does not produce the final render.
        """
        print('markdown process file', file)
        md = self.render_markdown_unit(file.raw_content(self.get_encoding(file)))
        self.md = md
        fields = self.rebrand_filename(file)
        fields += self.rebrand_menu_label(file)
        # disect segments
        # inject assocations.
        # bag of words
        self.bag_of_words(file)
        return fields

    def bag_of_words(self, file):
        # Extract all unique words and stash against the file.
        pass

    def render_live_model_test(self, model):
        return model.ext == 'md'

    def render_live_model(self, model, encoding=None):
        md = self.render_markdown_unit_extended(model.raw_content(encoding))
        model.markdown_unit = md
        return md._converted

    def rebrand_menu_label(self, file):
        """Return the "menu_label" field from the toc[0] item
        """
        toc = self.md.toc_tokens
        new_title = None
        if (toc is not None) and len(toc) > 0 and (toc[0]['level'] == 1):
            new_title = toc[0]['name']
            file.menu_label = new_title
            return ('menu_label',)
        return ()

    def rebrand_filename(self, file):
        # Extract TOC
        toc = self.md.toc_tokens
        # Change title
        new_title = file.filename
        # Grab the title from the TOC

        if (toc is not None) and len(toc) > 0 and (toc[0]['level'] == 1):
            new_title = toc[0]['id']

        # Override from meta.
        new_title = file.get_kv('filename', new_title)
        # Tag on 'rendering' format.
        file.filename = slugify(new_title)

        # Send back fields for bulk update.
        return ('filename',)

    def render_markdown_unit_extended(self, text):
        extensions = [
            'md_mermaid',
            'extra',
            'toc',
            'meta',
            # 'pymdownx.extra',
            # 'admonition',
            'codehilite',
            # 'sane_lists',
            # 'smarty',
            # 'wikilinks',
            # 'pymdownx.tasklist',
            # 'pymdownx.magiclink',
            # 'pymdownx.emoji',
            # 'pymdownx.smartsymbols',
        ]

        return self.render_markdown_unit(text, extensions)

    def render_markdown_unit(self, text, extensions=None):
        extensions = extensions or [
            # 'extra',
            'toc',
            'meta',
            # 'pymdownx.extra',
            # 'admonition',
            # 'codehilite',
            # 'sane_lists',
            # 'smarty',
            # 'wikilinks',
            # 'pymdownx.tasklist',
            # 'pymdownx.magiclink',
            # 'pymdownx.emoji',
            # 'pymdownx.smartsymbols',
        ]

        m = markdown.Markdown(extensions=extensions)
        m._converted = m.convert(text)
        m._input_text = text
        return m


    def render_markdown_unit_md2(self, text):
        # md2l
        extensions = [
            # 'extra',
            'metadata',
            'fenced-code-blocks',
            'toc',
            'header-ids',
            # 'pymdownx.extra',
            # 'admonition',
            # 'codehilite',
            # 'sane_lists',
            # 'smarty',
            # 'wikilinks',
            # 'pymdownx.tasklist',
            # 'pymdownx.magiclink',
            # 'pymdownx.emoji',
            # 'pymdownx.smartsymbols',
        ]

        m = _MD(extras=extensions)
        m._converted = m.convert(text)
        m._input_text = text
        return m

