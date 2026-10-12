# %% [markdown]
# ## Target distributions
#
# One numeric output per confirmed column. A later fit can use only
# the rows where every output is present.

# %%
y = FRAME[TARGETS]
complete_target_rows = int(y.notna().all(axis=1).sum())
target_summary = y.describe().T
target_summary["skew"] = y.skew(numeric_only=True)
target_summary["missing_count"] = y.isna().sum()
target_summary["missing_rate"] = y.isna().mean()
target_summary["complete_target_rows"] = complete_target_rows
target_summary

# %%
long_targets = y.melt(var_name="target", value_name="value")
g = sns.displot(
    data=long_targets,
    x="value",
    col="target",
    col_wrap=3,
    facet_kws={"sharex": False, "sharey": False},
)
g.savefig(OUT / "target_distributions.png", bbox_inches="tight")
g

# %% [markdown]
# ## Target vs target
#
# Association among the outputs. A strong correlation describes the
# problem; it is not a feature to drop.

# %%
target_corr = y.corr(numeric_only=True)
target_corr

# %% [markdown]
# ## Feature vs targets
#
# A readable subset of features versus every target. Sibling targets
# stay out of the feature list. Cap at 12 columns, ranked by the
# strongest absolute Pearson with any target.

# %%
BIVARIATE_CAP = 12
others = [c for c in FRAME.columns if c not in TARGETS]
numeric = FRAME[others].select_dtypes("number")
if len(others) > BIVARIATE_CAP and not numeric.empty:
    strength = numeric.apply(
        lambda column: y.corrwith(column).abs().max(),
        axis=0,
    ).sort_values(ascending=False)
    bivariate_cols = [
        c for c in strength.index if pd.notna(strength[c])
    ][:BIVARIATE_CAP]
else:
    bivariate_cols = others[:BIVARIATE_CAP]
pd.Series(bivariate_cols, name="bivariate_columns")

# %%
numeric_bivariate = [
    c for c in bivariate_cols if pd.api.types.is_numeric_dtype(FRAME[c])
]
feature_long = FRAME[numeric_bivariate + list(TARGETS)].melt(
    id_vars=list(TARGETS),
    value_vars=numeric_bivariate,
    var_name="feature",
    value_name="value",
)
long = feature_long.melt(
    id_vars=["feature", "value"],
    value_vars=list(TARGETS),
    var_name="target",
    value_name="target_value",
)
g = sns.relplot(
    data=long,
    x="value",
    y="target_value",
    col="feature",
    row="target",
    alpha=0.4,
    facet_kws={"sharex": False, "sharey": False},
)
g.savefig(OUT / "bivariate_targets.png", bbox_inches="tight")
g

# %% [markdown]
# ## Leakage candidates
#
# Flags only — not a train/test split. Sibling targets are not
# features.

# %%
leakage_flags: list[str] = []
features = FRAME[others].select_dtypes("number")
for target in TARGETS:
    corr = features.corrwith(FRAME[target]).abs().sort_values(ascending=False)
    for col, value in corr.items():
        if value is not None and value >= 0.99:
            leakage_flags.append(f"{col} abs(Pearson) vs {target} = {value:.3f}")
leakage_summary = pd.DataFrame({"flag": leakage_flags or ["none"]})
leakage_summary
