"""
MCP server for the AI Jewellery Stylist MVP.
Exposes expert styling guidelines and shopping query generators.
"""
import urllib.parse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("jewellery-stylist-server")


@mcp.tool()
def get_styling_guidelines(neckline: str = "", embroidery_level: str = "", dominant_colors: list[str] = None) -> str:
    """
    Lookup expert fashion styling rules based on neckline, embroidery intensity, and colors.
    """
    rules = []
    nl = (neckline or "").lower()
    emb = (embroidery_level or "").lower()
    cols = [c.lower() for c in dominant_colors or []]

    # Neckline rules
    if any(k in nl for k in ["v-neck", "plunge", "deep", "sweetheart"]):
        rules.append("Neckline Rule: Excellent for layered kundan chokers, pendant necklaces, or elegant princess-length sets.")
    elif any(k in nl for k in ["high", "halter", "turtle", "boat", "collar"]):
        rules.append("Neckline Rule: Avoid heavy necklaces. Focus on statement earrings (chandbalis/jhumkas) and stacked bangles/bracelets.")
    elif any(k in nl for k in ["round", "scoop", "square", "off-shoulder"]):
        rules.append("Neckline Rule: Pairs beautifully with collar necklaces, chokers, or medium statement sets.")
    else:
        rules.append("Neckline Rule: Balance the necklace length with the neckline cut to ensure it sits gracefully.")

    # Embroidery rules
    if any(k in emb for k in ["heavy", "intricate", "dense", "bridal", "high"]):
        rules.append("Embroidery Rule: The outfit is rich in detail. Recommend lighter or balanced jewellery so it complements rather than competes.")
    elif any(k in emb for k in ["minimal", "light", "plain", "subtle", "low"]):
        rules.append("Embroidery Rule: Minimalist outfit. This is the perfect canvas for bold statement jewellery or intricate heavy pieces.")
    else:
        rules.append("Embroidery Rule: Maintain a harmonious balance between outfit embroidery and jewellery craftsmanship.")

    # Color tone rules
    warm_tones = {"red", "maroon", "orange", "yellow", "gold", "beige", "rust", "mustard", "coral"}
    cool_tones = {"blue", "navy", "teal", "purple", "lavender", "silver", "grey"}
    if any(c in warm_tones for c in cols):
        rules.append("Color Rule: Warm dominant tones pair spectacularly with yellow gold, antique gold, kundan, and polki finishes.")
    elif any(c in cool_tones for c in cols):
        rules.append("Color Rule: Cool dominant tones pair exceptionally well with white gold, silver, diamonds, pearls, or rhodium finishes.")
    else:
        rules.append("Color Rule: Versatile palette. Choose metal finishes that complement the undertone of the outfit.")

    return "\n".join(rules)


@mcp.tool()
def generate_shopping_links(jewellery_type: str = "necklace", style: str = "elegant", platform: str = "Myntra") -> dict:
    """
    Generate smart search queries and clickable marketplace URLs for Amazon, Myntra, Everstylish, Tanishq, or Etsy.
    """
    p = (platform or "Myntra").strip()
    jt = (jewellery_type or "necklace").strip()
    st = (style or "elegant").strip()
    query = f"{st} {jt}"

    # Generate platform-specific search URLs
    encoded_query = urllib.parse.quote(query)
    url = ""
    if p.lower() == "amazon":
        url = f"https://www.amazon.in/s?k={encoded_query}"
    elif p.lower() == "myntra":
        url = f"https://www.myntra.com/{encoded_query.replace('%20', '-')}"
    elif "everstylish" in p.lower():
        url = f"https://everstylish.com/catalogsearch/result/?q={encoded_query}"
    elif "tanishq" in p.lower():
        url = f"https://www.tanishq.co.in/search?q={encoded_query}"
    elif p.lower() == "etsy":
        url = f"https://www.etsy.com/in-en/search?q={encoded_query}"
    else:
        url = f"https://www.google.com/search?q={encoded_query}+buy+online"

    return {
        "platform": p,
        "search_query": query,
        "search_url": url
    }



