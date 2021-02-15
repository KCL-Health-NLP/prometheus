import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.regression.mixed_linear_model as mlm


def make_smf_formula(target, covariates, timestamp=None):
    str_cov = ' + '.join(covariates)
    if timestamp is not None:
        str_cov = timestamp + ' + ' + str_cov
        add_slope = ' + ' + timestamp + ' * '
        str_cov += add_slope + add_slope.join(covariates)
    return target + ' ~ ' + str_cov


def fit_mlm(df, group, target, covariates, timestamp, rdn_slope=True, method=['lbfgs']):
    r_formula = make_smf_formula(target=target, covariates=covariates, timestamp=timestamp)
    if rdn_slope:
        # random intercept, and random slope (with respect to time)
        md = smf.mixedlm(r_formula, df, groups=df[group], re_formula='~' + timestamp)
    else:
        # random intercept only
        md = smf.mixedlm(r_formula, df, groups=df[group])
    mdf = md.fit(method=method, reml=True)  # other methods lbfgs bfgs cg
    print(mdf.summary().tables[1].loc[pd.to_numeric(mdf.summary().tables[1]['P>|z|']) <= 0.05])
    return mdf.summary()


def fit_mlm_constraint(df, group, target, covariates, timestamp, rdn_slope=True, method=['lbfgs']):
    # fit a model in which the two random effects are constrained to be uncorrelated:
    r_formula = make_smf_formula(target=target, covariates=covariates, timestamp=timestamp)
    md = smf.mixedlm(r_formula, df, groups=df[group], re_formula='~' + timestamp)
    free = sm.regression.mixed_linear_model.MixedLMParams.from_components(np.ones(2), np.eye(2))

    mdf = md.fit(free=free, method=method)
    print(mdf.summary())
    return mdf.summary()
