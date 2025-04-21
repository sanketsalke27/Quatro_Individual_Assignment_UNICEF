import pandas as pd
import plotly.express as px

# Load & merge data
df_ind = pd.read_csv("unicef_indicator_2.csv")
df_meta = pd.read_csv("unicef_metadata.csv")
df = pd.merge(df_ind, df_meta, on=["alpha_3_code","time_period"], how="left")

# 1) Time‐Series HTML
ts = df.groupby("time_period", as_index=False).agg({
    "obs_value":"mean",
    "Life expectancy at birth, total (years)":"mean"
}).rename(columns={
    "obs_value":"Coverage",
    "Life expectancy at birth, total (years)":"LifeExpectancy"
})
fig1 = px.line(ts, x="time_period", y=["Coverage","LifeExpectancy"],
               labels={"time_period":"Year","value":"Value","variable":"Indicator"},
               title="Vaccination Coverage vs. Life Expectancy")
fig1.update_layout(legend_title_text="")
fig1.write_html("time_series.html", include_plotlyjs="cdn")
print("✓ time_series.html generated")

# 2) Choropleth Map HTML
# (assumes you have a “country” column with ISO codes)
fig2 = px.choropleth(df[df.time_period == df.time_period.max()],
                     locations="alpha_3_code", color="obs_value",
                     color_continuous_scale="Viridis",
                     labels={"obs_value":"Coverage (%)"},
                     title=f"Global RCV1 Coverage ({df.time_period.max()})")
fig2.write_html("map.html", include_plotlyjs="cdn")
print("✓ map.html generated")

# 3) Scatter + Regression HTML
fig3 = px.scatter(df, x="GDP per capita (constant 2015 US$)", y="obs_value",
                  trendline="ols",
                  labels={"obs_value":"Coverage (%)"},
                  title="GDP per Capita vs. Vaccination Coverage")
fig3.write_html("scatter.html", include_plotlyjs="cdn")
print("✓ scatter.html generated")

# 4) Bar Chart HTML (Top 10 Growth Rates)
# Compute growth rate per country between first and last year
df_sorted = df.sort_values(["alpha_3_code", "time_period"])
summary = (
    df_sorted
      .groupby("alpha_3_code", as_index=False)
      .agg(
          first_obs=("obs_value", "first"),
          last_obs=("obs_value", "last")
      )
)
summary["GrowthRate"] = (summary["last_obs"] / summary["first_obs"] - 1) * 100

top10 = summary.nlargest(10, "GrowthRate")

fig4 = px.bar(
    top10,
    x="alpha_3_code",
    y="GrowthRate",
    labels={"alpha_3_code":"Country","GrowthRate":"% Growth"},
    title="Top 10 Countries by Vaccination Coverage Growth"
)
fig4.write_html("bar.html", include_plotlyjs="cdn")
print("✓ bar.html generated")
