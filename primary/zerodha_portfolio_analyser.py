
from dataclasses import dataclass
from primary.all_import import *



@dataclass
class PortfolioConfig:
    """Configuration class for portfolio analysis"""
    zerodha_api_key: str
    zerodha_access_token: str
    gemini_api_key: str
    min_investment_amount: float = 1000.0
    include_zero_quantity: bool = False
    analysis_depth: str = "detailed"

class ZerodhaPortfolioAnalyzer:
    """Main class for fetching Zerodha portfolio and analyzing with Gemini"""
    
    def __init__(self, config: PortfolioConfig):
        self.config = config
        self.kite = None
        self.portfolio_data = {}
        self.analysis_results = {}
        
        # Initialize Zerodha KiteConnect
        try:
            self.kite = KiteConnect(api_key=config.zerodha_api_key)
            self.kite.set_access_token(config.zerodha_access_token)
            logger.info("✅ Zerodha KiteConnect initialized successfully")
            
            # Test the connection
            try:
                profile = self.kite.profile()
                logger.info(f"✅ Connected to Zerodha account: {profile.get('user_name', 'Unknown')}")
            except Exception as e:
                logger.error(f"❌ Failed to fetch profile - Token might be invalid: {str(e)}")
                raise Exception(f"Invalid access token or API key. Error: {str(e)}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize KiteConnect: {str(e)}")
            raise
        
        # Initialize Gemini
        try:
            genai.configure(api_key=config.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✅ Google Gemini Flash initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
            raise

    def fetch_portfolio_data(self) -> Dict[str, Any]:
        """Fetch comprehensive portfolio data from Zerodha"""
        try:
            logger.info("📊 Fetching portfolio data from Zerodha...")
            
            # Fetch holdings
            holdings = self.kite.holdings()
            logger.info(f"✅ Fetched {len(holdings)} holdings")
            
            # Fetch positions
            positions = self.kite.positions()
            day_positions = positions.get('day', [])
            net_positions = positions.get('net', [])
            logger.info(f"✅ Fetched {len(day_positions)} day positions, {len(net_positions)} net positions")
            
            # Fetch funds/margins
            try:
                margins = self.kite.margins()
                equity_margin = margins.get('equity', {})
                commodity_margin = margins.get('commodity', {})
                logger.info("✅ Fetched margin data")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch margins: {str(e)}")
                equity_margin = commodity_margin = {}
            
            # Fetch orders (recent orders)
            try:
                orders = self.kite.orders()
                logger.info(f"✅ Fetched {len(orders)} orders")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch orders: {str(e)}")
                orders = []
            
            # Store portfolio data
            self.portfolio_data = {
                'holdings': holdings,
                'day_positions': day_positions,
                'net_positions': net_positions,
                'equity_margin': equity_margin,
                'commodity_margin': commodity_margin,
                'orders': orders,
                'fetch_timestamp': datetime.now().isoformat()
            }
            
            logger.info("✅ Portfolio data fetched successfully")
            return self.portfolio_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching portfolio data: {str(e)}")
            raise

    def apply_filters(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply filters to portfolio data based on configuration"""
        try:
            logger.info("🔍 Applying filters to portfolio data...")
            filtered_data = data.copy()
            
            # Filter holdings
            original_holdings_count = len(filtered_data['holdings'])
            filtered_holdings = []
            
            for holding in filtered_data['holdings']:
                # Skip zero quantity holdings if configured
                if not self.config.include_zero_quantity and holding.get('quantity', 0) == 0:
                    continue
                
                # Skip holdings below minimum investment amount
                investment_value = holding.get('average_price', 0) * holding.get('quantity', 0)
                if investment_value < self.config.min_investment_amount:
                    continue
                
                filtered_holdings.append(holding)
            
            filtered_data['holdings'] = filtered_holdings
            
            # Filter positions (remove zero quantity positions)
            filtered_data['day_positions'] = [
                pos for pos in filtered_data['day_positions'] 
                if pos.get('quantity', 0) != 0
            ]
            
            filtered_data['net_positions'] = [
                pos for pos in filtered_data['net_positions'] 
                if pos.get('quantity', 0) != 0
            ]
            
            logger.info(f"✅ Filters applied: Holdings {original_holdings_count} → {len(filtered_holdings)}")
            return filtered_data
            
        except Exception as e:
            logger.error(f"❌ Error applying filters: {str(e)}")
            return data

    def prepare_analysis_prompt(self, filtered_data: Dict[str, Any]) -> str:
        """Prepare a comprehensive prompt for Gemini analysis"""
        
        # Calculate portfolio summary
        total_investment = sum(
            holding.get('average_price', 0) * holding.get('quantity', 0) 
            for holding in filtered_data['holdings']
        )
        
        current_value = sum(
            holding.get('last_price', 0) * holding.get('quantity', 0) 
            for holding in filtered_data['holdings']
        )
        
        total_pnl = sum(holding.get('pnl', 0) for holding in filtered_data['holdings'])
        
        # Create summary statistics
        summary_stats = {
            'total_holdings': len(filtered_data['holdings']),
            'total_investment': total_investment,
            'current_value': current_value,
            'total_pnl': total_pnl,
            'return_percentage': (total_pnl / total_investment * 100) if total_investment > 0 else 0,
            'active_positions': len(filtered_data['day_positions']) + len(filtered_data['net_positions']),
            'available_margin': filtered_data['equity_margin'].get('available', {}).get('cash', 0)
        }
        
        prompt = f"""
As a financial analyst, please analyze this Zerodha portfolio data and provide comprehensive insights:

## Portfolio Summary:
- Total Holdings: {summary_stats['total_holdings']}
- Total Investment: ₹{summary_stats['total_investment']:,.2f}
- Current Value: ₹{summary_stats['current_value']:,.2f}
- Total P&L: ₹{summary_stats['total_pnl']:,.2f}
- Return %: {summary_stats['return_percentage']:.2f}%
- Active Positions: {summary_stats['active_positions']}
- Available Cash: ₹{summary_stats['available_margin']:,.2f}

## Holdings Data:
{json.dumps(filtered_data['holdings'], indent=2, default=str)}

## Current Positions:
Day Positions: {json.dumps(filtered_data['day_positions'], indent=2, default=str)}
Net Positions: {json.dumps(filtered_data['net_positions'], indent=2, default=str)}

## Analysis Requirements:
Please provide analysis covering:

1. **Portfolio Performance Analysis**:
   - Overall portfolio performance and returns
   - Best and worst performing stocks
   - Sector-wise distribution and performance

2. **Risk Assessment**:
   - Portfolio concentration risk
   - Sector concentration
   - Individual stock weightage analysis

3. **Investment Insights**:
   - Quality of stock selection
   - Dividend-paying stocks analysis
   - Growth vs Value stock distribution

4. **Recommendations**:
   - Rebalancing suggestions
   - Risk mitigation strategies
   - Potential opportunities for improvement

5. **Market Context**:
   - How the portfolio aligns with current market trends
   - Sectoral outlook for held stocks

Please format your response in clear sections with actionable insights and specific recommendations based on the data provided.
"""
        
        return prompt

    def analyze_with_gemini(self, filtered_data: Dict[str, Any]) -> str:
        """Analyze portfolio data using Google Gemini Flash"""
        try:
            logger.info("🤖 Starting Gemini analysis...")
            
            prompt = self.prepare_analysis_prompt(filtered_data)
            
            # Make request to Gemini with error handling and retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.gemini_model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.3,
                            max_output_tokens=4000,
                        )
                    )
                    
                    analysis = response.text
                    logger.info("✅ Gemini analysis completed successfully")
                    return analysis
                    
                except Exception as e:
                    logger.warning(f"⚠️ Gemini request attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"❌ Error in Gemini analysis: {str(e)}")
            return f"Analysis failed: {str(e)}"

    def generate_report(self, analysis: str, filtered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive report combining data and analysis"""
        try:
            # Calculate additional metrics
            holdings_df = pd.DataFrame(filtered_data['holdings'])
            
            if not holdings_df.empty:
                # Top holdings by value
                holdings_df['current_value'] = holdings_df['last_price'] * holdings_df['quantity']
                top_holdings = holdings_df.nlargest(5, 'current_value')[
                    ['tradingsymbol', 'current_value', 'pnl', 'quantity']
                ].to_dict('records')
                
                # Sector distribution (if available)
                sector_distribution = holdings_df.groupby('exchange').agg({
                    'current_value': 'sum',
                    'pnl': 'sum'
                }).to_dict('index') if 'exchange' in holdings_df.columns else {}
                
            else:
                top_holdings = []
                sector_distribution = {}
            
            report = {
                'analysis_timestamp': datetime.now().isoformat(),
                'portfolio_summary': {
                    'total_holdings': len(filtered_data['holdings']),
                    'total_investment': sum(h.get('average_price', 0) * h.get('quantity', 0) for h in filtered_data['holdings']),
                    'current_value': sum(h.get('last_price', 0) * h.get('quantity', 0) for h in filtered_data['holdings']),
                    'total_pnl': sum(h.get('pnl', 0) for h in filtered_data['holdings']),
                },
                'top_holdings': top_holdings,
                'sector_distribution': sector_distribution,
                'gemini_analysis': analysis,
                'data_filters_applied': {
                    'min_investment_amount': self.config.min_investment_amount,
                    'include_zero_quantity': self.config.include_zero_quantity
                }
            }
            
            logger.info("✅ Report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {str(e)}")
            return {'error': str(e), 'gemini_analysis': analysis}

    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save the analysis report to a JSON file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"zerodha_portfolio_analysis_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Report saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving report: {str(e)}")
            raise

    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run the complete portfolio analysis pipeline"""
        try:
            logger.info("🚀 Starting complete portfolio analysis...")
            
            # Step 1: Fetch portfolio data
            raw_data = self.fetch_portfolio_data()
            
            # Step 2: Apply filters
            filtered_data = self.apply_filters(raw_data)
            
            # Step 3: Analyze with Gemini
            analysis = self.analyze_with_gemini(filtered_data)
            
            # Step 4: Generate comprehensive report
            report = self.generate_report(analysis, filtered_data)
            
            # Step 5: Save report
            filename = self.save_report(report)
            
            logger.info(f"✅ Complete analysis finished! Report saved as {filename}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Complete analysis failed: {str(e)}")
            raise
