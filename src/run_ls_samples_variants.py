import time

import msprime
import numba as nb
import numpy as np
from forward_backward.fb_diploid_samples_variants import *
from forward_backward.fb_haploid_samples_variants import *
from simulate.sim_samples_variants import *
from viterbi.vit_diploid_samples_variants import *
from viterbi.vit_haploid_samples_variants import *

n = 10

H, s, r, mu, e, m = rand_for_testing_hap_better(n, length=1e5)

print(f"\nHaploid")
print(f"\nforwards backwards without rescaling numba...")
F, c, ll = forwards_ls_hap(n, m, H, s, e, r, norm=False)
B = backwards_ls_hap(n, m, H, s, e, c, r)
tic = time.perf_counter()
F, c, ll = forwards_ls_hap(n, m, H, s, e, r, norm=False)
B = backwards_ls_hap(n, m, H, s, e, c, r)
print(f"log-likelihood: {ll}")
print(np.log10(np.sum(F * B, 0)))
toc = time.perf_counter()
print(f"forwards backwards in {toc - tic:0.4f} seconds")

print(f"\nforwards backwards numba...")
F, c, ll = forwards_ls_hap(n, m, H, s, e, r)
B = backwards_ls_hap(n, m, H, s, e, c, r)
tic = time.perf_counter()
F, c, ll = forwards_ls_hap(n, m, H, s, e, r)
B = backwards_ls_hap(n, m, H, s, e, c, r)
ll = np.sum(np.log10(c))
print(f"log-likelihood: {ll}")
print(np.sum(F * B, 0))
toc = time.perf_counter()
print(f"forwards backwards in {toc - tic:0.4f} seconds")

print(f"\nnaive viterbi numba...")
V, P, ll = forwards_viterbi_hap_naive(n, m, H, s, e, r)
path = backwards_viterbi_hap(m, V[:, m - 1], P)
tic = time.perf_counter()
V, P, ll = forwards_viterbi_hap_naive(n, m, H, s, e, r)
path = backwards_viterbi_hap(m, V[:, m - 1], P)
print(f"log-likelihood: {ll}")
toc = time.perf_counter()
print(f"took {toc - tic:0.4f} seconds")

print(f"\nnaive low mem viterbi numba...")
V, P, ll = forwards_viterbi_hap_naive_low_mem(n, m, H, s, e, r)
path = backwards_viterbi_hap(m, V, P)
tic = time.perf_counter()
V, P, ll = forwards_viterbi_hap_naive_low_mem(n, m, H, s, e, r)
path = backwards_viterbi_hap(m, V, P)
print(f"log-likelihood: {ll}")
toc = time.perf_counter()
print(f"took {toc - tic:0.4f} seconds")

print(f"\nnaive low mem rescaling viterbi numba")
V, P, ll = forwards_viterbi_hap_naive_low_mem_rescaling(n, m, H, s, e, r)
path = backwards_viterbi_hap(m, V, P)
tic = time.perf_counter()
V, P, ll = forwards_viterbi_hap_naive_low_mem_rescaling(n, m, H, s, e, r)
path = backwards_viterbi_hap(m, V, P)
print(f"log-likelihood: {ll}")
toc = time.perf_counter()
print(f"took {toc - tic:0.4f} seconds")

print(f"\nnaive vector viterbi...")
V, P, ll = forwards_viterbi_hap_naive_vec(n, m, H, s, e, r)
path = backwards_viterbi_hap(m, V[:, m - 1], P)
tic = time.perf_counter()
V, P, ll = forwards_viterbi_hap_naive_vec(n, m, H, s, e, r)
path = backwards_viterbi_hap(m, V[:, m - 1], P)
print(f"log-likelihood: {ll}")
toc = time.perf_counter()
print(f"took {toc - tic:0.4f} seconds")

print(f"\nfinal viterbi numba...")
V, P, ll = forwards_viterbi_hap_lower_mem_rescaling(n, m, H, s, e, r)
path = backwards_viterbi_hap(m, V, P)
tic = time.perf_counter()
V, P, ll = forwards_viterbi_hap_lower_mem_rescaling(n, m, H, s, e, r)
path = backwards_viterbi_hap(m, V, P)
print(f"log-likelihood: {ll}")
toc = time.perf_counter()
print(f"took {toc - tic:0.4f} seconds")


# Diploid Li and Stephens
# Yes, I know there's a factor of two that we can squeeze out of this.
n = 50
H, G, s, r, mu, e, m = rand_for_testing_dip_better(n, length=5e5)

