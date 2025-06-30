from flask import Flask, request, jsonify
import asyncio
from requests_html import AsyncHTMLSession

app = Flask(__name__)

# Create a single AsyncHTMLSession globally
asession = AsyncHTMLSession()

@app.route('/')
def scrape_reviews():
    url = request.args.get('url')
    # Run the async function properly in main thread
    result = asyncio.run(scrape_reviews_async(url))
    return jsonify(result)

async def scrape_reviews_async(url):
    resp = await asession.get(url)
    await resp.html.arender(timeout=30)

    reviews = []
    for block in resp.html.find('div[data-hook=review]'):
        title_el = block.find('a[data-hook=review-title] span', first=True)
        text_el = block.find('span[data-hook=review-body] span', first=True)
        if title_el and text_el:
            reviews.append({
                'title': title_el.text,
                'text': text_el.text
            })

    return {'reviews': reviews}

if __name__ == '__main__':
    app.run(debug=True)

