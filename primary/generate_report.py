from primary.all_import import *

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

     