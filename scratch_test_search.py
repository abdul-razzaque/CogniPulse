import urllib.request
import urllib.parse
import re
import html

def search_ddg_html(query):
    encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=6.0) as resp:
            content = resp.read().decode('utf-8')
            # Extract titles and snippets
            snippets = re.findall(r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>', content, re.DOTALL)
            results = []
            for s in snippets[:3]:
                clean = html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
                if clean:
                    results.append(clean)
            return results
    except Exception as e:
        print('Error:', e)
        return []

if __name__ == '__main__':
    res = search_ddg_html('computer science fields careers overview')
    for idx, r in enumerate(res):
        print(f"[{idx+1}] {r}\n")
