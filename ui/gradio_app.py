"""
Gradio Frontend Interface
Simple MVP UI for blog generation.
"""

import gradio as gr
import requests
import json
from typing import Dict, Tuple

# API endpoint (adjust if running remotely)
API_URL = "http://localhost:8000"


def format_blog_output(response: Dict) -> Tuple[str, str, str]:
    """
    Format blog response for display.
    
    Args:
        response: API response dictionary
        
    Returns:
        Tuple of (blog_html, keywords_text, analysis_text)
    """
    if not response.get('success', False):
        error = response.get('error', 'Unknown error')
        return f"<h3 style='color: red;'>Error: {error}</h3>", "", ""
    
    blog = response['blog']
    keywords = response['keywords']
    analysis = response['analysis']
    
    # Format blog as HTML
    blog_html = f"""
    <div style='font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;'>
        <h1 style='color: #2c3e50;'>{blog['title']}</h1>
        
        <div style="
            background: linear-gradient(135deg, #EEF2FF, #E0E7FF);
            padding: 18px;
            border-radius: 14px;
            margin: 22px 0;
            border-left: 5px solid #4F46E5;
        ">
            <strong style="
                color: #4F46E5;
                font-size: 15px;
                letter-spacing: 0.3px;
            ">
                Meta Description
            </strong>
            <br/>
            <em style="
                color: #1E293B;
                font-style: normal;
                font-size: 15px;
                line-height: 1.6;
                display: block;
                margin-top: 6px;
            ">
                {blog['meta_description']}
            </em>
        </div>


        
        <div style='margin: 20px 0;'>
            <h2 style='color: #34495e;'>Introduction</h2>
            <p style='line-height: 1.8;'>{blog['introduction']}</p>
        </div>
    """
    
    # Add sections
    for section in blog.get('sections', []):
        blog_html += f"""
        <div style='margin: 25px 0;'>
            <h2 style='color: #34495e;'>{section['heading']}</h2>
            <p style='line-height: 1.8;'>{section['content']}</p>
        </div>
        """
    
    # Add conclusion and CTA
    blog_html += f"""
        <div style='margin: 20px 0;'>
            <h2 style='color: #34495e;'>Conclusion</h2>
            <p style='line-height: 1.8;'>{blog['conclusion']}</p>
        </div>
        
        <div style='background: #3498db; color: white; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;'>
            <strong>{blog['cta']}</strong>
        </div>
        
        <div style='margin-top: 30px; padding-top: 20px; border-top: 2px solid #ecf0f1;'>
            <p><strong>Tags:</strong> {', '.join(blog.get('tags', []))}</p>
            <p><strong>Word Count:</strong> {response['word_count']} words</p>
            <p><strong>Processing Time:</strong> {response['processing_time']}s</p>
        </div>
    </div>
    """
    
    # Format keywords
    keywords_text = f"""**Primary Keywords:**
{', '.join(keywords['primary_keywords'])}

**Secondary Keywords:**
{', '.join(keywords['secondary_keywords'])}

**Keyword Density:**
"""
    for kw, density in list(keywords['keyword_density'].items())[:10]:
        keywords_text += f"- {kw}: {density*100:.2f}%\n"
    
    # Format analysis
    analysis_text = f"""**Summary:**
{analysis['summary']}

**Detected Intent:** {analysis['intent'].upper()}

**Main Topics:**
{', '.join(analysis['topics'])}

**Content Length:** {analysis['content_length']} characters
"""
    
    return blog_html, keywords_text, analysis_text


def generate_blog(url: str, tone: str, word_count: int, include_meta: bool) -> Tuple[str, str, str]:
    """
    Call API to generate blog.
    
    Args:
        url: Website URL
        tone: Blog tone
        word_count: Target word count
        include_meta: Include meta info
        
    Returns:
        Tuple of formatted outputs
    """
    try:
        # Validate inputs
        if not url:
            return "<h3 style='color: red;'>Please enter a URL</h3>", "", ""
        
        # Prepare request
        payload = {
            "url": url,
            "tone": tone.lower(),
            "word_count": int(word_count),
            "include_meta": include_meta
        }
        
        # Call API
        response = requests.post(
            f"{API_URL}/generate-blog",
            json=payload,
            timeout=120  # 2 minutes timeout
        )
        
        # Parse response
        if response.status_code == 200:
            data = response.json()
            return format_blog_output(data)
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            return f"<h3 style='color: red;'>Error: {error_msg}</h3>", "", ""
            
    except requests.exceptions.Timeout:
        return "<h3 style='color: red;'>Request timeout. Please try again.</h3>", "", ""
    except requests.exceptions.ConnectionError:
        return "<h3 style='color: red;'>Cannot connect to API. Make sure the server is running.</h3>", "", ""
    except Exception as e:
        return f"<h3 style='color: red;'>Error: {str(e)}</h3>", "", ""


