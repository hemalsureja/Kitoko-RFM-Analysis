import os
import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore
from plotly.subplots import make_subplots # type: ignore
import logging
import warnings
from statsmodels.tsa.arima.model import ARIMA # type: ignore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KitokoVisualizer:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.campaign_file = os.path.join(self.data_dir, 'kitoko project files', 'Kitoko_Campaign_Data.xlsx')
        self.order_details_file = os.path.join(self.data_dir, 'kitoko project files', 'Kitoko order details.xlsx')
        self.output_html = os.path.join(self.data_dir, 'kitoko project files', 'kitoko_dashboard.html')

    def generate_dashboard(self):
        logging.info("Starting dashboard generation...")
        
        # Dashboard Data
        total_revenue = 0
        total_spend = 0
        total_orders = 0
        overall_roas = 0
        overall_acos = 0
        overall_ctr = 0
        overall_cvr = 0
        figs = []

        # Default layout for transparent, premium bento mode
        layout_defaults = dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#334155', family='Inter, sans-serif'),
            margin=dict(l=40, r=40, t=60, b=40),
            hovermode="x unified"
        )
        axes_defaults = dict(
            gridcolor='rgba(0,0,0,0.05)',
            zerolinecolor='rgba(0,0,0,0.1)'
        )

        # 1. Campaign Data Visuals & KPIs
        try:
            if os.path.exists(self.campaign_file):
                campaign_df = pd.read_excel(self.campaign_file)
                campaign_df['Report Date'] = pd.to_datetime(campaign_df['Report Date'], format='mixed', dayfirst=True)
                
                # Daily aggregation
                daily_campaign = campaign_df.groupby('Report Date').agg(
                    Total_Spend=('Spend(INR)', 'sum'),
                    Total_Sales=('Sales(INR)', 'sum'),
                    Total_Orders=('Orders', 'sum'),
                    Total_Clicks=('Clicks', 'sum'),
                    Total_Impressions=('Impressions', 'sum')
                ).reset_index().sort_values('Report Date')

                daily_campaign['ROAS'] = daily_campaign['Total_Sales'] / daily_campaign['Total_Spend'].replace(0, 1)
                daily_campaign['ACOS'] = (daily_campaign['Total_Spend'] / daily_campaign['Total_Sales'].replace(0, 1)) * 100

                # KPIs
                total_revenue = daily_campaign['Total_Sales'].sum()
                total_spend = daily_campaign['Total_Spend'].sum()
                total_orders = daily_campaign['Total_Orders'].sum()
                total_clicks = daily_campaign['Total_Clicks'].sum()
                total_impressions = daily_campaign['Total_Impressions'].sum()
                
                overall_roas = total_revenue / total_spend if total_spend > 0 else 0
                overall_acos = (total_spend / total_revenue) * 100 if total_revenue > 0 else 0
                overall_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
                overall_cvr = (total_orders / total_clicks) * 100 if total_clicks > 0 else 0

                # Figure 1: Marketing Funnel
                funnel_fig = go.Figure(go.Funnel(
                    y=["Impressions", "Clicks", "Orders"],
                    x=[total_impressions, total_clicks, total_orders],
                    textinfo="value+percent initial",
                    marker=dict(color=["#3b82f6", "#8b5cf6", "#10b981"])
                ))
                funnel_fig.update_layout(**layout_defaults, title="Marketing Conversion Funnel", title_font=dict(size=20, color='#1e293b'))
                figs.append({'html': funnel_fig.to_html(full_html=False, include_plotlyjs=False), 'class': 'col-span-1'})

                # Figure 2: ACOS vs ROAS Trend (Dual Axis)
                fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
                fig_dual.add_trace(
                    go.Scatter(x=daily_campaign['Report Date'], y=daily_campaign['ACOS'], name="ACOS %",
                               line=dict(color='#ef4444', width=3)),
                    secondary_y=False,
                )
                fig_dual.add_trace(
                    go.Scatter(x=daily_campaign['Report Date'], y=daily_campaign['ROAS'], name="ROAS",
                               line=dict(color='#10b981', width=3)),
                    secondary_y=True,
                )
                fig_dual.update_layout(**layout_defaults, title="ACOS vs ROAS Efficiency", title_font=dict(size=20, color='#1e293b'))
                fig_dual.update_xaxes(**axes_defaults, showgrid=False)
                fig_dual.update_yaxes(title_text="ACOS (%)", secondary_y=False, **axes_defaults)
                fig_dual.update_yaxes(title_text="ROAS (x)", secondary_y=True, showgrid=False)
                figs.append({'html': fig_dual.to_html(full_html=False, include_plotlyjs=False), 'class': 'col-span-2'})

                # Figure 3: Sales vs Spend over time
                fig1 = go.Figure()
                fig1.add_trace(go.Scatter(x=daily_campaign['Report Date'], y=daily_campaign['Total_Sales'], 
                                          mode='lines', name='Sales', fill='tozeroy',
                                          line=dict(color='#06b6d4', width=3), fillcolor='rgba(6, 182, 212, 0.1)'))
                fig1.add_trace(go.Scatter(x=daily_campaign['Report Date'], y=daily_campaign['Total_Spend'], 
                                          mode='lines', name='Ad Spend', fill='tozeroy',
                                          line=dict(color='#f43f5e', width=3), fillcolor='rgba(244, 63, 94, 0.1)'))
                fig1.update_layout(**layout_defaults, title="Revenue & Ad Spend Trends", title_font=dict(size=20, color='#1e293b'))
                fig1.update_xaxes(**axes_defaults, showgrid=False)
                fig1.update_yaxes(**axes_defaults)
                figs.append({'html': fig1.to_html(full_html=False, include_plotlyjs=False), 'class': 'col-span-2'})

                # Figure 4: Revenue Forecasting (ARIMA)
                try:
                    warnings.filterwarnings('ignore')
                    
                    hist_sales = daily_campaign['Total_Sales'].values
                    # Fit a simple ARIMA(1, 1, 1) model
                    model = ARIMA(hist_sales, order=(1, 1, 1))
                    model_fit = model.fit()
                    
                    forecast_steps = 14
                    forecast_values = model_fit.forecast(steps=forecast_steps)
                    
                    # Generate future dates
                    last_date = daily_campaign['Report Date'].iloc[-1]
                    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_steps)
                    
                    fig_fcst = go.Figure()
                    fig_fcst.add_trace(go.Scatter(x=daily_campaign['Report Date'], y=daily_campaign['Total_Sales'], 
                                              mode='lines', name='Historical Sales',
                                              line=dict(color='#06b6d4', width=3, shape='spline')))
                    fig_fcst.add_trace(go.Scatter(x=future_dates, y=forecast_values, 
                                              mode='lines', name='14-Day Forecast',
                                              line=dict(color='#8b5cf6', width=3, dash='dash', shape='spline')))
                    
                    fig_fcst.update_layout(**layout_defaults, title=dict(text="Revenue Forecast (14 Days)", x=0.5, font=dict(size=18, color='#1e293b')))
                    fig_fcst.update_xaxes(**axes_defaults, showgrid=False)
                    fig_fcst.update_yaxes(**axes_defaults)
                    figs.append({'html': fig_fcst.to_html(full_html=False, include_plotlyjs=False), 'class': 'col-span-2'})
                except Exception as e:
                    logging.error(f"Error generating forecast: {e}")

            else:
                logging.warning(f"Campaign file not found: {self.campaign_file}")
        except Exception as e:
            logging.error(f"Error processing campaign data: {e}")

        # 2. Order Details Visuals
        try:
            if os.path.exists(self.order_details_file):
                # We need raw order details to get Top ASINs
                orders_df = pd.read_excel(self.order_details_file, sheet_name='Order Details')
                
                # Clean Data
                orders_df['item-price'] = pd.to_numeric(orders_df['item-price'], errors='coerce').fillna(0)
                orders_df['quantity'] = pd.to_numeric(orders_df.get('quantity', 1), errors='coerce').fillna(1).astype(int)
                orders_df['total_value'] = orders_df['item-price']
                
                # Top 10 ASINs by Revenue
                top_asins = orders_df.groupby('asin')['total_value'].sum().reset_index()
                top_asins = top_asins.sort_values('total_value', ascending=True).tail(10) # Ascending for horizontal bar
                
                fig_asin = px.bar(top_asins, x='total_value', y='asin', orientation='h', 
                                  title="Top 10 ASINs by Revenue", text_auto='.2s')
                fig_asin.update_traces(marker_color='#8b5cf6', textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                fig_asin.update_layout(**layout_defaults, title_font=dict(size=20, color='#1e293b'))
                fig_asin.update_layout(margin=dict(l=120, r=20, t=70, b=20))
                fig_asin.update_xaxes(**axes_defaults, showgrid=False, title="Total Revenue (INR)")
                fig_asin.update_yaxes(title="")
                figs.append({'html': fig_asin.to_html(full_html=False, include_plotlyjs=False), 'class': 'col-span-1'})

                # RFM Segment Distribution
                rfm_df = pd.read_excel(self.order_details_file, sheet_name='RFM_Scores_new')
                color_map = {'Top Performer': '#8b5cf6', 'Recent Favorite': '#3b82f6', 'High Value': '#10b981', 'Mid Performer': '#f59e0b', 'At Risk': '#ef4444'}
                segment_counts = rfm_df['Segment'].value_counts().reset_index()
                segment_counts.columns = ['Segment', 'Count']
                
                fig3 = px.pie(segment_counts, names='Segment', values='Count', title='Product Segmentation (RFM)', 
                              hole=0.6, color='Segment', color_discrete_map=color_map)
                fig3.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='white', width=2)))
                fig3.update_layout(**layout_defaults, title_font=dict(size=20, color='#1e293b'), showlegend=False)
                figs.append({'html': fig3.to_html(full_html=False, include_plotlyjs=False), 'class': 'col-span-1'})

            else:
                logging.warning(f"Order details file not found: {self.order_details_file}")
        except Exception as e:
            logging.error(f"Error processing Order Details data: {e}")

        # Format KPIs
        fmt_rev = f"₹{total_revenue/1000:.1f}K" if total_revenue > 1000 else f"₹{total_revenue:,.0f}"
        fmt_spend = f"₹{total_spend/1000:.1f}K" if total_spend > 1000 else f"₹{total_spend:,.0f}"
        fmt_acos = f"{overall_acos:.1f}%"
        fmt_cvr = f"{overall_cvr:.1f}%"

        # 3. Write HTML with Bento Box UI
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kitoko Performance Dashboard</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
            <style>
                :root {{
                    --bg-page: #f8fafc;
                    --bg-card: #ffffff;
                    --text-main: #0f172a;
                    --text-muted: #64748b;
                    --border-color: rgba(0, 0, 0, 0.05);
                    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
                    --shadow-hover: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                    --radius: 20px;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: var(--bg-page);
                    color: var(--text-main);
                    font-family: 'Inter', sans-serif;
                    min-height: 100vh;
                }}
                .dashboard-wrapper {{
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }}
                .header {{
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    font-size: 2.2rem;
                    font-weight: 700;
                    margin: 0 0 5px 0;
                    color: #0f172a;
                }}
                .header p {{
                    color: var(--text-muted);
                    margin: 0;
                    font-size: 1rem;
                }}
                
                /* KPI Grid: 4 columns */
                .kpi-grid {{
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                
                /* Chart Grid: 2 columns */
                .chart-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                }}

                .bento-card {{
                    background: var(--bg-card);
                    border-radius: var(--radius);
                    box-shadow: var(--shadow);
                    border: 1px solid var(--border-color);
                    padding: 24px;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }}
                .bento-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: var(--shadow-hover);
                }}
                
                .kpi-title {{
                    font-size: 0.85rem;
                    font-weight: 600;
                    color: var(--text-muted);
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 8px;
                    display: block;
                }}
                .kpi-value {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    line-height: 1;
                }}
                
                /* Column spans for charts */
                .col-span-1 {{ grid-column: span 1; }}
                .col-span-2 {{ grid-column: span 2; }}
                
                .chart-container {{
                    min-height: 350px;
                    width: 100%;
                    height: 100%;
                }}

                /* Colors */
                .text-blue {{ color: #3b82f6; }}
                .text-emerald {{ color: #10b981; }}
                .text-rose {{ color: #f43f5e; }}
                .text-purple {{ color: #8b5cf6; }}

                @media (max-width: 1024px) {{
                    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
                    .chart-grid {{ grid-template-columns: 1fr; }}
                    .col-span-1, .col-span-2 {{ grid-column: span 1; }}
                }}
                @media (max-width: 640px) {{
                    .kpi-grid {{ grid-template-columns: 1fr; }}
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-wrapper">
                <div class="header">
                    <h1>Kitoko Workspace Analytics</h1>
                    <p>Advertising & Sales Performance Overview</p>
                </div>
                
                <!-- KPI Section -->
                <div class="kpi-grid">
                    <div class="bento-card">
                        <span class="kpi-title">Total Revenue</span>
                        <span class="kpi-value text-blue">{fmt_rev}</span>
                    </div>
                    <div class="bento-card">
                        <span class="kpi-title">Total Ad Spend</span>
                        <span class="kpi-value text-rose">{fmt_spend}</span>
                    </div>
                    <div class="bento-card">
                        <span class="kpi-title">Aggregate ACOS</span>
                        <span class="kpi-value text-emerald">{fmt_acos}</span>
                    </div>
                    <div class="bento-card">
                        <span class="kpi-title">Conversion Rate</span>
                        <span class="kpi-value text-purple">{fmt_cvr}</span>
                    </div>
                </div>

                <!-- Charts Section -->
                <div class="chart-grid">
        """

        for fig_data in figs:
            html_content += f"""
                    <div class="bento-card {fig_data['class']}">
                        <div class="chart-container">
                            {fig_data['html']}
                        </div>
                    </div>
            """

        html_content += """
                </div>
            </div>
        </body>
        </html>
        """

        if figs:
            with open(self.output_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logging.info(f"Dashboard successfully generated at {self.output_html}")
            return self.output_html
        else:
            logging.error("No figures were generated.")
            return None

if __name__ == "__main__":
    # Dynamically resolve directory to make the project portable
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.dirname(SCRIPT_DIR)
    visualizer = KitokoVisualizer(DATA_DIR)
    visualizer.generate_dashboard()
