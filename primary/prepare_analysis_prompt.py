from primary.all_import import *
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