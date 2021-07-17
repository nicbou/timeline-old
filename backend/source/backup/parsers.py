from rest_framework import parsers
from formencode.variabledecode import variable_decode

class MultipartFormencodeParser(parsers.MultiPartParser):
    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(
            stream,
            media_type=media_type,
            parser_context=parser_context
        )
        data = variable_decode(result.data)
        return parsers.DataAndFiles(data, result.files)