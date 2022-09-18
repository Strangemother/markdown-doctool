from project.processors import FileProcessor
import markdown
from . import md2l

from django.utils.text import slugify
import fitz

class PDFFileProcessor(FileProcessor):
    exts = ['pdf']
    default_encoding = 'utf-8'

    def process_file_test(self, file):
        return file.ext in self.exts

    def get_encoding(self, file):
        return self.default_encoding

    def render_live_model_test(self, model):
        return model.ext == 'pdf'

    def process_file(self, file):
        """Inspect the contents of the file.
        This does not produce the final render.
        """
        print('pdf process file', file)
        _pdf = self.render_pdf_unit(file)
        self._pdf = _pdf
        fields = self.rebrand_filename(file)
        fields += self.rebrand_menu_label(file)
        return fields

    def render_live_model(self, model, encoding=None):
        _pdf = self.render_pdf_unit_extended(model)
        model.markdown_unit = _pdf
        return _pdf._converted

    def rebrand_menu_label(self, file):
        """Return the "menu_label" field from the toc[0] item
        """
        return ()

    def rebrand_filename(self, file):

        # Send back fields for bulk update.
        return ('filename',)

    def render_pdf_unit_extended(self, file_path):
        return self.render_pdf_unit(file_path)

    def render_pdf_unit(self, file_path, extensions=None):
        doc = fitz.open(file_path)
        import pdb; pdb.set_trace()  # breakpoint ffdca32b //
        return doc

