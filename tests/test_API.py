import pytest

from . import lsbase
import lshmm as ls
import lshmm.core as core
import lshmm.fb_diploid as fbd
import lshmm.fb_haploid as fbh
import lshmm.vit_diploid as vd
import lshmm.vit_haploid as vh


class TestForwardBackwardHaploid(lsbase.ForwardBackwardAlgorithmBase):
    def verify(self, ts, scale_mutation_rate, include_ancestors):
        for n, m, H_vs, s, e_vs, r, mu in self.get_examples_pars(
            ts,
            ploidy=1,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
            include_extreme_rates=True,
        ):
            num_alleles = core.get_num_alleles(H_vs, s)
            F_vs, c_vs, ll_vs = fbh.forwards_ls_hap(
                n=n,
                m=m,
                H=H_vs,
                s=s,
                e=e_vs,
                r=r,
            )
            B_vs = fbh.backwards_ls_hap(
                n=n,
                m=m,
                H=H_vs,
                s=s,
                e=e_vs,
                c=c_vs,
                r=r,
            )
            F, c, ll = ls.forwards(
                reference_panel=H_vs,
                query=s,
                num_alleles=num_alleles,
                prob_recombination=r,
                prob_mutation=mu,
                scale_mutation_rate=scale_mutation_rate,
                normalise=True,
            )
            B = ls.backwards(
                reference_panel=H_vs,
                query=s,
                num_alleles=num_alleles,
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
    def test_ts_simple_n10_no_recomb(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n10_no_recomb()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_simple_n6(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n6()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_simple_n8(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n8()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_simple_n8_high_recomb(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n8_high_recomb()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_simple_n16(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n16()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_larger(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_custom_pars(
            ref_panel_size=45, length=1e5, mean_r=1e-5, mean_mu=1e-5
        )
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )


class TestForwardBackwardDiploid(lsbase.ForwardBackwardAlgorithmBase):
    def verify(self, ts, scale_mutation_rate, include_ancestors):
        for n, m, H_vs, query, e_vs, r, mu in self.get_examples_pars(
            ts,
            ploidy=2,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
            include_extreme_rates=True,
        ):
            G_vs = core.convert_haplotypes_to_phased_genotypes(H_vs)
            s = core.convert_haplotypes_to_unphased_genotypes(query)
            num_alleles = core.get_num_alleles(H_vs, query)

            F_vs, c_vs, ll_vs = fbd.forward_ls_dip_loop(
                n=n,
                m=m,
                G=G_vs,
                s=s,
                e=e_vs,
                r=r,
                norm=True,
            )
            B_vs = fbd.backward_ls_dip_loop(
                n=n,
                m=m,
                G=G_vs,
                s=s,
                e=e_vs,
                c=c_vs,
                r=r,
            )
            F, c, ll = ls.forwards(
                reference_panel=G_vs,
                query=s,
                num_alleles=num_alleles,
                prob_recombination=r,
                prob_mutation=mu,
                scale_mutation_rate=scale_mutation_rate,
                normalise=True,
            )
            B = ls.backwards(
                reference_panel=G_vs,
                query=s,
                num_alleles=num_alleles,
                normalisation_factor_from_forward=c,
                prob_recombination=r,
                prob_mutation=mu,
                scale_mutation_rate=scale_mutation_rate,
            )

            self.assertAllClose(F, F_vs)
            self.assertAllClose(B, B_vs)
            self.assertAllClose(ll_vs, ll)

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_simple_n10_no_recomb(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n10_no_recomb()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_simple_n6(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n6()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_simple_n8(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n8()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_simple_n8_high_recomb(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n8_high_recomb()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_simple_n16(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n16()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_larger(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_custom_pars(
            ref_panel_size=45, length=1e5, mean_r=1e-5, mean_mu=1e-5
        )
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )


class TestViterbiHaploid(lsbase.ViterbiAlgorithmBase):
    def verify(self, ts, scale_mutation_rate, include_ancestors):
        for n, m, H_vs, s, e_vs, r, mu in self.get_examples_pars(
            ts,
            ploidy=1,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
            include_extreme_rates=True,
        ):
            num_alleles = core.get_num_alleles(H_vs, s)
            V_vs, P_vs, ll_vs = vh.forwards_viterbi_hap_lower_mem_rescaling(
                n=n,
                m=m,
                H=H_vs,
                s=s,
                e=e_vs,
                r=r,
            )
            path_vs = vh.backwards_viterbi_hap(m=m, V_last=V_vs, P=P_vs)
            path, ll = ls.viterbi(
                reference_panel=H_vs,
                query=s,
                num_alleles=num_alleles,
                prob_recombination=r,
                prob_mutation=mu,
                scale_mutation_rate=scale_mutation_rate,
            )
            self.assertAllClose(ll_vs, ll)
            self.assertAllClose(path_vs, path)

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_simple_n10_no_recomb(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n10_no_recomb()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_simple_n6(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n6()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_simple_n8(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n8()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_simple_n8_high_recomb(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n8_high_recomb()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_simple_n16(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n16()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [True, False])
    def test_ts_larger(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_custom_pars(
            ref_panel_size=46, length=1e5, mean_r=1e-5, mean_mu=1e-5
        )
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )


class TestViterbiDiploid(lsbase.ViterbiAlgorithmBase):
    def verify(self, ts, scale_mutation_rate, include_ancestors):
        for n, m, H_vs, query, e_vs, r, mu in self.get_examples_pars(
            ts,
            ploidy=2,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
            include_extreme_rates=True,
        ):
            G_vs = core.convert_haplotypes_to_phased_genotypes(H_vs)
            s = core.convert_haplotypes_to_unphased_genotypes(query)
            num_alleles = core.get_num_alleles(H_vs, query)

            V_vs, P_vs, ll_vs = vd.forwards_viterbi_dip_low_mem(
                n=n,
                m=m,
                G=G_vs,
                s=s,
                e=e_vs,
                r=r,
            )
            path_vs = vd.backwards_viterbi_dip(m=m, V_last=V_vs, P=P_vs)
            phased_path_vs = vd.get_phased_path(n=n, path=path_vs)
            path, ll = ls.viterbi(
                reference_panel=G_vs,
                query=s,
                num_alleles=num_alleles,
                prob_recombination=r,
                prob_mutation=mu,
                scale_mutation_rate=scale_mutation_rate,
            )

            self.assertAllClose(ll_vs, ll)
            self.assertAllClose(phased_path_vs, path)

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_simple_n10_no_recomb(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n10_no_recomb()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_simple_n6(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n6()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_simple_n8(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n8()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_simple_n8_high_recomb(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n8_high_recomb()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_simple_n16(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_simple_n16()
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )

    @pytest.mark.parametrize("scale_mutation_rate", [True, False])
    @pytest.mark.parametrize("include_ancestors", [False])
    def test_ts_larger(self, scale_mutation_rate, include_ancestors):
        ts = self.get_ts_custom_pars(
            ref_panel_size=45, length=1e5, mean_r=1e-5, mean_mu=1e-5
        )
        self.verify(
            ts,
            scale_mutation_rate=scale_mutation_rate,
            include_ancestors=include_ancestors,
        )
