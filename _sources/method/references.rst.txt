References
==========

Core SPADE publications
------------------------

1. **Qiu, P., Simonds, E.F., Bendall, S.C., Gibbs, K.D. Jr., Bruggner, R.V., Linderman, M.D., Sachs, K.,
   Nolan, G.P., & Plevritis, S.K.** (2011). "Extracting a cellular hierarchy from high-dimensional cytometry
   data with SPADE." *Nature Biotechnology*, 29(10), 886--891.
   `doi:10.1038/nbt.1991 <https://doi.org/10.1038/nbt.1991>`_

   The original SPADE paper. Introduces density-dependent downsampling + agglomerative clustering + MST
   for CyTOF data.

2. **Qiu, P.** (2017). "Toward deterministic and semiautomated SPADE analysis." *Cytometry Part A*,
   91(7), 714--727. `doi:10.1002/cyto.a.23068 <https://doi.org/10.1002/cyto.a.23068>`_

   Addresses stochasticity and proposes deterministic variants of SPADE.

Key applications
-----------------

3. **Bendall, S.C., Simonds, E.F., Qiu, P., et al.** (2011). "Single-cell mass cytometry of differential
   immune and drug responses across a human hematopoietic continuum." *Science*, 332(6030), 687--696.
   `doi:10.1126/science.1198704 <https://doi.org/10.1126/science.1198704>`_

   First high-profile CyTOF + SPADE application — mapping human hematopoiesis.

4. **Levine, J.H., Simonds, E.F., Bendall, S.C., et al.** (2015). "Data-Driven Phenotypic Dissection of
   AML Reveals Progenitor-like Cells that Correlate with Prognosis." *Cell*, 162(1), 184--197.
   `doi:10.1016/j.cell.2015.05.047 <https://doi.org/10.1016/j.cell.2015.05.047>`_

   Introduces PhenoGraph; includes SPADE comparisons. Source of the **Levine_32dim** and **Levine_13dim**
   benchmark datasets.

Benchmark studies
------------------

5. **Samusik, N., Good, Z., Spitzer, M.H., Davis, K.L., & Nolan, G.P.** (2016). "Automated mapping of
   phenotype space with single-cell data." *Nature Methods*, 13(6), 493--496.
   `doi:10.1038/nmeth.3863 <https://doi.org/10.1038/nmeth.3863>`_

   Systematic comparison of SPADE, FlowSOM, PhenoGraph, and other methods. Source of the **Samusik_01**
   benchmark dataset.

6. **Weber, L.M. & Robinson, M.D.** (2016). "Comparison of clustering methods for high-dimensional
   single-cell flow and mass cytometry data." *Cytometry Part A*, 89(12), 1084--1096.
   `doi:10.1002/cyto.a.23030 <https://doi.org/10.1002/cyto.a.23030>`_

   Comprehensive benchmark of 18 clustering methods including SPADE, with standardized evaluation metrics.

Related methods
----------------

7. **Van Gassen, S., Callebaut, B., Van Helden, M.J., et al.** (2015). "FlowSOM: Using self-organizing
   maps for visualization and interpretation of cytometry data." *Cytometry Part A*, 87(7), 636--645.
   `doi:10.1002/cyto.a.22625 <https://doi.org/10.1002/cyto.a.22625>`_

   FlowSOM — often compared to SPADE. Faster, also produces a tree, but uses SOMs instead of
   density-dependent downsampling.

8. **Levine, J.H., et al.** (2015). See reference 4 above.

   PhenoGraph — graph-based clustering using k-NN + Louvain community detection. Produces flat clusters
   (no tree), but often better cluster purity.

Datasets used in densitree benchmarks
--------------------------------------

9. **Levine_32dim**: 81,747 cells, 32 markers, 14 manually gated populations. From reference 4. Available
   via `FlowRepository FR-FCM-ZZPH <https://flowrepository.org/id/FR-FCM-ZZPH>`_ and
   `Weber & Robinson's HDCytoData <https://github.com/lmweber/HDCytoData>`_.

10. **Samusik_01**: 86,864 cells, 39 markers, 24 manually gated populations. From reference 5. Available
    via `FlowRepository FR-FCM-ZZYA <https://flowrepository.org/id/FR-FCM-ZZYA>`_ and
    `HDCytoData <https://github.com/lmweber/HDCytoData>`_.
