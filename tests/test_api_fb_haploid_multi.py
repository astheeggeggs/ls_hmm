import pytest

from . import lsbase
import lshmm as ls
import lshmm.core as core
import lshmm.fb_haploid as fbh


class TestForwardBackwardHaploid(lsbase.ForwardBackwardAlgorithmBase):
    def verify(self, ts, scale_mutation_rate, include_ancestors):
        ploidy = 1
        for n, m, H_vs, s, e_vs, r, mu in self.get_examples_pars(
            ts,
            ploidy=ploidy,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
            include_extreme_rates=True,
        ):
            emission_func = core.get_emission_probability_haploid
            F_vs, c_vs, ll_vs = fbh.forwards_ls_hap(
                n=n,
                m=m,
                H=H_vs,
                s=s,
                e=e_vs,
                r=r,
                emission_func=emission_func,
            )
            B_vs = fbh.backwards_ls_hap(
                n=n,
                m=m,
                H=H_vs,
                s=s,
                e=e_vs,
                c=c_vs,
                r=r,
                emission_func=emission_func,
            )
            F, c, ll = ls.forwards(
                reference_panel=H_vs,
                query=s,
                ploidy=ploidy,
                prob_recombination=r,
                prob_mutation=mu,
                scale_mutation_rate=scale_mutation_rate,
                normalise=True,
            )
            B = ls.backwards(
                reference_panel=H_vs,
                query=s,
                ploidy=ploidy,
                normalisation_factor_from_forward=c,
                prob_recombination=r,
                prob_mutation=mu,
                scale_mutation_rate=scale_mutation_rate,
            )
            self.assertAllClose(F, F_vs)
            self.assertAllClose(B, B_vs)
            self.assertAllClose(ll_vs, ll)

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_multiallelic_n10_no_recomb(
        self, scale_mutation_rate, include_ancestors
    ):
        ts = self.get_ts_multiallelic_n10_no_recomb()
        self.verify(ts, scale_mutation_rate, include_ancestors)

    @pytest.mark.parametrize("num_samples", [6, 8, 16])
    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_multiallelic_n16(
        self, num_samples, scale_mutation_rate, include_ancestors
    ):
        ts = self.get_ts_multiallelic(num_samples)
        self.verify(ts, scale_mutation_rate, include_ancestors)
