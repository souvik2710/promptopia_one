from primary.all_import import *

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