def estimate_cost(url: str, word_count: int) -> str:
    """
    Estimate generation cost.
    
    Args:
        url: Website URL
        word_count: Target word count
        
    Returns:
        Cost estimation text
    """
    try:
        if not url:
            return "Please enter a URL"
        
        response = requests.post(
            f"{API_URL}/estimate-cost",
            params={"url": url, "word_count": int(word_count)},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return f"""**Cost Estimation:**
- Provider: {data['provider'].upper()}
- Model: {data['model']}
- Estimated Cost: ${data['estimated_cost_usd']:.4f} USD
- Word Count: {data['word_count']} words
            """
        else:
            return "Cost estimation failed"
            
    except Exception as e:
        return f"Error: {str(e)}"


# Build Gradio interface
with gr.Blocks(title="AI Blog Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 AI Blog Generator
    
    Generate SEO-optimized blog posts from any website URL using AI.
    
    **How it works:**
    1. Enter a website URL
    2. Choose your preferences (tone, word count)
    3. Click "Generate Blog"
    4. Get a complete, SEO-optimized blog post!
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            url_input = gr.Textbox(
                label="Website URL",
                placeholder="https://example.com",
                info="Enter the URL of the website you want to generate a blog about"
            )
            
            with gr.Row():
                tone_input = gr.Dropdown(
                    choices=["Professional", "Casual", "Technical", "Conversational"],
                    value="Professional",
                    label="Blog Tone"
                )
                
                word_count_input = gr.Slider(
                    minimum=300,
                    maximum=2000,
                    value=800,
                    step=100,
                    label="Target Word Count"
                )
            
            include_meta_input = gr.Checkbox(
                value=True,
                label="Include SEO Meta Description"
            )
            
            with gr.Row():
                generate_btn = gr.Button("🚀 Generate Blog", variant="primary", size="lg")
                estimate_btn = gr.Button("💰 Estimate Cost", variant="secondary")
        
        with gr.Column(scale=1):
            gr.Markdown("### ℹ️ Tips")
            gr.Markdown("""
            - **Professional**: Business, corporate
            - **Casual**: Friendly, relaxed
            - **Technical**: In-depth, detailed
            - **Conversational**: Personal, engaging
            
            **Recommended word count:**
            - Short form: 300-500 words
            - Medium form: 500-1000 words
            - Long form: 1000-2000 words
            """)
    
    gr.Markdown("---")
    
    with gr.Tabs():
        with gr.TabItem("📝 Generated Blog"):
            blog_output = gr.HTML(label="Blog Post")
        
        with gr.TabItem("🔑 Keywords & SEO"):
            keywords_output = gr.Markdown(label="Keyword Analysis")
        
        with gr.TabItem("📊 Content Analysis"):
            analysis_output = gr.Markdown(label="Topic Analysis")
        
        with gr.TabItem("💵 Cost Estimate"):
            cost_output = gr.Markdown(label="Cost Estimation")
    
    # Event handlers
    generate_btn.click(
        fn=generate_blog,
        inputs=[url_input, tone_input, word_count_input, include_meta_input],
        outputs=[blog_output, keywords_output, analysis_output]
    )
    
    estimate_btn.click(
        fn=estimate_cost,
        inputs=[url_input, word_count_input],
        outputs=cost_output
    )
    
    gr.Markdown("""
    ---
    ### 🛠️ Technical Stack
    - **Backend**: FastAPI + Python
    - **NLP**: KeyBERT, SentenceTransformers (local, no LLM)
    - **LLM**: Google Gemini
    - **Frontend**: Gradio
    
    **Note**: Make sure the FastAPI server is running at `http://localhost:8000`
    """)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # Set True to create public link
    )
