from django.shortcuts import render
from trim import views as trims

from . import models
from django.template.response import TemplateResponse
from django.template.base import Template


class MarkdownTemplateRenderer(TemplateResponse):
    """The standard Markdown template renderer allows the _early_ injection
    of processed markdown, to allow the standard django rendering on the given
    HTML.

    Within the primary template, apply the custom template tag.
    """
    tag = "[[MARKDOWN::RENDER]]"

    def get_tagger(self):
        word = 'MARKDOWN'
        s = "[%s]{2}%s::([A-Za-z0-9]+)[%s]{2}" % ('[', word, ']')
        print('  Looking at', s)
        return re.compile(s, re.IGNORECASE)

    @property
    def rendered_content(self):
        """Return the freshly rendered content for the template and context
        described by the TemplateResponse.

        This *does not* set the final content of the response. To set the
        response content, you must either call render(), or set the
        content explicitly using the value of this property.
        """

        # django.template.backends.django.Template
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)
        source = self.update_template(template, context)
        old_inner = template.template
        inner = Template(source, old_inner.origin, old_inner.name, old_inner.engine)
        template.template = inner
        return template.render(context, self._request)

    def update_template(self,template, context):
        """Given the standard django template, alter the 'source' of the template
        (the outbound HTML) and early replace all markdown components before
        the django rendering.

        Ensuring this occurs before the main rendering allows the use of
        django templates within markdown.
        """
        # django.template.backends.django.Template
        old_inner = template.template
        # django.template.base.Template
        source = old_inner.source#.replace(self.tag, content or "")
        tagger = self.get_tagger()

        fmap = {
            'render': self._render_content,
            'toc': self._render_toc,
        }

        for match in tagger.finditer(source):
            word =  match[1].lower()
            print('  match', word, match)
            func = fmap.get(word, context)
            if func is None:
                print('  No rendering tool for', word)
                continue
            source = func(match, source, context)
        return source

    def _render_toc(self, match, source, context):
        """Collect the TOC from the existing markdown_unit within the model,
        and replace the match group.
        """
        span = match.group()
        replacement = context['object'].markdown_unit.toc
        return source.replace(span, replacement)

    def _render_content(self, match, source, context):
        """Replace the match group() location with the correct markdown content.
        This may also generate the markdown_unit within the model.
        """
        content = context['object'].rendered_content('utf-8')
        span = match.group()
        return source.replace(span, content)
        # return source.replace(self.tag, content or "")

import re

class GenericFileView(trims.DetailView):
    """Present a Generic file using the standard model detailview with an
    extended response_class for replacing the incoming markdown.
    """
    model = models.FileOutput
    response_class = MarkdownTemplateRenderer


class GenericDirView(trims.DetailView):
    model = models.OutputDirectory

# trims.crud(models.Project, __name__)

class ProjectListView(trims.ListView):
    model = models.Project


class ProjectDetailView(trims.DetailView):
    model = models.Project

