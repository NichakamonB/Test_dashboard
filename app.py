import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from lightweight_charts.widgets import StreamlitChart
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# 🎨 ENHANCED UI CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(layout="wide", page_title="📊 Kwan test", page_icon="📈")

# 🎨 MODERN CSS STYLING (unchanged, keeping your excellent design)
st.markdown("""
    <style>
        .block-container {
            padding: 1rem 2rem 0.5rem 2rem !important;
            max-width: 100% !important;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
            width: 320px !important;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            transition: all 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
        }
        div[data-testid="stMetric"] label {
            font-size: 14px !important;
            font-weight: 600 !important;
            color: #94a3b8 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 32px !important;
            font-weight: 700 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4) !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.6) !important;
        }
        
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border-radius: 10px;
            border: 1px solid rgba(102, 126, 234, 0.2);
            font-weight: 600;
            padding: 8px 12px;
            font-size: 0.9em;
        }
        
        .stSelectbox > div > div {
            background: rgba(255,255,255,0.05) !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            padding: 6px 10px !important;
            font-size: 0.9em !important;
        }
        
        iframe {
            width: 100% !important;
            border-radius: 15px !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2) !important;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            margin: 5px 0;
        }
        .badge-bull {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }
        .badge-bear {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }
        
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        }
        .animated-bg::before {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 50%);
            animation: pulse 15s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: translate(-50%, -50%) scale(1); }
            50% { transform: translate(-50%, -50%) scale(1.1); }
        }
        
        /* Error Message Styling */
        .stAlert {
            border-radius: 10px;
        }
    </style>
    <div class="animated-bg"></div>
    """, unsafe_allow_html=True)

# Auto-refresh every 2 minutes
st_autorefresh(interval=120000, key="dashboard_refresh")

# ═══════════════════════════════════════════════════════════════
# 💾 SYSTEM STATE
# ═══════════════════════════════════════════════════════════════
if 'lang' not in st.session_state: 
    st.session_state.lang = 'TH'
if 'selected_stock' not in st.session_state: 
    st.session_state.selected_stock = "AAPL"
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

def t(th, en): 
    return th if st.session_state.lang == 'TH' else en

ASSET_GROUPS = {
    "🇺🇸 US MARKET": {
        "AAPL": "🍎 Apple", "TSLA": "🚗 Tesla", "NVDA": "🎮 Nvidia", 
        "MSFT": "💻 Microsoft", "GOOGL": "🔍 Google", "AMZN": "📦 Amazon"
    },
    "🇹🇭 THAI MARKET": {
        "CPALL.BK": "🛒 CP All", "PTT.BK": "⛽ PTT", "AOT.BK": "✈️ AOT",
        "KBANK.BK": "🏦 Kasikorn", "DELTA.BK": "🔌 Delta", "SCB.BK": "🏦 SCB"
    },
    "🪙 CRYPTO": {
        "BTC-USD": "₿ Bitcoin", "ETH-USD": "💎 Ethereum", 
        "BNB-USD": "🔶 Binance", "SOL-USD": "☀️ Solana"
    },
    "📈 INDICES": {
        "^SET.BK": "🇹🇭 SET Index", "^GSPC": "🇺🇸 S&P 500", 
        "^IXIC": "🇺🇸 Nasdaq", "^DJI": "🇺🇸 Dow Jones"
    }
}
ALL_SYMBOLS = [s for sub in ASSET_GROUPS.values() for s in sub]

