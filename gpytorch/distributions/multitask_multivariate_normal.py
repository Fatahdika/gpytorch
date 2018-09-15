from __future__ import absolute_import, division, print_function, unicode_literals

import torch

from ..lazy import LazyTensor
from .multivariate_normal import MultivariateNormal


class MultitaskMultivariateNormal(MultivariateNormal):
    def __init__(self, mean, covariance_matrix, validate_args=False):
        """
        Constructs a multi-output multivariate Normal random variable, based on mean and covariance
        Can be multi-output multivariate, or a batch of multi-output multivariate Normal

        Passing a matrix mean corresponds to a multi-output multivariate Normal
        Passing a matrix mean corresponds to a batch of multivariate Normals

        Params:
            mean (:obj:`torch.tensor`): An `n x t` or batch `b x n x t` matrix of means for the MVN distribution.
            covar (:obj:`torch.tensor` or :obj:`gpytorch.lazy.LazyTensor`): An `nt x nt` or batch `b x nt x nt`
                covariance matrix of MVN distribution.
        """
        if not torch.is_tensor(mean) and not isinstance(mean, LazyTensor):
            raise RuntimeError(
                "The mean of a MultitaskMultivariateNormal must be a Tensor or LazyTensor"
            )

        if not torch.is_tensor(covariance_matrix) and not isinstance(
            covariance_matrix, LazyTensor
        ):
            raise RuntimeError(
                "The covariance of a MultitaskMultivariateNormal must be a Tensor or LazyTensor"
            )

        if mean.ndimension() not in {2, 3}:
            raise RuntimeError("mean should be a matrix or a batch matrix (batch mode)")

        self._mean_shape = mean.shape
        batch_shape = self._mean_shape[:-2]
        super(MultitaskMultivariateNormal, self).__init__(
            mean=mean.view(batch_shape, -1) if batch_shape else mean.view(-1),
            covariance_matrix=covariance_matrix,
            validate_args=validate_args,
        )

    @property
    def n_tasks(self):
        return self._num_tasks

    @property
    def mean(self):
        return super(MultivariateNormal, self).variance.view(*self._mean_shape)

    @property
    def variance(self):
        return super(MultivariateNormal, self).mean.view(*self._mean_shape)

    def rsample(self, sample_shape=torch.Size([])):
        samples = super(MultivariateNormal, self).rsample(sample_shape=sample_shape)
        return samples.view(-1, *self._mean_shape)