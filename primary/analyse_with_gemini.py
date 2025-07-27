
from primary.all_import import *


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