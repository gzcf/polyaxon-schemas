# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import abc
import six

from marshmallow import ValidationError

from polyaxon_schemas.exceptions import PolyaxonConfigurationError, PolyaxonfileError
from polyaxon_schemas.operators import ForConfig, IfConfig
from polyaxon_schemas.polyaxonfile import reader, validator
from polyaxon_schemas.polyaxonfile.parser import Parser
from polyaxon_schemas.polyaxonfile.utils import cached_property
from polyaxon_schemas.utils import to_list


@six.add_metaclass(abc.ABCMeta)
class BaseSpecification(object):
    """Base abstract specification for plyaxonfiles and configurations."""

    _EXPERIMENT = 'experiment'
    _GROUP = 'group'
    _JOB = 'job'
    _PLUGIN = 'plugin'
    _KINDS = {_EXPERIMENT, _GROUP, _JOB, _PLUGIN}

    _SPEC_KIND = None

    MAX_VERSION = 1.0  # Min Polyaxonfile specification version this CLI supports
    MIN_VERSION = 1.0  # Max Polyaxonfile specification version this CLI supports

    VERSION = 'version'
    PROJECT = 'project'
    KIND = 'kind'
    SETTINGS = 'settings'
    DECLARATIONS = 'declarations'
    ENVIRONMENT = 'environment'
    RUN_EXEC = 'run'
    MODEL = 'model'
    TRAIN = 'train'
    EVAL = 'eval'

    SECTIONS = (
        VERSION, PROJECT, KIND, ENVIRONMENT, DECLARATIONS, SETTINGS, RUN_EXEC, MODEL, TRAIN, EVAL
    )

    HEADER_SECTIONS = (
        VERSION, PROJECT, KIND, SETTINGS
    )

    GRAPH_SECTIONS = (
        MODEL, TRAIN, EVAL
    )

    REQUIRED_SECTIONS = (
        VERSION, PROJECT, KIND
    )

    OPERATORS = {
        ForConfig.IDENTIFIER: ForConfig,
        IfConfig.IDENTIFIER: IfConfig,
    }

    def __init__(self, values):
        self._values = to_list(values)

        self._data = reader.read(self._values)
        self.check_data()
        headers = Parser.get_headers(spec=self, data=self._data)
        try:
            self._headers = validator.validate_headers(spec=self, data=headers)
        except ValidationError as e:
            raise PolyaxonConfigurationError(e)
        self._parsed_data = None
        self._validated_data = None
        self._set_parsed_data()
        self._extra_validation()

    def _extra_validation(self):
        pass

    def _set_parsed_data(self):
        parsed_data = Parser.parse(self, self._data, None)
        self._validated_data = validator.validate(spec=self, data=parsed_data)
        self._parsed_data = parsed_data

    @classmethod
    def check_version(cls, data):
        if cls.VERSION not in data:
            raise PolyaxonfileError("The Polyaxonfile `version` must be specified.")
        if not cls.MIN_VERSION <= data[cls.VERSION] <= cls.MAX_VERSION:
            raise PolyaxonfileError(
                "The Polyaxonfile's version specified is not supported by your current CLI."
                "Your CLI support Polyaxonfile versions between: {} {}."
                "You can run `polyaxon upgrade` and "
                "check documentation for the specification.".format(
                    cls.MIN_VERSION, cls.MAX_VERSION))

    @classmethod
    def check_kind(cls, data):
        if cls.KIND not in data:
            raise PolyaxonfileError("The Polyaxonfile `kind` must be specified.")

        if data[cls.KIND] not in cls._KINDS:
            raise PolyaxonfileError(
                "The Polyaxonfile with kind `{}` is not a supported value.".format(data[cls.KIND]))

    def check_data(self, data=None):
        data = data or self._data
        self.check_version(data)
        self.check_kind(data)
        if data[self.KIND] != self._SPEC_KIND:
            raise PolyaxonfileError(
                "The specification used `{}` is incompatible with the kind `{}`.".format(
                    self.__class__.__name__, data[self.KIND]))
        for key in set(six.iterkeys(data)) - set(self.SECTIONS):
            raise PolyaxonfileError("Unexpected section `{}` in Polyaxonfile version `{}`. "
                                    "Please check the Polyaxonfile specification "
                                    "for this version.".format(key, 'v1'))

        for key in self.REQUIRED_SECTIONS:
            if key not in data:
                raise PolyaxonfileError("{} is a required section for a valid Polyaxonfile".format(
                    key))

    @classmethod
    def get_kind(cls, data):
        cls.check_kind(data=data)
        return data[cls.KIND]

    @classmethod
    def read(cls, values):
        if isinstance(values, cls):
            return values
        return cls(values)

    @cached_property
    def is_experiment(self):
        return self.kind == self._EXPERIMENT

    @cached_property
    def is_group(self):
        return self.kind == self._GROUP

    @cached_property
    def is_job(self):
        return self.kind == self._JOB

    @cached_property
    def is_plugin(self):
        return self.kind == self._PLUGIN

    @property
    def values(self):
        return self._values

    @cached_property
    def data(self):
        return self._data

    @cached_property
    def headers(self):
        return self._headers

    @cached_property
    def parsed_data(self):
        return self._parsed_data

    @cached_property
    def version(self):
        return self.headers[self.VERSION]

    @cached_property
    def project(self):
        return self.headers[self.PROJECT]

    @cached_property
    def kind(self):
        return self.headers[self.KIND]

    @cached_property
    def settings(self):
        return self.headers.get(self.SETTINGS, None)

    @cached_property
    def log_level(self):
        if self.settings and self.settings.logging:
            return self.settings.logging.level
        return 'INFO'
