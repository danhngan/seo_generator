from bs4 import BeautifulSoup

from big_seo.llm_arch.indexer import (IParser
                                      )
from big_seo.common.lang import DocumentLang

from big_seo.llm_arch.core.common import (Document, IDocumentCreator)
from big_seo.llm_arch.implement.indexer import OutlineDocument
from big_seo.translator.core import Translator


class OutlineDocumentCreator(IDocumentCreator):
    def create(self, **kwargs) -> Document:
        header: str = kwargs['header'] if 'header' in kwargs else 'No heading'
        content: str = kwargs['content'] if 'content' in kwargs else 'No content'
        doc_lang: DocumentLang = kwargs['doc_lang'] if 'doc_lang' in kwargs else DocumentLang.VI
        return OutlineDocument(header, content, doc_lang)


class WebPageParser(IParser):
    """for in doc parser doc_creator create method must take 2 parameters: header and content"""

    def __init__(self, start_tag='h1',
                 exclude_tags=set(
                     ['script', 'style', 'noscript', 'footer', 'header']),
                 get_all_text_tags=set(
                     ['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']),
                 doc_creator: IDocumentCreator = None):
        self.start_tag = start_tag
        self.exclude_tags = exclude_tags
        self.get_all_text_tags = get_all_text_tags
        self._nested_structure = None
        self.doc_creator = doc_creator
        self.webpage: Document = None

    def feed(self, doc: Document) -> None:
        self.webpage = doc
        self._nested_structure = None

    def parse(self, nested: bool = False, in_doc: bool = False, concat_to=None) -> list[tuple[str, Document]]:
        if not self._nested_structure:
            self._nested_structure = self._get_nested_structure()
        if nested:
            return self._nested_structure

        if in_doc:
            flat_outline = self.get_flat_outline(concat_to=concat_to)
            return [(h, self.doc_creator.create(header=h, content=t)) for h, t in flat_outline]

        outer_doc = {'tag': 'body',
                     'tag_text': '-'.join(node['tag_text'] for node in self._nested_structure),
                     'children': self._nested_structure}
        res = []
        self._get_flat_structure(outer_doc, res)
        return [(o, self.webpage) for o in res]

    def get_flat_outline(self, concat_to=None):
        if not self._nested_structure:
            self._nested_structure = self._get_nested_structure()
        res = []
        self._get_flat_outline(self._nested_structure,
                               res, concat_to=concat_to)
        return res

    def _get_nested_structure(self) -> dict:
        page_content = self.webpage.get_doc_content()
        if not page_content:
            page_content = '<head><title>Không có nội dung</title></head><body><h1>Không có nội dung</h1></body>'

        soup = BeautifulSoup(page_content, 'html.parser')
        main_soup = self._get_main_content(soup)

        generations = [{'tag': 'h1', 'tag_text': '',
                        'text': soup.find('h1').text if soup.find('h1') else (soup.title.text if soup.title else 'Không có nội dung'),
                        'children': []}]

        self._parse_recursive_structure(main_soup, generations)
        res = []
        for node in generations:
            if node['tag'] == self.start_tag:
                self._concat_text(node)
                res.append(node)
        return res

    def _get_text(self, soup: BeautifulSoup) -> str:
        if not soup:
            return ''
        if soup.name in self.get_all_text_tags:
            return soup.text
        return soup.text
        # return soup.find(string=True, recursive=False)

    def _get_next(self, soup: BeautifulSoup) -> BeautifulSoup:
        if soup.name in self.get_all_text_tags:
            while soup and not soup.find_next_sibling():
                soup = soup.find_parent()
            return soup.find_next_sibling() if soup else None
        return soup.find_next()

    def _concat_text(self, node: dict) -> str:
        children_text = []
        children = node['children']
        new_children = []
        node['tag_text'] = node['text'] if isinstance(
            node['text'], str) else ''
        for child in children:
            if len(child['children']) == 0 and isinstance(child['text'], str):
                children_text.append(child['text'])
            elif len(child['children']) > 0:
                new_children.append(child)
                self._concat_text(child)
        node['text'] = '\n'.join(children_text)
        node['children'] = new_children

    def _concat_all_children_text(self, node: dict) -> str:
        text = node['tag_text'] + '\n'+node['text']
        for child in node['children']:
            text += '\n' + self._concat_all_children_text(child)
        return text

    # def _parse_recursive_structure(self, soup: BeautifulSoup, generations: list):
    #     if not soup or soup.name == 'footer':
    #         return None

    #     if soup.name in self.exclude_tags:
    #         return self._parse_recursive_structure(self._get_next(soup), generations)
    #     current = {'tag': soup.name,
    #                'text': self._get_text(soup), 'children': []}
    #     if soup.name.startswith('h'):
    #         while len(generations) > 0 and generations[-1]['tag'] >= soup.name and generations[-1]['tag'] > 'h1':
    #             generations.pop()
    #         if len(generations) > 0 and current['tag'] > 'h1':
    #             generations[-1]['children'].append(current)
    #         generations.append(current)
    #         self._parse_recursive_structure(self._get_next(soup), generations)
    #     else:
    #         generations[-1]['children'].append(current)
    #         self._parse_recursive_structure(self._get_next(soup), generations)

    def _parse_recursive_structure(self, soup: BeautifulSoup, generations: list):
        for node in soup.childGenerator():

            if not node.name or node.name in self.exclude_tags:
                continue
            current = {'tag': node.name,
                       'text': self._get_text(node),
                       'children': []}
            if node.name.startswith('h'):
                while len(generations) > 0 and generations[-1]['tag'] >= node.name and generations[-1]['tag'] > 'h1':
                    generations.pop()
                if len(generations) > 0 and current['tag'] > 'h1':
                    generations[-1]['children'].append(current)
                generations.append(current)

            else:
                generations[-1]['children'].append(current)

    def _get_flat_outline(self, children: list, res: list, concat_to: str = None):
        for child in children:
            if concat_to and child['tag'] == concat_to:
                child['text'] = self._concat_all_children_text(child)
            res.append((child['tag']+' - '+child['tag_text'], child['text']))
            if len(child['children']) > 0 and (concat_to is None or child['tag'] < concat_to):
                self._get_flat_outline(child['children'], res, concat_to)

    def _get_flat_structure(self, parent, res: list):
        for child in parent['children']:
            res.append(child['tag']+' - '+parent['tag_text'] +
                       ' - '+child['tag_text'])
            if len(child['children']) > 0:
                self._get_flat_structure(child, res)

    def _get_main_content(self, soup: BeautifulSoup, thres: int = 0.4) -> BeautifulSoup:
        body = soup.find('body')
        if not body:
            return BeautifulSoup('<head><title>Không có nội dung</title></head><body><h1>Không có nội dung</h1></body>', 'html.parser')
        total_text_count = len(
            body.text) - (len(body.find('footer').text) if body.find('footer') else 0)
        node_text_count = {}

        def count_text(soup: BeautifulSoup):
            if soup in node_text_count:
                return node_text_count[soup]
            if soup.name in self.get_all_text_tags or not hasattr(soup, 'children'):
                node_text_count[soup] = len(soup.text)
            elif soup.name in self.exclude_tags:
                node_text_count[soup] = 0
            else:
                node_text_count[soup] = sum(
                    count_text(child) for child in soup.children)
            return node_text_count[soup]

        def walk_tree(soup: BeautifulSoup):
            """return main content soup"""
            if soup.name in self.exclude_tags:
                return False
            if count_text(soup) / total_text_count > thres:
                if not hasattr(soup, 'children'):
                    return soup.parent
                for child in soup.children:
                    res = walk_tree(child)
                    if res:
                        return res
                return soup
            return False
        return walk_tree(body)


