"""External API definitions."""
import warnings

import numpy as np

from .forward_backward.fb_diploid_variants_samples import (
    backward_ls_dip_loop,
    forward_ls_dip_loop,
)
from .forward_backward.fb_haploid_variants_samples import (
    backwards_ls_hap,
    forwards_ls_hap,
)
from .vit_diploid_variants_samples import (
    backwards_viterbi_dip,
    forwards_viterbi_dip_low_mem,
    get_phased_path,
    path_ll_dip,
)
from .vit_haploid_variants_samples import (
    backwards_viterbi_hap,
    forwards_viterbi_hap_lower_mem_rescaling,
    path_ll_hap,
)

EQUAL_BOTH_HOM = 4
UNEQUAL_BOTH_HOM = 0
BOTH_HET = 7
REF_HOM_OBS_HET = 1
REF_HET_OBS_HOM = 2
MISSING_INDEX = 3


def check_alleles(alleles, m):
    """
    Checks the specified allele list and returns a list of lists
    of alleles of length num_sites.
    If alleles is a 1D list of strings, assume that this list is used
    for each site and return num_sites copies of this list.
    Otherwise, raise a ValueError if alleles is not a list of length
    num_sites.
    """
    if isinstance(alleles[0], str):
        return np.int8([len(alleles) for _ in range(m)])
    if len(alleles) != m:
        raise ValueError("Malformed alleles list")
    n_alleles = np.int8([(len(alleles_site)) for alleles_site in alleles])
    return n_alleles


def checks(
    reference_panel,
    query,
    mutation_rate,
    recombination_rate,
    scale_mutation_based_on_n_alleles,
):
    """
    Checks that the input data and parameters are valid.

    The reference panel must be a matrix of size (m, n) or (m, n, n).
    The query must be a matrix of size (k, m) or (k, m, 2).

    m = number of sites.
    n = number of samples in the reference panel (haplotypes, not individuals).
    k = number of samples in the query (haplotypes, not individuals).

    :param numpy.ndarray(dtype=int) reference_panel: Matrix of size (m, n) or (m, n, n).
    :param numpy.ndarray(dtype=int) query: Matrix of size (k, m) or (k, m, 2).
    :param numpy.ndarray(dtype=float) mutation_rate: Scalar or vector of length m.
    :param numpy.ndarray(dtype=float) recombination_rate: Scalar or vector of length m.
    :param bool scale_mutation_based_on_n_alleles: Whether to scale mutation rate based on the number of alleles (True) or not (False).
    :return: n, m, ploidy
    :rtype: tuple
    """
    # Check reference panel
    if not len(reference_panel.shape) in (2, 3):
        raise ValueError("Reference panel array must have 2 or 3 dimensions.")

    if len(reference_panel.shape) == 2:
        m, n = reference_panel.shape
        ploidy = 1
    else:
        m, n, _ = reference_panel.shape
        ploidy = 2

    if ploidy == 2 and reference_panel.shape[1] != reference_panel.shape[2]:
        raise ValueError(
            "Reference_panel dimensions are incorrect, "
            "perhaps a sample x sample x variant matrix was passed. "
            "Expected sites x samples x samples."
        )

    # Check query
    if not len(query.shape) in (2, 3):
        raise ValueError("Query array must have 2 or 3 dimensions.")

    if len(query.shape) == 2:
        _, m_query = query.shape
        ploidy_query = 1
    else:
        _, m_query, z = query.shape
        if z != 2:
            raise ValueError(f"Query array is expected to have a ploidy of 2, but has {z}")
        ploidy_query = 2

    if m_query != m:
        raise ValueError(
            "Number of sites in query does not match reference panel. "
            "If haploid, ensure a sites x samples matrix is passed."
        )

    if ploidy != ploidy_query:
        raise ValueError(f"Ploidy {ploidy} of reference panel does not match ploidy {ploidy_query} of query.")

    # Ensure that the mutation rate is either a scalar or vector of length m
    if isinstance(mutation_rate, (int, float)):
        if not scale_mutation_based_on_n_alleles:
            warnings.warn(
                "Passed a scalar mutation rate, "
                "but not rescaling this mutation rate conditional on the number of alleles at the site."
            )
    elif isinstance(mutation_rate, np.ndarray) and mutation_rate.shape[0] == m:
        if scale_mutation_based_on_n_alleles:
            warnings.warn(
                "Passed a vector of mutation rates, "
                "but rescaling each mutation rate conditional on the number of alleles at each site."
            )
    elif mutation_rate is None:
        warnings.warn(
          "No mutation rate passed, setting mutation rate based on Li and Stephens 2003, "
          "equations (A2) and (A3)"
        )
    else:
        raise ValueError(f"Mutation rate is not None, a scalar, or vector of length m: {m}")

    # Ensure that the recombination rate is either a scalar or a vector of length m
    if not (
        isinstance(recombination_rate, (int, float)) or \
        (isinstance(recombination_rate, np.ndarray) and recombination_rate.shape[0] == m)
    ):
        raise ValueError(f"Recombination_rate is not a scalar or vector of length m: {m}")

    return (n, m, ploidy)