@mcp.tool()
def search_fashion_trends(query: str = "jewellery") -> str:
    """
    Search the live web for current fashion trends, celebrity bridal looks, or jewellery styles.
    """
    import urllib.request
    import re
    import ssl
    try:
        context = ssl._create_unverified_context()
        clean_query = f"{query} jewellery fashion trends 2026"
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(clean_query)}"
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10, context=context) as response:
            html = response.read().decode("utf-8")
            
        snippets = re.findall(r'<a class="result__snippet[^>]*>([\s\S]*?)</a>', html)
        if not snippets:
            return "No live trend snippets found. Relying on elite stylist training."
            
        clean_snippets = []
        for s in snippets[:5]:
            text = re.sub(r'<[^>]+>', '', s).strip()
            text = text.replace("&#x27;", "'").replace("&quot;", '"').replace("&amp;", "&").replace("<b>", "").replace("</b>", "")
            clean_snippets.append(f"- {text}")
            
        return f"Live Web Trends for '{query}':\n" + "\n".join(clean_snippets)
    except Exception as e:
        return f"Live search temporarily unavailable ({e}). Using expert stylist knowledge base."


@mcp.tool()
def search_jewellery_images(query: str = "kundan jewellery") -> str:
    """
    Search the live web for real product and style images of jewellery. Returns a direct image URL.
    """
    import urllib.request
    import urllib.parse
    import re
    import ssl
    try:
        context = ssl._create_unverified_context()
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        # 0. Extract core keywords to ensure high match rate across marketplaces
        # E.g., convert "Rose Gold Diamonds Emeralds Layered Choker Neckpiece" -> "diamond choker necklace"
        q_lower = query.lower()
        core_query = query
        if any(w in q_lower for w in ["neck", "choker", "pendant", "haar", "mala"]):
            if "choker" in q_lower:
                core_query = "choker necklace"
            else:
                core_query = "necklace"
            # Add primary material if present
            for mat in ["kundan", "polki", "diamond", "emerald", "ruby", "pearl", "gold", "silver", "zirconia", "meenakari"]:
                if mat in q_lower:
                    core_query = f"{mat} {core_query}"
                    break
        elif any(w in q_lower for w in ["earring", "jhumk", "chandbali", "stud", "drop"]):
            if "jhumk" in q_lower:
                core_query = "jhumkas"
            elif "chandbali" in q_lower:
                core_query = "chandbali earrings"
            elif "drop" in q_lower:
                core_query = "drop earrings"
            else:
                core_query = "earrings"
            for mat in ["kundan", "polki", "diamond", "emerald", "ruby", "pearl", "gold", "silver", "zirconia"]:
                if mat in q_lower:
                    core_query = f"{mat} {core_query}"
                    break
        elif any(w in q_lower for w in ["bangle", "kada", "bracelet", "wrist"]):
            if "kada" in q_lower:
                core_query = "kada"
            elif "bracelet" in q_lower:
                core_query = "bracelet"
            else:
                core_query = "bangles"
            for mat in ["kundan", "polki", "diamond", "gold", "silver", "zirconia"]:
                if mat in q_lower:
                    core_query = f"{mat} {core_query}"
                    break
        elif any(w in q_lower for w in ["ring", "finger"]):
            core_query = "finger ring"
            for mat in ["diamond", "solitaire", "gold", "silver", "zirconia", "kundan"]:
                if mat in q_lower:
                    core_query = f"{mat} ring"
                    break
        elif any(w in q_lower for w in ["hair", "head", "tikka", "patti", "passa", "maang"]):
            if "patti" in q_lower or "sheesh" in q_lower:
                core_query = "matha patti"
            elif "passa" in q_lower:
                core_query = "passa"
            else:
                core_query = "maang tikka"
            for mat in ["kundan", "polki", "gold", "silver", "pearl"]:
                if mat in q_lower:
                    core_query = f"{mat} {core_query}"
                    break

        # 1. Scrape Everstylish live marketplace catalog using the refined core query
        try:
            es_url = f"https://everstylish.com/catalogsearch/result/?q={urllib.parse.quote(core_query)}"
            req = urllib.request.Request(es_url, headers=headers)
            with urllib.request.urlopen(req, timeout=7, context=context) as response:
                html = response.read().decode("utf-8")
            imgs = [u for u in re.findall(r'src=[\"\'](https://everstylish\.com/[^\"\']+\.(?:jpg|png|webp))[\"\']', html) if 'catalog/product' in u]
            if imgs:
                # Pick deterministically based on full query hash so multiple tiles in same category get distinct images
                return imgs[abs(hash(query)) % len(imgs)]
        except Exception:
            pass

        # 2. Backup Marketplace Scraper: Kushal's Fashion Jewellery using core query
        try:
            kushal_url = f"https://www.kushals.com/search?q={urllib.parse.quote(core_query)}"
            req = urllib.request.Request(kushal_url, headers=headers)
            with urllib.request.urlopen(req, timeout=7, context=context) as response:
                html = response.read().decode("utf-8")
            imgs = [u for u in re.findall(r'https://cdn\.shopify\.com/s/files/[^\s\"\'<>?]+\.(?:jpg|png|webp)', html) if 'products' in u or 'files/' in u]
            imgs = [u for u in imgs if not any(b in u.lower() for b in ['app_download', 'icon', 'logo', 'badge', 'button'])]
            if imgs:
                return imgs[abs(hash(query)) % len(imgs)]
        except Exception:
            pass

        # 3. Fallback Everstylish search using ultra-broad keywords if specific query had 0 matches
        try:
            ultra_broad = core_query.split()[-1] # E.g. "necklace", "earrings", "bangles", "ring", "tikka"
            es_url2 = f"https://everstylish.com/catalogsearch/result/?q={urllib.parse.quote(ultra_broad)}"
            req2 = urllib.request.Request(es_url2, headers=headers)
            with urllib.request.urlopen(req2, timeout=7, context=context) as response:
                html2 = response.read().decode("utf-8")
            imgs2 = [u for u in re.findall(r'src=[\"\'](https://everstylish\.com/[^\"\']+\.(?:jpg|png|webp))[\"\']', html2) if 'catalog/product' in u]
            if imgs2:
                return imgs2[abs(hash(query)) % len(imgs2)]
        except Exception:
            pass

        # 4. Final Backup Bing search with negative keywords for isolated product shots using FULL query for exact description match
        try:
            clean_query = f"{query} jewellery product shot white background isolated -person -model -woman -wearer"
            bing_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(clean_query)}"
            bing_req = urllib.request.Request(bing_url, headers=headers)
            with urllib.request.urlopen(bing_req, timeout=7, context=context) as response:
                bing_html = response.read().decode("utf-8")
            urls = re.findall(r'https://tse[0-9]\.mm\.bing\.net/th/id/OIP[^&\s\"\'<>?]+', bing_html)
            if urls:
                return urls[0]
        except Exception:
            pass

        # 5. Ultimate Curated Category-Specific Backup Images (Expanded 4-to-5 High-Resolution Product Shots per Category)
        backup_images = {
            "earring": [
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1109578-2-2.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1109085-3-3.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1105252-2.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1109818-2.jpg"
            ],
            "neck": [
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1110418-m2.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/5/_/5.1_1.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1108392-2.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1109080-2.jpg"
            ],
            "bangle": [
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1104298-7.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1106992-t_1.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1109150-2.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1108225-2.jpg"
            ],
            "kada": [
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1104298-7.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1106992-t_1.jpg"
            ],
            "ring": [
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1108157-2-2.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1108160-2.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1108165-2.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1108170-2.jpg"
            ],
            "tikka": [
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1107755-3.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1107760-2.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1107765-2.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1107770-2.jpg"
            ],
            "head": [
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1107755-3.jpg",
                "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1107760-2.jpg"
            ]
        }
        
        for cat, urls in backup_images.items():
            if cat in q_lower:
                idx = abs(hash(query)) % len(urls)
                return urls[idx]
                
        return "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1110418-m2.jpg"
    except Exception as e:
        return "https://everstylish.com/media/catalog/product/cache/32d6a1cc700912c0dcf6eda1e76255f8/j/e/jew1110418-m2.jpg"





if __name__ == "__main__":
    mcp.run(transport="stdio")

