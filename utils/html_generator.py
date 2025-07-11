def html_generator(title, sections, provider=None):
    """
    Generates an HTML string with a handwriting style using Tailwind CSS.

    :param title: Main title for the page ("Title 1").
    :param sections: A list of dictionaries, each containing:
        {
            "title": str (Title for the section e.g. "Title 2"),
            "bullets": [
                ("bold_text", "regular_text"),
                ("bold_text_2", "regular_text_2"),
                ...
            ]
        }
    :param provider: Optional LLM provider name to append to title (e.g., "openai", "gemini")
    :return: A string of HTML content.
    """
    # Prepare title with provider if specified
    display_title = title
    if provider:
        display_title = f"{title} ({provider.upper()})"
    
    # Start building the HTML
    html_template = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Youtube Made Simple</title>
  <!-- Using Tailwind CSS CDN -->
  <link
    rel=\"stylesheet\"
    href=\"https://unpkg.com/tailwindcss@2.2.19/dist/tailwind.min.css\"
  />
  <!-- Google Font for a clean, professional style -->
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" />
  <link
    href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap\"
    rel=\"stylesheet\"
  />
  <style>
    body {{
      background-color: #f7fafc;
      font-family: 'Inter', sans-serif;
    }}
    h1, h2 {{
      font-weight: 700;
      margin-bottom: 0.5rem;
    }}
    ul {{
      list-style-type: disc;
      margin-left: 1.5rem;
      margin-bottom: 1.5rem;
    }}
    li {{
      margin-bottom: 1rem;
    }}
    ol {{
      list-style-type: decimal;
      margin-left: 2rem;
      margin-top: 0.5rem;
    }}
    ol li {{
      margin-bottom: 0.2rem;
    }}
    .bullet-content ol {{
      margin-top: 0.3rem;
      margin-bottom: 0.3rem;
    }}
  </style>
</head>
<body class=\"min-h-screen flex items-center justify-center p-4\">
  <div class=\"max-w-2xl w-full bg-white rounded-2xl shadow-lg p-6\">
    <!-- Title 1 -->
    <h1 class=\"text-4xl text-gray-800 mb-6\">{display_title}</h1>"""

    # For each section, add a sub-title (Title 2, etc.) and bullet points.
    for section in sections:
        section_title = section.get("title", "")
        bullets = section.get("bullets", [])

        # Add the section's title (Title 2, Title 3, etc.)
        html_template += f"""
    <h2 class=\"text-2xl text-gray-800 mb-4\">{section_title}</h2>
    <ul class=\"text-gray-600\">"""

        # Create list items for each bullet pair
        for bold_text, normal_text in bullets:
            html_template += f"""
      <li>
        <strong>{bold_text}</strong><br />
        <div class="bullet-content">{normal_text}</div>
      </li>"""

        html_template += "\n    </ul>"

    # Close the main container and body
    html_template += """
  </div>
</body>
</html>"""

    return html_template

if __name__ == "__main__":
    sections_data = [
        {
            "title": "Title 2",
            "bullets": [
                ("First line of bullet 1", "Additional normal text."),
                ("First line of bullet 2", "Another detail in normal weight."),
            ]
        },
        {
            "title": "Title 3",
            "bullets": [
                ("First line of bullet 3", "More text in normal weight for bullet 3. <ol><li>1</li><li>2</li><li>3</li></ol>"),
            ]
        }
    ]
    html_content = html_generator("Title 1", sections_data) 
    with open("output.html", "w") as file:
        file.write(html_content)