class UpToDateWebPageParser(WebPageParser):

    def parse(self, nested: bool = False, in_doc: bool = False, concat_to=None) -> list[tuple[str, Document]]:

        if not self._nested_structure:
            self._nested_structure = self._get_nested_structure()
        if nested:
            return self._nested_structure

        if in_doc:
            flat_outline = self.get_flat_outline(concat_to=concat_to)
            return [(h, self.doc_creator.create(header=h, content=t)) for h, t in flat_outline]

        outer_doc = {'tag': 'body',
                     'tag_text': '-'.join(node['tag_text'] for node in self._nested_structure),
                     'children': self._nested_structure}
        res = []
        self._get_flat_structure(outer_doc, res)
        return [(o, self.webpage) for o in res]

    def _get_nested_structure(self) -> dict:
        page_content = self.webpage.get_doc_content()
        if not page_content:
            page_content = '<head><title>Không có nội dung</title></head><body><h1>Không có nội dung</h1></body>'

        soup = BeautifulSoup(page_content, 'html.parser')
        main_soup = self._get_main_content(soup)

        generations = [{'tag': 'h1', 'tag_text': '',
                        'text': 'For text before h1',
                        'children': []}]

        self._parse_recursive_structure(main_soup, generations)
        res = []
        for node in generations:
            if node['tag'] == self.start_tag:
                self._concat_text(node)
                res.append(node)
        if len(res[0]['children']) == 0:
            return res[1:]
        return res

    def _get_heading_text(self, soup: BeautifulSoup) -> str:
        span = soup.find('span')
        if span:
            return span.text
        return ''
        # return soup.find(string=True, recursive=False)

    def _parse_recursive_structure(self, soup: BeautifulSoup, generations: list):
        for node in soup.childGenerator():
            node_name = self._get_heading_name(node)
            if not node_name or node_name in self.exclude_tags:
                continue
            if node_name.startswith('h'):
                current = {'tag': node_name,
                           'text': self._get_heading_text(node),
                           'children': []}
                self._process_generations(current, generations)

            current = {'tag': soup.name,
                       'text': self._get_text(node),
                       'children': []}
            self._process_generations(current, generations)

    def _get_main_content(self, soup: BeautifulSoup, thres: int = 0.4) -> BeautifulSoup:
        main_soup = soup.find(attrs={'id': 'topicText'})
        if main_soup:
            return main_soup

        return super()._get_main_content(soup, thres)

    def _get_heading_name(self, soup: BeautifulSoup):
        if not soup.name:
            return soup.name
        if soup.name.startswith('h'):
            return soup.name
        soup_classes = soup.get_attribute_list('class')
        if not soup_classes:
            return soup.name
        for soup_class in soup_classes:
            if isinstance(soup_class, str) and soup_class == 'headingAnchor':
                span = soup.find('span')
                if span and span.get_attribute_list('class'):
                    for span_class in span.get_attribute_list('class'):
                        if isinstance(span_class, str) and len(span_class) == 2 and span_class.startswith('h'):
                            return span_class
        return soup.name

    def _process_generations(self, current, generations):
        node_name = current['tag']
        if node_name.startswith('h'):
            while len(generations) > 0 and generations[-1]['tag'] >= node_name and generations[-1]['tag'] > 'h1':
                generations.pop()
            if len(generations) > 0 and current['tag'] > 'h1':
                generations[-1]['children'].append(current)
            generations.append(current)
        else:
            generations[-1]['children'].append(current)


