from primary.all_import import *
from primary.create_detailed_holdings_table import *
from primary.create_portfolio_dashboard import *
from primary.run_complete_analysis import *
from primary.zerodha_portfolio_analyser import PortfolioConfig,ZerodhaPortfolioAnalyzer
# from primary.run_complete_analysis import run_complete_analysis
# import primary.run_complete_analysis as rca
# from primary.streamlit import PortfolioConfig, StreamlitPortfolioAnalyzer


# Configure page
st.set_page_config(
    page_title="🚀 InvestGPT - Your AI-Powered Investment Companion",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': "https://github.com/your-repo/issues",
        'About': "# AI-Powered Portfolio Analyzer\nAnalyze your Zerodha portfolio with AI insights!"
    }
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e1e5eb;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .insight-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .voice-button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        border: none;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        cursor: pointer;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .voice-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stPlotlyChart {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .title-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = False

class VoiceAssistant:
    """Voice synthesis assistant"""
    
    def __init__(self):
        self.engine = None
        self.initialize_engine()
    
    def initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            # Set properties
            self.engine.setProperty('rate', 180)  # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume level
            
            # Try to set a better voice
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            st.error(f"Voice engine initialization failed: {e}")
            self.engine = None
    
    def speak(self, text: str):
        """Speak the given text"""
        if self.engine and st.session_state.voice_enabled:
            try:
                # Run in a separate thread to avoid blocking
                def speak_thread():
                    self.engine.say(text)
                    self.engine.runAndWait()
                
                thread = threading.Thread(target=speak_thread)
                thread.daemon = True
                thread.start()
            except Exception as e:
                st.error(f"Voice synthesis error: {e}")

class StreamlitPortfolioAnalyzer:
    """Streamlit-specific portfolio analyzer"""
    
    def __init__(self, config: PortfolioConfig):
        self.config = config
        self.kite = None
        self.gemini_model = None
        self.voice_assistant = VoiceAssistant()
        
        self.initialize_apis()
    
    def initialize_apis(self):
        """Initialize APIs with error handling"""
        try:
            # Initialize Zerodha
            self.kite = KiteConnect(api_key=self.config.zerodha_api_key)
            self.kite.set_access_token(self.config.zerodha_access_token)
            
            # Test connection
            profile = self.kite.profile()
            st.success(f"✅ Connected to Zerodha: {profile.get('user_name', 'Unknown')}")
            
            # Initialize Gemini
            genai.configure(api_key=self.config.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            st.success("✅ Gemini AI initialized successfully")
            
        except Exception as e:
            st.error(f"❌ API initialization failed: {str(e)}")
            return False
        
        return True
    
    def fetch_portfolio_data(self):
        """Fetch portfolio data with progress tracking"""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Fetch holdings
            status_text.text("📊 Fetching holdings...")
            progress_bar.progress(20)
            holdings = self.kite.holdings()
            
            # Fetch positions
            status_text.text("📈 Fetching positions...")
            progress_bar.progress(40)
            positions = self.kite.positions()
            
            # Fetch margins
            status_text.text("💰 Fetching margins...")
            progress_bar.progress(60)
            try:
                margins = self.kite.margins()
            except:
                margins = {'equity': {}, 'commodity': {}}
            
            # Fetch orders
            status_text.text("📋 Fetching recent orders...")
            progress_bar.progress(80)
            try:
                orders = self.kite.orders()
            except:
                orders = []
            
            progress_bar.progress(100)
            status_text.text("✅ Portfolio data fetched successfully!")
            
            portfolio_data = {
                'holdings': holdings,
                'day_positions': positions.get('day', []),
                'net_positions': positions.get('net', []),
                'equity_margin': margins.get('equity', {}),
                'commodity_margin': margins.get('commodity', {}),
                'orders': orders,
                'fetch_timestamp': datetime.now().isoformat()
            }
            
            time.sleep(1)  # Show success message
            progress_bar.empty()
            status_text.empty()
            
            return portfolio_data
            
        except Exception as e:
            st.error(f"❌ Error fetching portfolio data: {str(e)}")
            progress_bar.empty()
            status_text.empty()
            return None
    
    def analyze_with_gemini(self, portfolio_data):
        """Analyze portfolio with Gemini AI"""
        if not self.gemini_model:
            return "Gemini AI not initialized"
        
        # Prepare analysis prompt
        prompt = self.prepare_comprehensive_prompt(portfolio_data)
        
        with st.spinner("🤖 AI is analyzing your portfolio..."):
            try:
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=4000,
                    )
                )
                return response.text
            except Exception as e:
                return f"Analysis failed: {str(e)}"
    
    def prepare_comprehensive_prompt(self, data):
        """Prepare comprehensive analysis prompt"""
        # Calculate summary statistics
        holdings = data['holdings']
        total_investment = sum(h.get('average_price', 0) * h.get('quantity', 0) for h in holdings)
        current_value = sum(h.get('last_price', 0) * h.get('quantity', 0) for h in holdings)
        total_pnl = sum(h.get('pnl', 0) for h in holdings)
        
        prompt = f"""
        As an expert financial advisor, analyze this Indian stock portfolio and provide comprehensive insights:

        PORTFOLIO SUMMARY:
        - Total Investment: ₹{total_investment:,.2f}
        - Current Value: ₹{current_value:,.2f}
        - Total P&L: ₹{total_pnl:,.2f}
        - Return %: {(total_pnl/total_investment*100) if total_investment > 0 else 0:.2f}%
        - Holdings Count: {len(holdings)}

        HOLDINGS DATA:
        {json.dumps(holdings[:10], indent=2, default=str)}  # Limit data size

        Provide analysis in these sections:
        1. PERFORMANCE OVERVIEW - Overall portfolio health
        2. TOP PERFORMERS - Best performing stocks
        3. UNDERPERFORMERS - Stocks needing attention  
        4. RISK ANALYSIS - Concentration and diversification
        5. SECTOR INSIGHTS - Sector allocation and trends
        6. ACTIONABLE RECOMMENDATIONS - Specific next steps
        7. MARKET OUTLOOK - Current market context

        Keep insights practical, specific, and actionable for an Indian investor.
        """
        
        return prompt

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <h1 class="title-header">🚀 InvestGPT - Your AI-Powered Investment Companion - PromptopiaAI</h1>
    <p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
        Analyze your Zerodha portfolio with AI-powered insights and voice assistance
    </p>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Voice toggle
        voice_enabled = st.toggle("🔊 Voice Assistant", value=st.session_state.voice_enabled)
        st.session_state.voice_enabled = voice_enabled
        
        # API Configuration
        st.markdown("### 🔑 API Keys")
        
        zerodha_api_key = st.text_input(
            "Zerodha API Key", 
            value=os.getenv('ZERODHA_API_KEY', ''),
            type="password"
        )
        
        zerodha_access_token = st.text_input(
            "Zerodha Access Token", 
            value=os.getenv('ZERODHA_ACCESS_TOKEN', ''),
            type="password"
        )
        
        gemini_api_key = st.text_input(
            "Gemini API Key", 
            value=os.getenv('GEMINI_API_KEY', ''),
            type="password"
        )
        
        # Analysis settings
        st.markdown("### 📊 Analysis Settings")
        min_investment = st.number_input("Minimum Investment Amount (₹)", value=1000.0, step=500.0)
        include_zero_qty = st.checkbox("Include Zero Quantity Holdings", value=False)
        
        # Initialize analyzer button
        if st.button("🔄 Initialize Analyzer", type="primary"):
            if all([zerodha_api_key, zerodha_access_token, gemini_api_key]):
                config = PortfolioConfig(
                    zerodha_api_key=zerodha_api_key,
                    zerodha_access_token=zerodha_access_token,
                    gemini_api_key=gemini_api_key,
                    min_investment_amount=min_investment,
                    include_zero_quantity=include_zero_qty
                )
                
                try:
                    # Initialize analyzer
                    analyzer = ZerodhaPortfolioAnalyzer(config)
                    
                    # Run complete analysis
                    report = analyzer.run_complete_analysis()
                    
                    # Print summary
                    print("\n" + "="*60)
                    print("🎉 PORTFOLIO ANALYSIS COMPLETE!")
                    print("="*60)
                    
                    summary = report.get('portfolio_summary', {})
                    print(f"📊 Total Holdings: {summary.get('total_holdings', 0)}")
                    print(f"💰 Current Value: ₹{summary.get('current_value', 0):,.2f}")
                    print(f"📈 Total P&L: ₹{summary.get('total_pnl', 0):,.2f}")
                    
                    # Print Gemini analysis snippet
                    analysis = report.get('gemini_analysis', '')
                    if analysis:
                        print(f"\n🤖 Gemini Analysis Preview:")
                        print("-" * 40)
                        print(analysis[:500] + "..." if len(analysis) > 500 else analysis)
                    
                    print(f"\n📄 Full report saved to JSON file")
                    print("="*60)
                    
                except Exception as e:
                    logger.error(f"❌ Analysis failed: {str(e)}")
                    print(f"\n❌ Error: {str(e)}")
                    print("\nPlease check:")
                    print("1. Your API keys are correct")
                    print("2. Your Zerodha access token is valid and not expired")
                    print("3. You have active internet connection")
                    print("4. Your Gemini API key has sufficient quota")
                    print("5. Make sure your .env file is in the same directory as this script")

                
                
                analyzer = StreamlitPortfolioAnalyzer(config)
                st.session_state.analyzer = analyzer
                
                if voice_enabled:
                    analyzer.voice_assistant.speak("Portfolio analyzer initialized successfully!")
            else:
                st.error("Please provide all required API keys")
    
    # Main content area
    if 'analyzer' not in st.session_state:
        st.info("👈 Please configure your API keys in the sidebar and initialize the analyzer")
        return
    
    analyzer = st.session_state.analyzer
    
    # Fetch portfolio data
    if st.button("📊 Fetch Portfolio Data", type="primary"):
        portfolio_data = analyzer.fetch_portfolio_data()
        if portfolio_data:
            st.session_state.portfolio_data = portfolio_data
            if st.session_state.voice_enabled:
                analyzer.voice_assistant.speak("Portfolio data fetched successfully!")
    
    # Display portfolio dashboard
    if st.session_state.portfolio_data:
        portfolio_data = st.session_state.portfolio_data
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📋 Holdings", "🤖 AI Analysis", "📈 Advanced Charts"])
        
        with tab1:
            create_portfolio_dashboard(analyzer, portfolio_data)
        
        with tab2:
            create_detailed_holdings_table(portfolio_data)
        
        with tab3:
            st.subheader("🤖 AI-Powered Analysis")
            
            if st.button("🚀 Generate AI Analysis", type="primary"):
                # with st.spinner("🤖 AI is analyzing your portfolio..."):
                    analysis = analyzer.analyze_with_gemini(portfolio_data)
                    st.session_state.analysis_results = analysis
                    
                    if st.session_state.voice_enabled:
                        analyzer.voice_assistant.speak("AI analysis completed!")
            
            if st.session_state.analysis_results:
                st.markdown("""
                <div class="insight-card">
                    <h3>🎯 AI Insights & Recommendations</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(st.session_state.analysis_results)
                
                # Voice playback of analysis
                if st.session_state.voice_enabled:
                    if st.button("🔊 Listen to Analysis"):
                        # Get first few sentences for voice
                        sentences = st.session_state.analysis_results.split('.')[:5]
                        summary = '. '.join(sentences) + '.'
                        analyzer.voice_assistant.speak(summary)
            
                        
        
        with tab4:
            st.subheader("📈 Advanced Portfolio Analytics")
            
            df = pd.DataFrame(portfolio_data['holdings'])
            if not df.empty:
                df['current_value'] = df['last_price'] * df['quantity']
                df['return_pct'] = ((df['last_price'] - df['average_price']) / df['average_price'] * 100)
                
                # Scatter plot: Risk vs Return
                fig = px.scatter(
                    df, 
                    x='current_value', 
                    y='return_pct',
                    size='quantity',
                    color='pnl',
                    hover_data=['tradingsymbol'],
                    title="Portfolio Risk-Return Analysis",
                    labels={'current_value': 'Investment Value (₹)', 'return_pct': 'Return (%)'},
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Correlation matrix
                numeric_cols = ['quantity', 'average_price', 'last_price', 'pnl', 'current_value', 'return_pct']
                corr_matrix = df[numeric_cols].corr()
                
                fig = px.imshow(
                    corr_matrix,
                    title="Portfolio Metrics Correlation Matrix",
                    color_continuous_scale='RdBu'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🚀 AI Portfolio Analyzer | Built with Streamlit & Google Gemini</p>
        <p>💡 Tip: Enable voice assistant for a hands-free experience!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()