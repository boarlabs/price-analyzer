import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import matplotlib
# Example: create dummy hourly LMP data for 90 days
rng = pd.date_range("2025-01-01", periods=24*90, freq="H")
np.random.seed(42)
price = 30 + 10*np.sin(2*np.pi*rng.hour/24) + 5*np.cos(2*np.pi*rng.dayofweek/7) + np.random.normal(0, 3, len(rng))
df = pd.DataFrame({"timestamp": rng, "price": price})
#  Extract features

df["date"] = df["timestamp"].dt.date
df["hour"] = df["timestamp"].dt.hour

# fig = px.scatter(df, x="timestamp", y="price", title="Price Scatter Plot", labels={"timestamp": "Timestamp", "price": "Price"})
# fig.add_scatter(x=df['timestamp'], y=df['price'], mode='lines', name='Line')

# fig.show
# fig.show()
# Pivot so rows = days, columns = hours
daily_matrix = df.pivot_table(index="date", columns="hour", values="price")
daily_matrix = daily_matrix.fillna(method="ffill")  # Handle missing values


shape_mat   = daily_matrix.sub(daily_matrix.mean(axis=1), axis=0)
scaler      = StandardScaler(with_mean=True, with_std=True)
X           = scaler.fit_transform(shape_mat)      # rows = days, cols = hours
pca         = PCA(n_components=6, random_state=0).fit(X)
i
matplotlib.use("TkAgg")
plt.figure()
plt.plot(range(1, 7), pca.explained_variance_ratio_.cumsum(), marker='o')
plt.xlabel('Number of components')
plt.ylabel('Cumulative explained variance')
plt.title('How many PCs?')
plt.grid(True)
plt.show()
# X = daily_matrix.values  # shape (n_days, 24)


# fig1 = go.Figure()

# # Iterate over each day (each row in X)
# for i, row in enumerate(X):
#     fig1.add_trace(go.Scatter(
#         x=list(range(24)),  # Assuming 24 hours in a day
#         y=row,
#         mode='lines',
#         name=f'Day {i+1}'
#     ))

# fig1.update_layout(
#     title='Daily Data Traces',
#     xaxis_title='Hour of Day',
#     yaxis_title='Value',
#     legend_title='Day'
# )
# fig1.show()
# import matplotlib.pyplot as plt

# pca = PCA(n_components=2)
# X_pca = pca.fit_transform(X)

# print("Explained variance ratio:", pca.explained_variance_ratio_)


# num_components = len(pca.components_)
# fig2 = make_subplots(rows=num_components, cols=1, subplot_titles=[f"PCA Component {i}" for i in range(1, num_components + 1)])

# for i, component in enumerate(pca.components_, 1):
#     fig2.add_trace(
#         go.Scatter(x=list(range(24)), y=component, mode='lines', name=f'Component {i}'),
#         row=i, col=1
#     )

# fig2.update_layout(height=400 * num_components, width=800, title_text="PCA Components")
# fig2.update_xaxes(title_text="Hour of Day", row=num_components, col=1)
# fig2.update_yaxes(title_text="Relative Pattern")

# fig2.show()
