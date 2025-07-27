from primary.all_import import *
def create_detailed_holdings_table(portfolio_data):
    """Create detailed holdings table"""
    st.subheader("📋 Detailed Holdings")
    
    holdings = portfolio_data['holdings']
    if not holdings:
        st.info("No holdings to display")
        return
    
    df = pd.DataFrame(holdings)
    
    # Calculate additional columns
    df['Current Value'] = df['last_price'] * df['quantity']
    df['Invested Value'] = df['average_price'] * df['quantity']
    df['Return %'] = ((df['last_price'] - df['average_price']) / df['average_price'] * 100).round(2)
    df['Weight %'] = (df['Current Value'] / df['Current Value'].sum() * 100).round(2)
    
    # Display columns
    display_columns = [
        'tradingsymbol', 'quantity', 'average_price', 'last_price', 
        'Invested Value', 'Current Value', 'pnl', 'Return %', 'Weight %'
    ]
    
    # Style the dataframe
    styled_df = df[display_columns].style.format({
        'average_price': '₹{:.2f}',
        'last_price': '₹{:.2f}',
        'Invested Value': '₹{:,.0f}',
        'Current Value': '₹{:,.0f}',
        'pnl': '₹{:,.0f}',
        'Return %': '{:.2f}%',
        'Weight %': '{:.2f}%'
    }).apply(lambda x: ['background-color: #d4edda' if v > 0 else 'background-color: #f8d7da' if v < 0 else '' for v in x], subset=['pnl'])
    
    st.dataframe(styled_df, use_container_width=True, height=400)