class TranslationParser(IParser):
    """Currently support only parser generating list[tuple[str, Document]]"""

    def __init__(self, org_parser: IParser, translator: Translator, input_lang: DocumentLang, target_lang: DocumentLang):
        self.org_parser = org_parser
        self.translator = translator
        self.input_lang = input_lang
        self.target_lang = target_lang

    def feed(self, doc: Document):
        return self.org_parser.feed(doc)

    def parse(self, **kwargs) -> list[tuple[str, Document]]:
        res = self.org_parser.parse(**kwargs)
        self._walk(res)
        return res

    def _walk(self, obj):
        for i, (h, c) in enumerate(obj):
            obj[i] = (self._identify_and_process_end_object(h),
                      self._identify_and_process_end_object(c))

    def _identify_and_process_end_object(self, obj):
        if isinstance(obj, str):
            return self._translate(obj)
        if isinstance(obj, Document):
            content = obj.get_doc_content()
            if not hasattr(obj, 'translations'):
                obj.translations = {}
            obj.translations[str(self.target_lang)] = self._translate(content)
            obj.get_doc_content = lambda: obj.translations[str(
                self.target_lang)]
            return obj
        else:
            return obj

    def _translate(self, text: str):
        return self.translator.translate(text, input_lang=self.input_lang, output_lang=self.target_lang)
