from primary.all_import import *
def create_portfolio_dashboard(analyzer, portfolio_data):
    """Create comprehensive portfolio dashboard"""
    
    holdings = portfolio_data['holdings']
    if not holdings:
        st.warning("No holdings found in your portfolio.")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(holdings)
    
    # Calculate metrics
    total_investment = (df['average_price'] * df['quantity']).sum()
    current_value = (df['last_price'] * df['quantity']).sum()
    total_pnl = df['pnl'].sum()
    total_returns = (total_pnl / total_investment * 100) if total_investment > 0 else 0
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>💰 Portfolio Value</h3>
            <h2>₹{:,.0f}</h2>
            <p>Current Market Value</p>
        </div>
        """.format(current_value), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Total Returns</h3>
            <h2>₹{:,.0f}</h2>
            <p>{:.2f}% Overall Return</p>
        </div>
        """.format(total_pnl, total_returns), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🏢 Holdings</h3>
            <h2>{}</h2>
            <p>Total Stocks</p>
        </div>
        """.format(len(holdings)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>💵 Invested</h3>
            <h2>₹{:,.0f}</h2>
            <p>Total Investment</p>
        </div>
        """.format(total_investment), unsafe_allow_html=True)
    
    # Voice summary
    if st.session_state.voice_enabled:
        summary_text = f"""Your portfolio is currently valued at {current_value:,.0f} rupees, 
        with total returns of {total_pnl:,.0f} rupees, representing a {total_returns:.1f} percent return. 
        You have {len(holdings)} different stock holdings."""
        analyzer.voice_assistant.speak(summary_text)
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Top Holdings by Value")
        df['current_value'] = df['last_price'] * df['quantity']
        top_holdings = df.nlargest(10, 'current_value')
        
        fig = px.bar(
            top_holdings, 
            x='current_value', 
            y='tradingsymbol',
            orientation='h',
            title="Top 10 Holdings by Market Value",
            color='pnl',
            color_continuous_scale='RdYlGn',
            hover_data=['quantity', 'average_price', 'last_price']
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 P&L Distribution")
        
        # Create P&L pie chart
        profit_stocks = df[df['pnl'] > 0]
        loss_stocks = df[df['pnl'] < 0]
        
        pnl_data = pd.DataFrame({
            'Category': ['Profitable Stocks', 'Loss Making Stocks'],
            'Count': [len(profit_stocks), len(loss_stocks)],
            'Total PnL': [profit_stocks['pnl'].sum(), abs(loss_stocks['pnl'].sum())]
        })
        
        fig = px.pie(
            pnl_data, 
            values='Count', 
            names='Category',
            title="Profit vs Loss Making Stocks",
            color_discrete_sequence=['#00CC96', '#FF6B6B']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance analysis
    st.subheader("📈 Performance Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Best performers
        best_performers = df.nlargest(5, 'pnl')[['tradingsymbol', 'pnl', 'quantity']]
        st.markdown("### 🏆 Top Gainers")
        for _, row in best_performers.iterrows():
            st.markdown(f"""
            <div class="success-card">
                <strong>{row['tradingsymbol']}</strong><br>
                Profit: ₹{row['pnl']:,.0f} | Qty: {row['quantity']}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Worst performers
        worst_performers = df.nsmallest(5, 'pnl')[['tradingsymbol', 'pnl', 'quantity']]
        st.markdown("### 📉 Top Losers")
        for _, row in worst_performers.iterrows():
            st.markdown(f"""
            <div class="warning-card">
                <strong>{row['tradingsymbol']}</strong><br>
                Loss: ₹{row['pnl']:,.0f} | Qty: {row['quantity']}
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # Portfolio composition
        st.markdown("### 🎯 Portfolio Stats")
        profitable_count = len(df[df['pnl'] > 0])
        loss_count = len(df[df['pnl'] < 0])
        
        st.metric("Profitable Stocks", profitable_count, f"{profitable_count/len(df)*100:.1f}%")
        st.metric("Loss Making Stocks", loss_count, f"{loss_count/len(df)*100:.1f}%")
        
        avg_return = df['pnl'].mean()
        st.metric("Average P&L per Stock", f"₹{avg_return:,.0f}")