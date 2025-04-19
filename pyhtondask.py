import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Load the dataset
df = pd.read_csv('mobile_phones_2000.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Mobile Phone Sales Dashboard"),

    # Overall Sales Trends
    html.H2("Overall Sales Trends"),
    dcc.Graph(id='price-distribution'),

    # Brand Performance
    html.H2("Brand Performance"),
    dcc.Graph(id='brand-performance'),

    # Feature Relationships
    html.H2("Feature Relationships"),
    dcc.Graph(id='feature-relationships'),

    # Controls (Filters)
    html.Label("Select a Brand:"),
    dcc.Dropdown(
        id='brand-filter',
        options=[{'label': brand, 'value': brand} for brand in df['Brand'].unique()],
        value=df['Brand'].unique()[0]
    ),
    html.Label("Select Price Category:"),
    dcc.Dropdown(
        id='price-category-filter',
        options=[
            {'label': 'Budget (< $300)', 'value': 'Budget'},
            {'label': 'Mid-range ($300 - $700)', 'value': 'Mid-range'},
            {'label': 'Premium (>$700)', 'value': 'Premium'}
        ],
        value='Budget'
    )
])

# Helper: Add a new column for price category
def categorize_price(price):
    if price < 300:
        return 'Budget'
    elif price <= 700:
        return 'Mid-range'
    else:
        return 'Premium'

df['Price Category'] = df['Price (USD)'].apply(categorize_price)

# Callback: Price distribution by price category
@app.callback(
    Output('price-distribution', 'figure'),
    Input('price-category-filter', 'value')
)
def update_price_distribution(selected_category):
    filtered_df = df[df['Price Category'] == selected_category]
    fig = px.histogram(filtered_df, x='Price (USD)', nbins=20, title='Phone Price Distribution')
    return fig

# Callback: Brand performance (rating vs price)
@app.callback(
    Output('brand-performance', 'figure'),
    Input('brand-filter', 'value')
)
def update_brand_performance(selected_brand):
    filtered_df = df[df['Brand'] == selected_brand]

    grouped = filtered_df.groupby('Model').agg({
        'Price (USD)': 'mean',
        'Rating': 'mean'
    }).reset_index()

    if grouped.empty:
        return px.scatter(title="No data available for this brand.")

    fig = px.scatter(grouped, x='Rating', y='Price (USD)',
                     hover_data=['Model'], title='Average Rating vs. Average Price')
    return fig

# Callback: Feature relationships
@app.callback(
    Output('feature-relationships', 'figure'),
    [Input('brand-filter', 'value'), Input('price-category-filter', 'value')]
)
def update_feature_relationships(selected_brand, selected_category):
    filtered_df = df[(df['Brand'] == selected_brand) & (df['Price Category'] == selected_category)]
    fig = px.scatter(filtered_df, x='Screen Size (inches)', y='Price (USD)', color='RAM (GB)',
                     hover_data=['Model'], title='Screen Size vs Price')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8051, use_reloader=False)
