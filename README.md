# Sempler: Sampling from general structural causal models (SCMs)

### Installation
You can clone this repo or install using pip:
```
pip install sempler
```

Disclaimer: This package is still at its infancy and the API could be subject to change.
Use at your own risk, but also know that feedback is very welcome :)

Two main classes are provided:

-   `sempler.ANM`: to define and sample from general additive noise SCMs. Any
    assignment function is possible, as are the noise distributions.
-   `sempler.LGANM`: to define and sample from a linear model with Gaussian
    additive noise (i.e. a Gaussian Bayesian network).

Both classes define a `sample` function which generates samples from the
SCM, in the observational setting or under interventions.

Additionally, `sempler.LGANM` allows sampling "in the population setting", i.e. by
returning a symbolic gaussian distribution, `sempler.NormalDistribution`, defined by its mean and
covariance, which allows for manipulation such as conditioning,
marginalization and regression in the population setting.

## ANMs - General Additive Noise Models

The ANM class allows to define and sample from general additive noise
models. Any assignment function is possible, as are the noise
distributions.

ANMs are defined by providing the following arguments:

1.  `A` (`np.array`): a connectivity matrix, representing the underlying DAG

2.  `assignments` (`list`): the functional assignments, i.e. a list with a function per variable
    in the SCM, which takes as many arguments as parents (incoming
    edges) of the variable and returns a single (numerical) value. For
    variables which are source nodes in the graph, `None` is used.

3.  `noise_distributions` (`list`): the noise distributions of each variable, i.e. a list with a
    function per variable which can be called with a single (int)
    parameter n and returns n samples. Any distribution is possible
    (even arbitrary deterministic ones); see sempler.noise for common
    ones (uniform, gaussian, laplace, ...).

The parameters of the ANM follow this *functional* approach to give you
maximum flexibility. For more standard, linear SCMs with gaussian noise,
it is easier to use the LGANM class.

### Sampling

Samples are generated by calling the `sample` function, with parameters:

-   `n` (`int`): the number of samples
-   `do\_interventions` (`dict`, optional): a dictionary containing the
    distribution functions (see `sempler.noise`) from which to
    generate samples for each intervened variable
-   `shift\_interventions` (`dict`, optional): a dictionary containing the
    distribution functions (see `sempler.noise`) from which to
    generate the noise which is added to each intervened variable
-   `random\_state` (`int`, optional): seed for the random state generator

An example: creating an ANM with standard Gaussian noise and linear and
non-linear assignments, and sampling from it.

```python
import sempler
import sempler.noise as noise
import numpy as np

# Connectivity matrix
A = np.array([[0, 0, 0, 1, 0],
  [0, 0, 1, 0, 0],
  [0, 0, 0, 1, 0],
  [0, 0, 0, 0, 1],
  [0, 0, 0, 0, 0]])

# Noise distributions (see sempler.noise)
noise_distributions = [noise.normal(0,1)] * 5

# Variable assignments
functions = [None, None, np.sin, lambda x: np.exp(x[:,0]) + 2*x[:,1], lambda x: 2*x]

# All together
anm = sempler.ANM(A, functions, noise_distributions)

# Sampling from the observational setting
samples = anm.sample(100)

# Sampling under a shift intervention on variable 1
samples = anm.sample(100, shift_interventions = {1: noise.normal(0,1)})
```

## LGANMs - Linear Gaussian Additive Noise Models

The `sempler.LGANM` class defines linear models with Gaussian additive noise (i.e.
a Gaussian Bayesian networks).

LGANMs are defined by providing the following arguments:

-   `W` (`np.array`): weighted connectivity matrix representing the DAG
-   `variances` (`np.array` or `tuple`): the variances of the noise terms. Can be either a vector of variances or a tuple indicating a range for their uniform sampling.
-   `means` (`np.array` or `tuple`, optional): the means of the noise terms. Either a vector of means or a tuple indicating the range for uniform sampling. If left unspecified all means are set to zero.

### Sampling

Sampling is again done by calling the `sample` function, with
parameters:

-   `n` (`int`, optinal): the number of samples. Ignored if `population` is True, defaults to 100.
-   `population` (`bool`, optional): If set to True, parameter `n` is ignored and
    `sample` returns a `sempler.NormalDistribution` object, which is a symbolic
    gaussian distribution (see below).
-   `do\_interventions` (`dict`, optional): Dictionary with keys being the
    targets of the interventions and values being either a number (the
    variable is deterministically set to this value) or a tuple with the
    mean and variance of the normal distribution from which to sample
    the variable.
-   `shift\_interventions` (`dict`, optional): Dictionary with keys being the
    targets of the interventions and values being either a number (which
    is then added to the variable) or a tuple with the mean and variance
    of the normal distribution from which to sample added noise.

An example: creating a LGANM with noise means and variances sampled
uniformly from [0,1], and sampling from it.

```python
import sempler
import numpy as np

# Connectivity matrix
W = np.array([[0, 0, 0, 0.1, 0],
              [0, 0, 2.1, 0, 0],
              [0, 0, 0, 3.2, 0],
              [0, 0, 0, 0, 5.0],
              [0, 0, 0, 0, 0]])

# All together
lganm = sempler.LGANM(W, (0,1), (0,1))

# Sampling from the observational setting
samples = lganm.sample(100)

# Sampling under a shift intervention on variable 1 with standard gaussian noise
samples = lganm.sample(100, shift_interventions = {1: (0,1)})

# Sampling the observational environment in the "population setting"
distribution = lganm.sample(population = True)
```


### Symbolic Normal Distribution

The `sempler.NormalDistribution` class allows for symbolic representation of a
multivariate normal distribution, and is returned when calling `LGANM.sample` with `population=True`.

An example:

```python
import numpy as np
import sempler

# Define by mean and covariance
mean = np.array([1,2,3])
covariance = np.array([[1, 2, 4], [2, 6, 5], [4, 5, 1]])
distribution = sempler.NormalDistribution(mean, covariance)

# Marginal distribution of X0 and X1 (also a NormalDistribution object)
marginal = distribution.marginal([0, 1])

# Conditional distribution of X2 on X1=1 (also a NormalDistribution object)
conditional = distribution.conditional(2,1,1)

# Regress X0 on X1 and X2 in the population setting (no estimation errors)
(coefs, intercept) = distribution.regress(0, [1,2])
```