print(f"\nDiploid")
print(f"\nforwards backwards without rescaling numba...")
F, c, ll = forwards_ls_dip(n, m, G, s, e, r, norm=False)
B = backwards_ls_dip(n, m, G, s, e, c, r)
tic = time.perf_counter()
F, c, ll = forwards_ls_dip(n, m, G, s, e, r, norm=False)
print(f"log-likelihood: {ll}")
B = backwards_ls_dip(n, m, G, s, e, c, r)
toc = time.perf_counter()
print(f"took {toc - tic:0.4f} seconds")

print(f"\nforwards backwards numba...")
F, ll = forward_ls_dip_starting_point(n, m, G, s, e, r)
B = backward_ls_dip_starting_point(n, m, G, s, e, r)
tic = time.perf_counter()
F, ll = forward_ls_dip_starting_point(n, m, G, s, e, r)
print(f"log-likelihood: {ll}")
B = backward_ls_dip_starting_point(n, m, G, s, e, r)
toc = time.perf_counter()
print(f"took {toc - tic:0.4f} seconds")

print(f"\nforwards backwards...")
F, c, ll = forward_ls_dip_loop(n, m, G, s, e, r, norm=False)
B = backward_ls_dip_loop(n, m, G, s, e, c, r)
tic = time.perf_counter()
F, c, ll = forward_ls_dip_loop(n, m, G, s, e, r, norm=False)
print(f"log-likelihood: {ll}")
B = backward_ls_dip_loop(n, m, G, s, e, c, r)
toc = time.perf_counter()
print(f"took {toc - tic:0.4f} seconds")

print(f"\nnaive viterbi...")
V, P, ll = forwards_viterbi_dip_naive(n, m, G, s, e, r)
path = backwards_viterbi_dip(n, m, V[:, :, m - 1], P)
tic = time.perf_counter()
V, P, ll = forwards_viterbi_dip_naive(n, m, G, s, e, r)
print(f"log-likelihood: {ll}")
path = backwards_viterbi_dip(n, m, V[:, :, m - 1], P)
toc = time.perf_counter()
phased_path = get_phased_path(n, path)
print(f"took {toc - tic:0.4f} seconds")
path_ll = path_ll_dip(n, m, G, phased_path, s, e, r)
print(f"path log-likelihood: {path_ll}")

print(f"\nnaive low mem viterbi...")
V, P, ll = forwards_viterbi_dip_naive_low_mem(n, m, G, s, e, r)
path = backwards_viterbi_dip(n, m, V, P)
tic = time.perf_counter()
V, P, ll = forwards_viterbi_dip_naive_low_mem(n, m, G, s, e, r)
print(f"log-likelihood: {ll}")
path = backwards_viterbi_dip(n, m, V, P)
toc = time.perf_counter()
phased_path = get_phased_path(n, path)
print(f"took {toc - tic:0.4f} seconds")
path_ll = path_ll_dip(n, m, G, phased_path, s, e, r)
print(f"path log-likelihood: {path_ll}")

print(f"\nlow mem viterbi...")
V, P, ll = forwards_viterbi_dip_low_mem(n, m, G, s, e, r)
path = backwards_viterbi_dip(n, m, V, P)
tic = time.perf_counter()
V, P, ll = forwards_viterbi_dip_low_mem(n, m, G, s, e, r)
print(f"log-likelihood: {ll}")
path = backwards_viterbi_dip(n, m, V, P)
toc = time.perf_counter()
phased_path = get_phased_path(n, path)
print(f"took {toc - tic:0.4f} seconds")
path_ll = path_ll_dip(n, m, G, phased_path, s, e, r)
print(f"path log-likelihood: {path_ll}")

print(f"\nvectorised naive viterbi...")
V, P, ll = forwards_viterbi_dip_naive_vec(n, m, G, s, e, r)
path = backwards_viterbi_dip(n, m, V[:, :, m - 1], P)
tic = time.perf_counter()
V, P, ll = forwards_viterbi_dip_naive_vec(n, m, G, s, e, r)
print(f"log-likelihood: {ll}")
path = backwards_viterbi_dip(n, m, V[:, :, m - 1], P)
toc = time.perf_counter()
phased_path = get_phased_path(n, path)
print(f"took {toc - tic:0.4f} seconds")
path_ll = path_ll_dip(n, m, G, phased_path, s, e, r)
print(f"path log-likelihood: {path_ll}")

print(f"\nfully vectorised naive viterbi...")
tic = time.perf_counter()
V, P, ll = forwards_viterbi_dip_naive_full_vec(n, m, G, s, e, r)
print(f"log-likelihood: {ll}")
path = backwards_viterbi_dip(n, m, V[:, :, m - 1], P)
toc = time.perf_counter()
phased_path = get_phased_path(n, path)
print(f"took {toc - tic:0.4f} seconds")
path_ll = path_ll_dip(n, m, G, phased_path, s, e, r)
print(f"path log-likelihood: {path_ll}")
