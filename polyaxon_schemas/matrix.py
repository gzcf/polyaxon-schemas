# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import numpy as np
import six

from numpy.random.mtrand import normal  # noqa

from marshmallow import Schema, fields, post_dump, post_load, validates_schema

from polyaxon_schemas.base import BaseConfig
from polyaxon_schemas.utils import (
    GeomSpace,
    LinSpace,
    LogNormal,
    LogSpace,
    LogUniform,
    Normal,
    PValue,
    QLogNormal,
    QLogUniform,
    QNormal,
    QUniform,
    Range,
    Uniform,
    lognormal,
    loguniform,
    pvalues,
    qlognormal,
    qloguniform,
    qnormal,
    quniform
)

# pylint:disable=redefined-outer-name


def validate_matrix(values):
    v = sum(map(lambda x: 1 if x else 0, values))
    if v == 0 or v > 1:
        raise ValueError("Matrix element is not valid, one and only one option is required.")


class MatrixSchema(Schema):
    # Discrete
    values = fields.List(fields.Raw(), allow_none=True)
    pvalues = fields.List(PValue(), allow_none=True)
    range = Range(allow_none=True)
    linspace = LinSpace(allow_none=True)
    logspace = LogSpace(allow_none=True)
    geomspace = GeomSpace(allow_none=True)
    # Continuous
    uniform = Uniform(allow_none=True)
    quniform = QUniform(allow_none=True)
    loguniform = LogUniform(allow_none=True)
    qloguniform = QLogUniform(allow_none=True)
    normal = Normal(allow_none=True)
    qnormal = QNormal(allow_none=True)
    lognormal = LogNormal(allow_none=True)
    qlognormal = QLogNormal(allow_none=True)

    class Meta:
        ordered = True

    @post_load
    def make(self, data):
        return MatrixConfig(**data)

    @post_dump
    def unmake(self, data):
        return MatrixConfig.remove_reduced_attrs(data)

    @validates_schema
    def validate_matrix(self, data):
        validate_matrix([
            data.get('values'),
            data.get('pvalues'),
            data.get('range'),
            data.get('linspace'),
            data.get('logspace'),
            data.get('geomspace'),
            data.get('uniform'),
            data.get('quniform'),
            data.get('loguniform'),
            data.get('qloguniform'),
            data.get('normal'),
            data.get('qnormal'),
            data.get('lognormal'),
            data.get('qlognormal'),
        ])


class MatrixConfig(BaseConfig):
    IDENTIFIER = 'matrix'
    SCHEMA = MatrixSchema
    REDUCED_ATTRIBUTES = [
        'values', 'pvalues', 'range', 'linspace', 'logspace', 'geomspace',
        'uniform', 'quniform', 'loguniform', 'qloguniform',
        'normal', 'qnormal', 'lognormal', 'qlognormal'
    ]

    NUMPY_MAPPING = {
        'range': np.arange,
        'linspace': np.linspace,
        'logspace': np.logspace,
        'geomspace': np.geomspace,
        'uniform': np.random.uniform(),
        'quniform': quniform,
        'loguniform': loguniform,
        'qloguniform': qloguniform,
        'normal': normal,
        'qnormal': qnormal,
        'lognormal': lognormal,
        'qlognormal': qlognormal,
    }

    def __init__(self,
                 values=None,
                 pvalues=None,
                 range=None,  # noqa
                 linspace=None,
                 logspace=None,
                 geomspace=None,
                 uniform=None,
                 quniform=None,
                 loguniform=None,
                 qloguniform=None,
                 normal=None,
                 qnormal=None,
                 lognormal=None,
                 qlognormal=None):
        self.values = values
        self.pvalues = pvalues
        self.range = range
        self.linspace = linspace
        self.logspace = logspace
        self.geomspace = geomspace
        self.uniform = uniform
        self.quniform = quniform
        self.loguniform = loguniform
        self.qloguniform = qloguniform
        self.normal = normal
        self.qnormal = qnormal
        self.lognormal = lognormal
        self.qlognormal = qlognormal

        validate_matrix([
            values, pvalues, range, linspace, logspace, geomspace, uniform, quniform,
            loguniform, qloguniform, normal, qnormal, lognormal, qlognormal])

    def to_numpy(self):
        key, value = list(six.iteritems(self.to_dict()))[0]
        if key == 'values':
            return value
        if key == 'pvalues':
            return pvalues(values=value)

        return self.NUMPY_MAPPING[key](**value)

    def sample(self, size=None, rand_generator=None):
        size = None if size == 1 else size
        key, value = list(six.iteritems(self.to_dict()))[0]
        if key in {'values', 'range', 'linspace', 'logspace', 'geomspace'}:
            value = self.to_numpy()
            rand_generator = rand_generator or np.random
            return rand_generator.choice(value, size=size)

        if key == 'pvalues':
            return pvalues(values=value, size=size, rand_generator=rand_generator)

        value['size'] = size
        value['rand_generator'] = rand_generator
        return self.NUMPY_MAPPING[key](**value)
