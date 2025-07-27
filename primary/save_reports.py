from primary.all_import import *


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