def set_emission_probabilities(
    n,
    m,
    reference_panel,
    query,
    alleles,
    mutation_rate,
    ploidy,
    scale_mutation_based_on_n_alleles,
):
    # Check alleles should go in here, and modify e before passing to the algorithm
    # If alleles is not passed, we don't perform a test of alleles, but set n_alleles based on the reference_panel.
    if alleles is None:
        n_alleles = np.int8(
            [
                len(np.unique(np.append(reference_panel[j, :], query[:, j])))
                for j in range(reference_panel.shape[0])
            ]
        )
    else:
        n_alleles = check_alleles(alleles, m)

    if mutation_rate is None:
        # Set the mutation rate to be the proposed mutation rate in Li and Stephens (2003).
        theta_tilde = 1 / np.sum([1 / k for k in range(1, n - 1)])
        mutation_rate = 0.5 * (theta_tilde / (n + theta_tilde))

    if isinstance(mutation_rate, float):
        mutation_rate = mutation_rate * np.ones(m)

    if ploidy == 1:
        # Haploid
        # Evaluate emission probabilities here, using the mutation rate - this can take a scalar or vector.
        e = np.zeros((m, 2))

        if scale_mutation_based_on_n_alleles:
            # Scale mutation based on the number of alleles - so the mutation rate is the mutation rate to one of the alleles.
            # The overall mutation rate is then (n_alleles - 1) * mutation_rate.
            e[:, 0] = mutation_rate - mutation_rate * np.equal(
                n_alleles, np.ones(m)
            )  # Added boolean in case we're at an invariant site
            e[:, 1] = 1 - (n_alleles - 1) * mutation_rate
        else:
            # No scaling based on the number of alleles - so the mutation rate is the mutation rate to anything.
            # Which means that we must rescale the mutation rate to a different allele, by the number of alleles.
            for j in range(m):
                if n_alleles[j] == 1:  # In case we're at an invariant site
                    e[j, 0] = 0
                    e[j, 1] = 1
                else:
                    e[j, 0] = mutation_rate[j] / (n_alleles[j] - 1)
                    e[j, 1] = 1 - mutation_rate[j]
    else:
        # Diploid
        # Evaluate emission probabilities here, using the mutation rate - this can take a scalar or vector.
        # DEV: there's a wrinkle here.
        e = np.zeros((m, 8))
        e[:, EQUAL_BOTH_HOM] = (1 - mutation_rate) ** 2
        e[:, UNEQUAL_BOTH_HOM] = mutation_rate ** 2
        e[:, BOTH_HET] = (1 - mutation_rate) ** 2 + mutation_rate ** 2
        e[:, REF_HOM_OBS_HET] = 2 * mutation_rate * (1 - mutation_rate)
        e[:, REF_HET_OBS_HOM] = mutation_rate * (1 - mutation_rate)
        e[:, MISSING_INDEX] = 1

    return e


def viterbi_hap(n, m, reference_panel, query, emissions, recombination_rate):

    V, P, log_likelihood = forwards_viterbi_hap_lower_mem_rescaling(
        n, m, reference_panel, query, emissions, recombination_rate
    )
    most_likely_path = backwards_viterbi_hap(m, V, P)

    return most_likely_path, log_likelihood


