import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def plot_candlestick(df: pd.DataFrame, title: str = "Price Chart") -> go.Figure:
    """
    Create candlestick chart

    Args:
        df: DataFrame with OHLC data (open, high, low, close)
        title: Chart title

    Returns:
        Plotly figure
    """
    try:
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC'
        )])

        fig.update_layout(
            title=title,
            template='plotly_dark',
            xaxis_title='Date',
            yaxis_title='Price',
            hovermode='x unified',
            height=400
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating candlestick chart: {e}")
        return go.Figure()


def plot_line_chart(df: pd.DataFrame, columns: list, title: str = "Price Chart") -> go.Figure:
    """
    Create line chart

    Args:
        df: DataFrame with data
        columns: List of column names to plot
        title: Chart title

    Returns:
        Plotly figure
    """
    try:
        fig = go.Figure()

        colors = ['#00d4ff', '#00e676', '#ffb300', '#ff4444', '#7c4dff']

        for i, col in enumerate(columns):
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode='lines',
                    name=col,
                    line=dict(color=colors[i % len(colors)], width=2)
                ))

        fig.update_layout(
            title=title,
            template='plotly_dark',
            xaxis_title='Date',
            yaxis_title='Price',
            hovermode='x unified',
            height=400
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating line chart: {e}")
        return go.Figure()


def plot_histogram(df: pd.DataFrame, column: str, title: str = "Volume") -> go.Figure:
    """
    Create histogram (for volume)

    Args:
        df: DataFrame with data
        column: Column name to plot
        title: Chart title

    Returns:
        Plotly figure
    """
    try:
        colors = df[column].apply(lambda x: '#00e676' if x > df[column].mean() else '#ff4444')

        fig = go.Figure(data=[go.Bar(
            x=df.index,
            y=df[column],
            marker_color=colors,
            name=column,
            showlegend=False
        )])

        fig.update_layout(
            title=title,
            template='plotly_dark',
            xaxis_title='Date',
            yaxis_title=column,
            hovermode='x unified',
            height=300
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating histogram: {e}")
        return go.Figure()


def plot_sentiment_gauge(sentiment_score: float, title: str = "Sentiment") -> go.Figure:
    """
    Create sentiment gauge chart

    Args:
        sentiment_score: Score from -1 to 1
        title: Chart title

    Returns:
        Plotly figure
    """
    try:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sentiment_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            gauge={
                'axis': {'range': [-100, 100]},
                'bar': {'color': '#00d4ff'},
                'steps': [
                    {'range': [-100, -33.33], 'color': 'rgba(255,68,68,0.3)'},
                    {'range': [-33.33, 33.33], 'color': 'rgba(255,179,0,0.3)'},
                    {'range': [33.33, 100], 'color': 'rgba(0,230,118,0.3)'}
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig.update_layout(
            template='plotly_dark',
            height=400
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating gauge: {e}")
        return go.Figure()


def plot_distribution(df: pd.DataFrame, column: str, title: str = "Distribution") -> go.Figure:
    """
    Create distribution chart

    Args:
        df: DataFrame with data
        column: Column to plot distribution
        title: Chart title

    Returns:
        Plotly figure
    """
    try:
        fig = px.histogram(
            x=df[column],
            nbins=30,
            title=title,
            template='plotly_dark',
            color_discrete_sequence=['#00d4ff']
        )

        fig.update_layout(
            xaxis_title=column,
            yaxis_title='Frequency',
            height=400,
            hovermode='x unified'
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating distribution chart: {e}")
        return go.Figure()


def plot_correlation_heatmap(df: pd.DataFrame, title: str = "Correlation Matrix") -> go.Figure:
    """
    Create correlation heatmap

    Args:
        df: DataFrame with numeric data
        title: Chart title

    Returns:
        Plotly figure
    """
    try:
        corr = df.corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale='RdBu',
            zmid=0
        ))

        fig.update_layout(
            title=title,
            template='plotly_dark',
            height=500,
            width=600
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating heatmap: {e}")
        return go.Figure()


def plot_comparison_bars(data: dict, title: str = "Comparison") -> go.Figure:
    """
    Create comparison bar chart

    Args:
        data: Dictionary with labels as keys and values
        title: Chart title

    Returns:
        Plotly figure
    """
    try:
        fig = go.Figure(data=[go.Bar(
            x=list(data.keys()),
            y=list(data.values()),
            marker_color='#00d4ff'
        )])

        fig.update_layout(
            title=title,
            template='plotly_dark',
            xaxis_title='Category',
            yaxis_title='Value',
            height=400,
            hovermode='x unified'
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating bar chart: {e}")
        return go.Figure()