# ═══════════════════════════════════════════════════════════════
# 📊 DATA ENGINE - IMPROVED ERROR HANDLING
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=110)
def get_pro_data(symbol, timeframe):
    """
    Fetch and process market data with comprehensive error handling
    
    Improvements:
    - Better error handling with specific error messages
    - Data validation
    - Safer timezone handling
    - Division by zero protection for RSI calculation
    """
    tf_map = {'5min': '5m', '15min': '15m', '1hour': '1h', '1day': '1d'}
    interval = tf_map.get(timeframe, '1d')
    
    period_map = {'5min': '5d', '15min': '5d', '1hour': '1mo', '1day': '6mo'}
    period = period_map.get(timeframe, '6mo')
    
    try:
        # Download data
        df = yf.download(symbol, interval=interval, period=period, progress=False, auto_adjust=False)
        
        # Validate data
        if df.empty:
            st.warning(f"⚠️ No data available for {symbol}")
            return pd.DataFrame()
        
        # Handle MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        df.columns = df.columns.str.lower()
        
        # Timezone handling
        if isinstance(df.index, pd.DatetimeIndex):
            if df.index.tz is None:
                df.index = df.index.tz_localize('UTC')
            df.index = df.index.tz_convert('Asia/Bangkok')
        
        # Reset index
        df = df.reset_index()
        df.rename(columns={'Datetime': 'time', 'Date': 'time'}, inplace=True)
        df['time'] = df['time'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        
        # === TECHNICAL INDICATORS ===
        
        # EMAs
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # Bollinger Bands
        df['sma20'] = df['close'].rolling(window=20).mean()
        df['std20'] = df['close'].rolling(window=20).std()
        df['bb_up'] = df['sma20'] + (df['std20'] * 2)
        df['bb_low'] = df['sma20'] - (df['std20'] * 2)
        
        # RSI - with division by zero protection
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        # Avoid division by zero
        rs = gain / loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi'].fillna(50, inplace=True)  # Fill NaN with neutral 50
        
        # MACD
        df['macd_line'] = df['close'].ewm(span=12, adjust=False).mean() - df['close'].ewm(span=26, adjust=False).mean()
        df['macd_signal'] = df['macd_line'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd_line'] - df['macd_signal']
        
        # Support/Resistance
        df['res'] = df['high'].rolling(window=20).max()
        df['sup'] = df['low'].rolling(window=20).min()
        
        # Trading signals
        df['signal'] = 0
        df.loc[df['close'] > df['res'].shift(1), 'signal'] = 1
        df.loc[df['close'] < df['sup'].shift(1), 'signal'] = -1
        
        # Strategy returns
        df['cum_ret'] = (1 + (df['signal'].shift(1) * df['close'].pct_change()).fillna(0)).cumprod() - 1
        
        # Update last update time
        st.session_state.last_update = datetime.now()
        
        return df.dropna().tail(300)
        
    except Exception as e:
        st.error(f"❌ Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

# ═══════════════════════════════════════════════════════════════
# 📊 CHART RENDERING FUNCTIONS
# ═══════════════════════════════════════════════════════════════
def render_main_chart(chart_obj, data):
    """Render main price chart with price-related indicators"""
    try:
        chart_obj.legend(visible=True, font_size=12, font_family='SF Pro Display, Segoe UI, sans-serif')
        chart_obj.set(data)
        
        if show_vol:
            v = chart_obj.create_histogram(name='Volume', color='rgba(102, 126, 234, 0.3)')
            v.set(data[['time', 'volume']].rename(columns={'volume': 'Volume'}))
        
        if show_bb:
            chart_obj.create_line(name='BB Upper', color='rgba(147, 197, 253, 0.6)').set(
                data[['time', 'bb_up']].rename(columns={'bb_up': 'BB Upper'}))
            chart_obj.create_line(name='BB Lower', color='rgba(147, 197, 253, 0.6)').set(
                data[['time', 'bb_low']].rename(columns={'bb_low': 'BB Lower'}))
        
        if show_ema50:
            chart_obj.create_line(name='EMA 50', color='#fbbf24', width=2).set(
                data[['time', 'ema50']].rename(columns={'ema50': 'EMA 50'}))
        
        if show_ema200:
            chart_obj.create_line(name='EMA 200', color='#a855f7', width=2).set(
                data[['time', 'ema200']].rename(columns={'ema200': 'EMA 200'}))
    except Exception as e:
        st.error(f"Chart rendering error: {str(e)}")

def render_full_chart(chart_obj, data):
    """Render simplified chart for grid view"""
    try:
        chart_obj.legend(visible=True, font_size=11, font_family='SF Pro Display, Segoe UI, sans-serif')
        chart_obj.set(data)
        
        if show_vol:
            v = chart_obj.create_histogram(name='Volume', color='rgba(102, 126, 234, 0.3)')
            v.set(data[['time', 'volume']].rename(columns={'volume': 'Volume'}))
        
        if show_ema50:
            chart_obj.create_line(name='EMA 50', color='#fbbf24', width=2).set(
                data[['time', 'ema50']].rename(columns={'ema50': 'EMA 50'}))
        
        if show_ema200:
            chart_obj.create_line(name='EMA 200', color='#a855f7', width=2).set(
                data[['time', 'ema200']].rename(columns={'ema200': 'EMA 200'}))
    except Exception as e:
        st.error(f"Grid chart error: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# 🎨 SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='font-size: 2.5em; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                📊 Kwan test
            </h1>
            <p style='color: #94a3b8; font-size: 0.9em; margin-top: 5px;'>Advanced Technical Analysis</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Language Toggle
    col1, col2 = st.columns(2)
    if col1.button("🇹🇭 ไทย", use_container_width=True): 
        st.session_state.lang = 'TH'
        st.rerun()
    if col2.button("🇺🇸 EN", use_container_width=True): 
        st.session_state.lang = 'EN'
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mode Selection
    st.markdown(f"### {t('⚙️ โหมดการทำงาน', '⚙️ Display Mode')}")
    page = st.radio(
        "",
        [t("🔍 วิเคราะห์รายตัว", "🔍 Single Asset"), 
         t("📊 กระดาน 4 จอ", "📊 Multi-View Grid")],
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Timeframe
    st.markdown(f"### {t('⏰ ช่วงเวลา', '⏰ Timeframe')}")
    timeframe = st.selectbox("", ['5min', '15min', '1hour', '1day'], index=0, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Indicators
    st.markdown(f"### {t('📈 ตัวชี้วัด', '📈 Indicators')}")
    with st.container():
        show_vol = st.checkbox(t("📊 Volume", "📊 Volume"), value=True)
        show_ema50 = st.checkbox("📉 EMA 50", value=True)
        show_ema200 = st.checkbox("📈 EMA 200", value=True)
        show_bb = st.checkbox("🎯 Bollinger Bands", value=False)
        show_rsi = st.checkbox("⚡ RSI", value=False)
        show_macd = st.checkbox("🌊 MACD", value=False)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Asset Selection
    st.markdown(f"### {t('🎯 เลือกสินทรัพย์', '🎯 Select Asset')}")
    for cat, items in ASSET_GROUPS.items():
        with st.expander(cat, expanded=(cat == "🇺🇸 US MARKET")):
            for sym, name in items.items():
                if st.button(name, key=f"s_{sym}", use_container_width=True):
                    st.session_state.selected_stock = sym
                    st.rerun()
    
    # Last update info
    if st.session_state.last_update:
        st.markdown(f"""
            <div style='text-align: center; color: #64748b; font-size: 0.75em; padding: 10px; margin-top: 20px;'>
                <p>🕐 {t('อัปเดตล่าสุด', 'Last Update')}:<br>{st.session_state.last_update.strftime('%H:%M:%S')}</p>
            </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 🎯 MAIN CONTENT - SINGLE VIEW
# ═══════════════════════════════════════════════════════════════
if page == t("🔍 วิเคราะห์รายตัว", "🔍 Single Asset"):
    symbol = st.session_state.selected_stock
    df = get_pro_data(symbol, timeframe)
    
    if not df.empty:
        # Header
        col1, col2 = st.columns([8, 2])
        with col1:
            st.markdown(f"""
                <h1 style='margin: 0; font-size: 2.5em;'>
                    📊 {symbol} 
                    <span style='font-size: 0.5em; color: #94a3b8;'>({timeframe})</span>
                </h1>
            """, unsafe_allow_html=True)
        with col2:
            if st.button(f"🔄 {t('รีเฟรช', 'Refresh')}", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Metrics Dashboard
        curr = df['close'].iloc[-1]
        prev = df['close'].iloc[-2] if len(df) > 1 else curr
        change = curr - prev
        change_pct = (change / prev) * 100 if prev != 0 else 0
        
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.metric(
                t("💰 ราคาปัจจุบัน", "💰 Current Price"),
                f"${curr:,.2f}" if not symbol.endswith('.BK') else f"฿{curr:,.2f}",
                f"{change:+,.2f} ({change_pct:+.2f}%)"
            )
        
        with m2:
            res_val = df['res'].iloc[-1]
            st.metric(
                t("📈 แนวต้าน", "📈 Resistance"),
                f"${res_val:,.2f}" if not symbol.endswith('.BK') else f"฿{res_val:,.2f}",
                f"{((res_val - curr) / curr * 100):+.2f}%"
            )
        
        with m3:
            sup_val = df['sup'].iloc[-1]
            st.metric(
                t("📉 แนวรับ", "📉 Support"),
                f"${sup_val:,.2f}" if not symbol.endswith('.BK') else f"฿{sup_val:,.2f}",
                f"{((curr - sup_val) / curr * 100):+.2f}%"
            )
        
        with m4:
            strategy_profit = df['cum_ret'].iloc[-1] * 100
            st.metric(
                t("🎯 กำไรกลยุทธ์", "🎯 Strategy P/L"),
                f"{strategy_profit:+.2f}%",
                t("แบ็คเทสต์", "Backtest")
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Main Chart
        chart = StreamlitChart(height=550)
        render_main_chart(chart, df)
        chart.load()
        
        # RSI Chart
        if show_rsi:
            st.markdown("<br>", unsafe_allow_html=True)
            col_rsi1, col_rsi2 = st.columns([1, 20])
            with col_rsi1:
                st.markdown("### ⚡")
            with col_rsi2:
                rsi_chart = StreamlitChart(height=180)
                rsi_chart.legend(visible=True, font_size=11)
                
                rsi_line = rsi_chart.create_line(name='RSI', color='#8b5cf6', width=2)
                rsi_line.set(df[['time', 'rsi']].rename(columns={'rsi': 'RSI'}))
                
                df_temp = df.copy()
                df_temp['rsi_70'] = 70
                df_temp['rsi_30'] = 30
                df_temp['rsi_50'] = 50
                
                rsi_chart.create_line(name='', color='rgba(239, 68, 68, 0.3)', width=1).set(
                    df_temp[['time', 'rsi_70']].rename(columns={'rsi_70': '70'}))
                rsi_chart.create_line(name='', color='rgba(34, 197, 94, 0.3)', width=1).set(
                    df_temp[['time', 'rsi_30']].rename(columns={'rsi_30': '30'}))
                rsi_chart.create_line(name='', color='rgba(148, 163, 184, 0.2)', width=1).set(
                    df_temp[['time', 'rsi_50']].rename(columns={'rsi_50': '50'}))
                
                rsi_chart.load()
        
        # MACD Chart
        if show_macd:
            st.markdown("<br>", unsafe_allow_html=True)
            col_macd1, col_macd2 = st.columns([1, 20])
            with col_macd1:
                st.markdown("### 🌊")
            with col_macd2:
                macd_chart = StreamlitChart(height=180)
                macd_chart.legend(visible=True, font_size=11)
                
                macd_hist = macd_chart.create_histogram(name='Histogram', color='rgba(102, 126, 234, 0.4)')
                macd_hist.set(df[['time', 'macd_hist']].rename(columns={'macd_hist': 'Histogram'}))
                
                macd_line = macd_chart.create_line(name='MACD', color='#3b82f6', width=2)
                macd_line.set(df[['time', 'macd_line']].rename(columns={'macd_line': 'MACD'}))
                
                signal_line = macd_chart.create_line(name='Signal', color='#f59e0b', width=2)
                signal_line.set(df[['time', 'macd_signal']].rename(columns={'macd_signal': 'Signal'}))
                
                df_temp = df.copy()
                df_temp['zero'] = 0
                macd_chart.create_line(name='', color='rgba(148, 163, 184, 0.3)', width=1).set(
                    df_temp[['time', 'zero']].rename(columns={'zero': '0'}))
                
                macd_chart.load()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Signal Analysis
        with st.expander(t("🔍 วิเคราะห์สัญญาณ", "🔍 Signal Analysis"), expanded=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                last_sig = df['signal'].iloc[-1]
                trend = "BULL" if curr > df['ema200'].iloc[-1] else "BEAR"
                
                st.markdown(f"""
                    <div style='text-align: center; padding: 20px;'>
                        <h3>{t('📊 เทรนด์ตลาด', '📊 Market Trend')}</h3>
                        <div class='status-badge {"badge-bull" if trend=="BULL" else "badge-bear"}'>
                            {'🟢 BULLISH' if trend=='BULL' else '🔴 BEARISH'}
                        </div>
                        <br><br>
                        <h3>{t('⚡ สัญญาณ', '⚡ Signal')}</h3>
                """, unsafe_allow_html=True)
                
                if last_sig == 1:
                    st.success(f"✅ {t('ซื้อ (Breakout)', 'BUY (Breakout)')}")
                elif last_sig == -1:
                    st.error(f"❌ {t('ขาย (Breakdown)', 'SELL (Breakdown)')}")
                else:
                    st.info(f"⌛ {t('รอสัญญาณ', 'HOLD/WAIT')}")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"#### {t('📋 ประวัติสัญญาณล่าสุด', '📋 Recent Signals')}")
                signal_df = df[df['signal'] != 0][['time', 'close', 'signal']].tail(5).copy()
                if not signal_df.empty:
                    signal_df['signal'] = signal_df['signal'].map({1: '✅ BUY', -1: '❌ SELL'})
                    signal_df.columns = [t('เวลา', 'Time'), t('ราคา', 'Price'), t('สัญญาณ', 'Signal')]
                    st.dataframe(signal_df, use_container_width=True, hide_index=True)
                else:
                    st.info(t("ไม่มีสัญญาณในช่วงเวลานี้", "No signals in this period"))
        
        # Technical Stats
        with st.expander(t("📊 สถิติทางเทคนิค", "📊 Technical Statistics")):
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            
            with stat_col1:
                st.metric("RSI (14)", f"{df['rsi'].iloc[-1]:.2f}")
                st.metric("MACD", f"{df['macd_line'].iloc[-1]:.4f}")
            
            with stat_col2:
                st.metric(t("ความผันผวน (20)", "Volatility (20)"), f"{df['std20'].iloc[-1]:.2f}")
                st.metric(t("ช่วงราคา (H-L)", "Range (H-L)"), f"{df['high'].iloc[-1] - df['low'].iloc[-1]:.2f}")
            
            with stat_col3:
                st.metric(t("ปริมาณเฉลี่ย", "Avg Volume"), f"{df['volume'].tail(20).mean():,.0f}")
                st.metric(t("ปริมาณล่าสุด", "Last Volume"), f"{df['volume'].iloc[-1]:,.0f}")
    else:
        st.error(f"❌ {t('ไม่สามารถโหลดข้อมูลสำหรับ', 'Unable to load data for')} {symbol}")

# ═══════════════════════════════════════════════════════════════
# 📊 MULTI-VIEW GRID
# ═══════════════════════════════════════════════════════════════
else:
    # Compact Header
    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown(f"""
            <h2 style='margin: 0; padding: 10px 0;'>
                📊 {t('กระดาน 4 จอ', 'Multi-View Dashboard')}
            </h2>
        """, unsafe_allow_html=True)
    with col2:
        if st.button(f"🔄 {t('รีเซ็ต', 'Reset')}", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Grid Layout - 2x2
    row1_cols = st.columns(2)
    row2_cols = st.columns(2)
    
    all_cols = [row1_cols[0], row1_cols[1], row2_cols[0], row2_cols[1]]
    
    for i in range(4):
        with all_cols[i]:
            # Compact Symbol Selector
            sel = st.selectbox(
                "", 
                ALL_SYMBOLS, 
                index=min(i, len(ALL_SYMBOLS)-1), 
                key=f"grid_sel_{i}",
                label_visibility="collapsed"
            )
            
            d = get_pro_data(sel, timeframe)
            
            if not d.empty:
                curr_price = d['close'].iloc[-1]
                prev_price = d['close'].iloc[-2] if len(d) > 1 else curr_price
                change = ((curr_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
                
                # Compact Price Display
                st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.05); padding: 8px 12px; border-radius: 8px; margin-bottom: 8px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span style='font-weight: 600; font-size: 0.95em;'>{sel}</span>
                            <span style='font-size: 1.1em; font-weight: 700; color: {"#10b981" if change >= 0 else "#ef4444"};'>
                                ${curr_price:,.2f} <span style='font-size: 0.75em;'>({change:+.2f}%)</span>
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Smaller Chart
                c = StreamlitChart(height=320)
                render_full_chart(c, d)
                c.load()
            else:
                st.warning(f"⚠️ {t('ไม่สามารถโหลด', 'Cannot load')} {sel}")

# ═══════════════════════════════════════════════════════════════
# 🔗 FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='text-align: center; padding: 30px; background: rgba(255,255,255,0.02); border-radius: 15px; border: 1px solid rgba(255,255,255,0.05);'>
        <p style='font-size: 1.1em; margin-bottom: 10px;'>
            📊 {t('ข้อมูลจาก', 'Data Source')}: 
            <a href="https://finance.yahoo.com/quote/{st.session_state.selected_stock}" 
               target="_blank" 
               style="color: #667eea; text-decoration: none; font-weight: 600;">
                Yahoo Finance (Official API)
            </a>
        </p>
        <p style='font-size: 0.85em; color: #64748b; margin: 0;'>
            ⚠️ {t('ข้อมูลนี้ใช้เพื่อการศึกษาและวิเคราะห์เท่านั้น ไม่ใช่คำแนะนำการลงทุน', 
                  'This information is for educational purposes only. Not financial advice.')}
        </p>
        <p style='font-size: 0.75em; color: #475569; margin-top: 10px;'>
            🔐 {t('ปลอดภัย | อัปเดตทุก 2 นาที | เทคโนโลยีล้ำสมัย', 'Secure | Auto-refresh every 2 min | Advanced Technology')}
        </p>
    </div>
""", unsafe_allow_html=True)