def viterbi_dip(n, m, reference_panel, query, emissions, recombination_rate):

    V, P, log_likelihood = forwards_viterbi_dip_low_mem(
        n, m, reference_panel, query, emissions, recombination_rate
    )
    unphased_path = backwards_viterbi_dip(m, V, P)
    most_likely_path = get_phased_path(n, unphased_path)

    return most_likely_path, log_likelihood


def forwards(
    reference_panel,
    query,
    recombination_rate,
    alleles=None,
    mutation_rate=None,
    scale_mutation_based_on_n_alleles=True,
):
    """
    Run the Li and Stephens forwards algorithm on haplotype or
    unphased genotype data.
    """

    n, m, ploidy = checks(
        reference_panel,
        query,
        mutation_rate,
        recombination_rate,
        scale_mutation_based_on_n_alleles,
    )

    emissions = set_emission_probabilities(
        n,
        m,
        reference_panel,
        query,
        alleles,
        mutation_rate,
        ploidy,
        scale_mutation_based_on_n_alleles,
    )

    if ploidy == 1:
        forward_function = forwards_ls_hap
    else:
        forward_function = forward_ls_dip_loop

    (
        forward_array,
        normalisation_factor_from_forward,
        log_likelihood,
    ) = forward_function(
        n, m, reference_panel, query, emissions, recombination_rate, norm=True
    )

    return forward_array, normalisation_factor_from_forward, log_likelihood


def backwards(
    reference_panel,
    query,
    normalisation_factor_from_forward,
    recombination_rate,
    alleles=None,
    mutation_rate=None,
    scale_mutation_based_on_n_alleles=True,
):
    """
    Run the Li and Stephens backwards algorithm on haplotype or
    unphased genotype data.
    """
    n, m, ploidy = checks(
        reference_panel,
        query,
        mutation_rate,
        recombination_rate,
        scale_mutation_based_on_n_alleles,
    )

    emissions = set_emission_probabilities(
        n,
        m,
        reference_panel,
        query,
        alleles,
        mutation_rate,
        ploidy,
        scale_mutation_based_on_n_alleles,
    )

    if ploidy == 1:
        backward_function = backwards_ls_hap
    else:
        backward_function = backward_ls_dip_loop

    backwards_array = backward_function(
        n,
        m,
        reference_panel,
        query,
        emissions,
        normalisation_factor_from_forward,
        recombination_rate,
    )

    return backwards_array


def viterbi(
    reference_panel,
    query,
    recombination_rate,
    alleles=None,
    mutation_rate=None,
    scale_mutation_based_on_n_alleles=True,
):
    """
    Run the Li and Stephens Viterbi algorithm on haplotype or
    unphased genotype data.
    """
    n, m, ploidy = checks(
        reference_panel,
        query,
        mutation_rate,
        recombination_rate,
        scale_mutation_based_on_n_alleles,
    )

    emissions = set_emission_probabilities(
        n,
        m,
        reference_panel,
        query,
        alleles,
        mutation_rate,
        ploidy,
        scale_mutation_based_on_n_alleles,
    )

    if ploidy == 1:
        viterbi_function = viterbi_hap
    else:
        viterbi_function = viterbi_dip

    most_likely_path, log_likelihood = viterbi_function(
        n, m, reference_panel, query, emissions, recombination_rate
    )

    return most_likely_path, log_likelihood


def path_ll(
    reference_panel,
    query,
    path,
    recombination_rate,
    alleles=None,
    mutation_rate=None,
    scale_mutation_based_on_n_alleles=True,
):

    n, m, ploidy = checks(
        reference_panel,
        query,
        mutation_rate,
        recombination_rate,
        scale_mutation_based_on_n_alleles,
    )

    emissions = set_emission_probabilities(
        n,
        m,
        reference_panel,
        query,
        alleles,
        mutation_rate,
        ploidy,
        scale_mutation_based_on_n_alleles,
    )

    if ploidy == 1:
        path_ll_function = path_ll_hap
    else:
        path_ll_function = path_ll_dip

    ll = path_ll_function(
        n, m, reference_panel, path, query, emissions, recombination_rate
    )

    return ll
