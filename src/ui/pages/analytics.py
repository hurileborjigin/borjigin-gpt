# src/ui/pages/analytics.py
import streamlit as st
from src.ui.utils import init_session_state
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List

def render_analytics():
    """Render the analytics dashboard"""
    init_session_state()
    
    st.title("📊 Analytics Dashboard")
    st.markdown("Track your interview preparation progress and performance over time.")
    
    # Get performance data
    performance = st.session_state.orchestrator.get_mock_interview_summary()
    
    if not performance or performance.get('question_count', 0) == 0:
        st.info("👋 No practice data yet. Start practicing to see your analytics!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Go to Preparation Mode"):
                st.session_state.current_mode = "preparation"
                st.rerun()
        with col2:
            if st.button("💪 Go to Practice Mode"):
                st.session_state.current_mode = "practice"
                st.rerun()
        return
    
    # Overview Metrics
    st.header("📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "Total Questions",
        performance.get('question_count', 0)
    )
    
    col2.metric(
        "Average Score",
        f"{performance.get('average_score', 0):.1f}/10"
    )
    
    col3.metric(
        "Follow-ups Practiced",
        performance.get('follow_up_count', 0)
    )
    
    # Calculate improvement
    latest_scores = performance.get('latest_scores', [])
    if len(latest_scores) >= 2:
        recent_avg = sum(s.get('overall', 0) for s in latest_scores[-3:]) / min(3, len(latest_scores))
        older_avg = sum(s.get('overall', 0) for s in latest_scores[:3]) / min(3, len(latest_scores))
        improvement = recent_avg - older_avg
        col4.metric(
            "Improvement",
            f"{improvement:+.1f}",
            delta=f"{improvement:+.1f} points"
        )
    else:
        col4.metric("Improvement", "N/A")
    
    st.markdown("---")
    
    # Score Distribution
    st.header("🎯 Score Distribution")
    
    if latest_scores:
        # Create DataFrame for visualization
        score_data = []
        for i, score_dict in enumerate(latest_scores, 1):
            score_data.append({
                'Question': i,
                'Overall': score_dict.get('overall', 0),
                'Authenticity': score_dict.get('scores', {}).get('authenticity', 0),
                'Relevance': score_dict.get('scores', {}).get('relevance', 0),
                'Structure': score_dict.get('scores', {}).get('structure', 0),
                'Specificity': score_dict.get('scores', {}).get('specificity', 0),
                'Impact': score_dict.get('scores', {}).get('impact', 0)
            })
        
        df = pd.DataFrame(score_data)
        
        # Overall score trend
        st.subheader("Overall Score Trend")
        st.line_chart(df.set_index('Question')['Overall'])
        
        # Detailed metrics
        st.subheader("Detailed Metrics")
        
        metric_cols = ['Authenticity', 'Relevance', 'Structure', 'Specificity', 'Impact']
        st.line_chart(df.set_index('Question')[metric_cols])
        
        # Average by category
        st.subheader("Average Scores by Category")
        
        avg_scores = {
            'Authenticity': df['Authenticity'].mean(),
            'Relevance': df['Relevance'].mean(),
            'Structure': df['Structure'].mean(),
            'Specificity': df['Specificity'].mean(),
            'Impact': df['Impact'].mean()
        }
        
        avg_df = pd.DataFrame({
            'Category': list(avg_scores.keys()),
            'Average Score': list(avg_scores.values())
        })
        
        st.bar_chart(avg_df.set_index('Category'))
    
    st.markdown("---")
    
    # Strengths and Weaknesses Analysis
    st.header("💪 Strengths & Areas for Improvement")
    
    if latest_scores:
        # Aggregate strengths and improvements
        all_strengths = []
        all_improvements = []
        
        for score_dict in latest_scores:
            all_strengths.extend(score_dict.get('strengths', []))
            all_improvements.extend(score_dict.get('improvements', []))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Common Strengths")
            if all_strengths:
                # Count frequency
                from collections import Counter
                strength_counts = Counter(all_strengths)
                top_strengths = strength_counts.most_common(5)
                
                for strength, count in top_strengths:
                    st.success(f"**{strength}** (mentioned {count}x)")
            else:
                st.info("No strengths data yet")
        
        with col2:
            st.subheader("🔧 Common Areas to Improve")
            if all_improvements:
                from collections import Counter
                improvement_counts = Counter(all_improvements)
                top_improvements = improvement_counts.most_common(5)
                
                for improvement, count in top_improvements:
                    st.warning(f"**{improvement}** (mentioned {count}x)")
            else:
                st.info("No improvement data yet")
    
    st.markdown("---")
    
    # Iteration Analysis
    st.header("🔄 Iteration Analysis")
    
    session = st.session_state.orchestrator.short_term_memory.current_session
    if session and session.practice_session.iteration_history:
        st.markdown("See how your answers improved through iterations:")
        
        iteration_data = []
        for iter_dict in session.practice_session.iteration_history:
            iteration_data.append({
                'Iteration': iter_dict.get('iteration', 0),
                'Score': iter_dict.get('score', 0)
            })
        
        if iteration_data:
            iter_df = pd.DataFrame(iteration_data)
            st.line_chart(iter_df.set_index('Iteration'))
            
            avg_iterations = len(iteration_data) / max(1, performance.get('question_count', 1))
            st.metric("Average Iterations per Question", f"{avg_iterations:.1f}")
    else:
        st.info("No iteration data available yet")
    
    st.markdown("---")
    
    # Recommendations
    st.header("💡 Personalized Recommendations")
    
    recommendations = generate_recommendations(performance, latest_scores)
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"**{i}.** {rec}")
    
    st.markdown("---")
    
    # Export Analytics
    st.header("📥 Export Analytics")
    
    if st.button("Download Full Analytics Report"):
        from src.ui.utils import export_to_json
        
        analytics_data = {
            "summary": performance,
            "scores": latest_scores,
            "session_data": st.session_state.orchestrator.export_session(),
            "generated_at": datetime.now().isoformat()
        }
        
        export_to_json(
            analytics_data,
            f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

def generate_recommendations(performance: Dict[str, Any], scores: List[Dict]) -> List[str]:
    """Generate personalized recommendations based on performance"""
    recommendations = []
    
    avg_score = performance.get('average_score', 0)
    question_count = performance.get('question_count', 0)
    
    # Based on average score
    if avg_score < 6:
        recommendations.append(
            "📚 Focus on fundamentals: Review the STAR framework and practice structuring your answers."
        )
    elif avg_score < 8:
        recommendations.append(
            "🎯 You're doing well! Focus on adding more specific metrics and concrete examples to your answers."
        )
    else:
        recommendations.append(
            "🌟 Excellent work! Consider practicing more challenging questions and situational scenarios."
        )
    
    # Based on question count
    if question_count < 5:
        recommendations.append(
            "💪 Practice more questions to build confidence and identify patterns in your answers."
        )
    elif question_count < 15:
        recommendations.append(
            "🔄 Good progress! Try a full mock interview to simulate the real experience."
        )
    else:
        recommendations.append(
            "🎭 You've practiced extensively! Consider doing mock interviews with different companies and roles."
        )
    
    # Based on score consistency
    if scores:
        score_values = [s.get('overall', 0) for s in scores]
        if len(score_values) >= 3:
            import statistics
            std_dev = statistics.stdev(score_values)
            
            if std_dev > 2:
                recommendations.append(
                    "📊 Your scores vary significantly. Focus on consistency by developing a standard approach to answering questions."
                )
    
    # Based on specific metrics
    if scores:
        latest = scores[-1] if scores else {}
        metric_scores = latest.get('scores', {})
        
        if metric_scores.get('specificity', 10) < 6:
            recommendations.append(
                "🔍 Add more specific details: Include numbers, metrics, and concrete examples in your answers."
            )
        
        if metric_scores.get('structure', 10) < 6:
            recommendations.append(
                "🏗️ Improve structure: Practice using the STAR framework consistently for behavioral questions."
            )
        
        if metric_scores.get('impact', 10) < 6:
            recommendations.append(
                "💥 Emphasize impact: Always conclude with measurable results and the value you delivered."
            )
    
    # Follow-up practice
    follow_up_count = performance.get('follow_up_count', 0)
    if follow_up_count < 3:
        recommendations.append(
            "🔄 Practice follow-up questions more. Interviewers often dig deeper into your answers."
        )
    
    return recommendations[:5]  # Return top 5 recommendations