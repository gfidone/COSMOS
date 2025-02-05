import warnings

class DefaultDict(dict):
    def __missing__(self, k):
        return '{' + k + '}'

class Prompt:
    
    def __init__(self, template, user_attributes, profile_tags=('<personal information>', '</personal information>')):
        self.template = template
        self.attributes = user_attributes
        self.profile_tags = profile_tags
        self.format_template()
        
    def format_template(self):
        attribute_module = '\n'
        for attribute in self.attributes:
            attribute_module += f'{attribute.capitalize()}: {{{attribute}}}\n'
        start = self.template.find(self.profile_tags[0]) + len(self.profile_tags[0])
        end = self.template.find(self.profile_tags[1])
        self.template = self.template[:start] + attribute_module + self.template[start:]
        
    def __call__(self, **kwargs):
        valued = DefaultDict(kwargs)
        missed = [k for k in self.attributes if k not in valued]
        prompt = self.template.format_map(valued)
        if missed:
            warnings.warn(f'Prompt template is missing the following arguments: {missed}', UserWarning)
        return prompt

