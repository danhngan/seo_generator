from big_seo.common.lang import DocumentLang


TEMPLATE = {f'{DocumentLang.EN}_{DocumentLang.VI}_latest': {'template': f"""Bạn là một chuyên gia dịch thuật trong lĩnh vực {{realm}}, bạn có khả dịch chính xác những bài viết bằng {DocumentLang.EN.get_full_lang_name(DocumentLang.VI)} sang {DocumentLang.VI.get_full_lang_name(DocumentLang.VI)}.
Dịch bài sau sang {DocumentLang.VI.get_full_lang_name(DocumentLang.VI)}: {{main_text}}""",
            'parameters': ['realm', 'main_text']},
            f'{DocumentLang.EN}_{DocumentLang.VI}_v1': {'template': f"""Bạn là một chuyên gia dịch thuật trong lĩnh vực {{realm}}, bạn có khả dịch chính xác những bài viết bằng {DocumentLang.EN.get_full_lang_name(DocumentLang.VI)} sang {DocumentLang.VI.get_full_lang_name(DocumentLang.VI)}.
Dịch bài sau sang {DocumentLang.VI.get_full_lang_name(DocumentLang.VI)} {{other_instruction}}: {{main_text}}""",
                                                        'parameters': ['realm', 'main_text', 'other_instruction']}}
