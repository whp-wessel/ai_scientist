# Missingness Diagnostics (Exploratory)

Generated: 2025-10-16T13:30:33.217638+00:00

## Overview

This exploratory report summarizes missingness patterns for the self-love and parental emotional abuse items.

### Missingness Rates

```
     variable_short                                                                 variable_name missing_count  missing_pct  nonmissing_count  nonmissing_pct
          self_love                                                       I love myself (2l8994l)           <10          NaN             14436           99.95
parental_abuse_0_12 during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)            17         0.12             14426           99.88
```

### Logistic Models for Missingness Indicators

#### self_love

Observations (listwise complete): 14443

```
                         Results: Logit
================================================================
Model:              Logit             Method:           MLE     
Dependent Variable: missing_self_love Pseudo R-squared: 0.117   
Date:               2025-10-16 15:30  AIC:              118.6786
No. Observations:   14443             BIC:              164.1464
Df Model:           5                 Log-Likelihood:   -53.339 
Df Residuals:       14437             LL-Null:          -60.423 
Converged:          1.0000            LLR p-value:      0.014584
No. Iterations:     13.0000           Scale:            1.0000  
-----------------------------------------------------------------
             Coef.   Std.Err.     z     P>|z|    [0.025    0.975]
-----------------------------------------------------------------
const       -8.9857    1.6260  -5.5263  0.0000  -12.1727  -5.7988
selfage      0.0623    0.0290   2.1485  0.0317    0.0055   0.1190
classchild   0.7779    0.3377   2.3036  0.0212    0.1160   1.4398
networth    -0.1393    0.2097  -0.6645  0.5064   -0.5502   0.2716
education   -0.7174    0.2397  -2.9924  0.0028   -1.1872  -0.2475
biomale     -0.1533    0.7768  -0.1973  0.8436   -1.6758   1.3692
================================================================

```

#### parental_abuse_0_12

Observations (listwise complete): 14443

```
                               Results: Logit
============================================================================
Model:              Logit                       Method:           MLE       
Dependent Variable: missing_parental_abuse_0_12 Pseudo R-squared: 0.084     
Date:               2025-10-16 15:30            AIC:              253.2798  
No. Observations:   14443                       BIC:              298.7476  
Df Model:           5                           Log-Likelihood:   -120.64   
Df Residuals:       14437                       LL-Null:          -131.65   
Converged:          1.0000                      LLR p-value:      0.00051863
No. Iterations:     12.0000                     Scale:            1.0000    
-------------------------------------------------------------------------------
                 Coef.     Std.Err.       z       P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------
const           -8.0153      1.2781    -6.2711    0.0000    -10.5204    -5.5102
selfage         -0.0217      0.0324    -0.6687    0.5037     -0.0852     0.0418
classchild       0.6498      0.2192     2.9646    0.0030      0.2202     1.0795
networth        -0.0758      0.1449    -0.5230    0.6010     -0.3597     0.2082
education       -0.3099      0.1536    -2.0179    0.0436     -0.6108    -0.0089
biomale          1.7221      0.7602     2.2652    0.0235      0.2321     3.2122
============================================================================

```

_Exploratory output – do not treat as confirmatory evidence._