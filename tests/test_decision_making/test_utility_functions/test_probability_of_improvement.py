# Copyright 2023 The GPJax Contributors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from jax import config

config.update("jax_enable_x64", True)

import jax.random as jr
import jax.numpy as jnp

from gpjax.decision_making.test_functions.continuous_functions import Forrester
from gpjax.decision_making.utility_functions.probability_of_improvement import (
    ProbabilityOfImprovement,
)
from gpjax.decision_making.utils import OBJECTIVE, gaussian_cdf
from tests.test_decision_making.utils import generate_dummy_conjugate_posterior


def test_probability_of_improvement_gives_correct_value_for_a_seed():
    key = jr.key(42)
    forrester = Forrester()
    dataset = forrester.generate_dataset(num_points=10, key=key)
    posterior = generate_dummy_conjugate_posterior(dataset)
    posteriors = {OBJECTIVE: posterior}
    datasets = {OBJECTIVE: dataset}

    pi_utility_builder = ProbabilityOfImprovement()
    pi_utility = pi_utility_builder.build_utility_function(
        posteriors=posteriors, datasets=datasets, key=key
    )

    test_X = forrester.generate_test_points(num_points=10, key=key)
    utility_values = pi_utility(test_X)

    # Computing the expected utility values
    predictive_dist = posterior.predict(test_X, train_data=dataset)
    predictive_mean = predictive_dist.mean()
    predictive_std = predictive_dist.stddev()

    expected_utility_values = gaussian_cdf(
        (dataset.y.min() - predictive_mean) / predictive_std
    ).reshape(-1, 1)

    assert utility_values.shape == (10, 1)
    assert jnp.isclose(utility_values, expected_utility_values).all()
