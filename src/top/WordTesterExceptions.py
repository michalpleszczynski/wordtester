#-*- coding: utf-8 -*-

class FileHandlingExceptions(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class EncodingError(FileHandlingExceptions):
    pass

class VersionError(FileHandlingExceptions):
    pass

class SignatureError(FileHandlingExceptions):
    pass

class UnsupportedFileError(FileHandlingExceptions):
    pass

class ImportSyntaxError(FileHandlingExceptions):
    pass

class ExportSyntaxError(FileHandlingExceptions):
    pass

class TestError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class NoWordsAvailable(TestError):
    pass
