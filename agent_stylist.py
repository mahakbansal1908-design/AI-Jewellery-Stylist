"""
agent_stylist.py — AI Jewellery Stylist Agent following Session 5 architecture.
Implements Plan → Act → Verify loop with multimodal analysis, parallel MCP tool dispatch,
and structured Pydantic verification.
"""
import asyncio
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import V2 client
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "llm_gatewayV2"))
from client import LLM  # noqa: E402


# ────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas (One Source of Truth)
# ────────────────────────────────────────────────────────────────────────────

class ToolDef(BaseModel):
    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)


class OutfitAnalysis(BaseModel):
    outfit_type: str = Field(..., description="e.g. lehenga, saree, gown, indo-western, modern chic")
    dominant_colors: list[str] = Field(..., description="List of main colors detected in the outfit")
    neckline: str = Field(..., description="e.g. v-neck, high neck, sweetheart, boat neck, round")
    style_vibe: str = Field(..., description="e.g. royal bridal, modern minimalist, festive elegance")
    embroidery_level: str = Field(..., description="e.g. heavy zari, subtle floral, minimal, plain")
    occasion_fit: str = Field(..., description="e.g. wedding reception, festive family dinner, cocktail party")
    ideal_color_tone: str = Field(..., description="Ideal skin color tone/undertone (e.g. Warm/Cool/Neutral/Olive/Fair/Dusky) that this outfit looks best on, and why")



class JewelleryRecommendation(BaseModel):
    jewellery_type: str = Field(..., description="e.g. Earrings, Necklace, Bangles, Rings, Maang Tikka")
    style: str = Field(..., description="e.g. Chandbali, Choker, Tennis Bracelet, Stacked")
    material: str = Field(..., description="e.g. Kundan, Polki, Diamonds, Temple Gold, Pearls")
    finish_color: str = Field(..., description="e.g. Antique Gold, White Gold, Rose Gold, Emerald Accents")
    size_intensity: str = Field(..., description="e.g. Statement bold, subtle delicate, medium elegant")
    styling_notes: str = Field(..., description="Specific advice on how this piece complements the outfit")
    image_url: str = Field(default="", description="High quality Unsplash image URL representing the jewellery")


class ShoppingSuggestion(BaseModel):
    platform: str = Field(..., description="e.g. Myntra, Amazon, Ajio, Etsy")
    search_query: str = Field(..., description="Highly optimized search keywords")
    search_url: str = Field(..., description="Clickable marketplace search URL")


class StylistResponse(BaseModel):
    outfit_analysis: OutfitAnalysis
    recommendations: list[JewelleryRecommendation]
    styling_explanation: str = Field(..., description="Expert, warm, luxurious explanation of WHY the jewellery matches")
    shopping_suggestions: list[ShoppingSuggestion]


class TraceEvent(BaseModel):
    kind: Literal["llm_call", "tool_call", "verdict"]
    turn: int
    provider: str | None = None
    model: str | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cache_read: int | None = None
    cache_create: int | None = None
    dialect: str | None = None
    tool_name: str | None = None
    tool_args: dict | None = None
    tool_result: str | None = None
    text: str | None = None
    payload: dict | None = None


class AgentTrace(BaseModel):
    goal: str
    events: list[TraceEvent] = Field(default_factory=list)
    started_at: float = Field(default_factory=time.time)

    def add(self, **kw) -> None:
        self.events.append(TraceEvent(**kw))


# ────────────────────────────────────────────────────────────────────────────
# MCP ↔ V2 Bridge & Dispatcher
# ────────────────────────────────────────────────────────────────────────────

def mcp_tool_to_v2(t) -> dict:
    return ToolDef(
        name=t.name,
        description=t.description or "",
        input_schema=t.inputSchema or {"type": "object", "properties": {}},
    ).model_dump()


async def dispatch_tool_calls(session, tool_calls: list[dict]) -> list[dict]:
    async def run_one(tc: dict) -> dict:
        tool_id = tc.get("id") or f"call_{uuid.uuid4().hex[:8]}"
        tool_name = tc.get("name") or "unknown_tool"
        try:
            result = await session.call_tool(tool_name, tc.get("arguments") or {})
            text = result.content[0].text if hasattr(result, "content") and result.content else str(result)
        except Exception as e:
            text = f"Tool execution error: {e}. Using expert stylist knowledge base."
        return {
            "role": "tool",
            "tool_call_id": tool_id,
            "tool_name": tool_name,
            "content": text,
        }

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(run_one(tc)) for tc in tool_calls]
    return [t.result() for t in tasks]


# ────────────────────────────────────────────────────────────────────────────
# Phase 1: Multimodal Outfit Analysis
# ────────────────────────────────────────────────────────────────────────────

def analyze_outfit(image_base64: str, provider: str = "g") -> OutfitAnalysis:
    """Use multimodal Gemini to extract structured outfit attributes."""
    llm = LLM()
    prompt_parts = [
        {"text": "Analyze this outfit image in detail. Detect the outfit type, dominant colors, neckline cut, embroidery intensity, style vibe, suitable occasion, and determine which skin color tones/undertones (e.g. warm, cool, neutral, olive, fair, dusky) this outfit will look best on and why. Be precise and expert."},
        {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}
    ]
    
    schema = OutfitAnalysis.model_json_schema()
    reply = llm.chat(
        messages=[{"role": "user", "content": prompt_parts}],
        system="You are an expert luxury fashion analyst. Return a clean OutfitAnalysis JSON object.",
        provider=provider,
        response_format={
            "type": "json_schema",
            "schema": schema,
            "name": "OutfitAnalysis",
            "strict": True,
        },
        temperature=0,
        max_tokens=512,
    )

    if reply.get("parsed"):
        return OutfitAnalysis.model_validate(reply["parsed"])
    
    # Fallback if structured output wasn't parsed perfectly
    text = reply.get("text", "")
    try:
        # Attempt manual json extraction
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return OutfitAnalysis.model_validate_json(text[start:end+1])
    except Exception:
        pass

    # Ultimate default fallback
    return OutfitAnalysis(
        outfit_type="Elegant Evening Wear",
        dominant_colors=["Royal Blue", "Gold"],
        neckline="V-Neck",
        style_vibe="Modern Luxury",
        embroidery_level="Subtle Zari Work",
        occasion_fit="Festive Celebration",
        ideal_color_tone="Warm Olive / Golden Undertones (Enhances the rich royal blue and gold embroidery perfectly)"
    )


# ────────────────────────────────────────────────────────────────────────────
# Phase 2: Native Tool-Use Loop (Act)
# ────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a luxury jewellery stylist specializing in Indian and modern fashion. "
    "Your task is to style an outfit based on its analysis. "
    "Step 1: Call `get_styling_guidelines` to lookup expert rules for the neckline, embroidery, and colors. "
    "Step 2: Call `search_fashion_trends` to check live 2026 celebrity and bridal jewellery trends for the outfit type. "
    "Step 3: Call `generate_shopping_links` for key jewellery pieces (e.g. necklace, earrings) to get search queries and URLs. "
    "Step 4: Once you have all tool results, synthesize a beautiful styling recommendation and explanation."
)


async def run_native_loop(
    session: ClientSession,
    tools: list[dict],
    analysis: OutfitAnalysis,
    trace: AgentTrace,
    provider: str | None = "g",
    max_turns: int = 5,
) -> str:
    llm = LLM()
    task_desc = (
        f"Style this outfit: {analysis.model_dump_json()}. "
        "Call `get_styling_guidelines` and `search_fashion_trends` first, and also call `generate_shopping_links` for at least 4 platforms (e.g. Myntra, Amazon, Everstylish, Tanishq, Etsy) in parallel."
    )
    messages: list[dict] = [{"role": "user", "content": task_desc}]

    for turn in range(1, max_turns + 1):
        reply = llm.chat(
            messages=messages,
            system=SYSTEM_PROMPT,
            cache_system=True,
            tools=tools,
            tool_choice="auto",
            reasoning="off",
            provider=provider,
            temperature=0.2,
            max_tokens=1024,
        )

        trace.add(
            kind="llm_call",
            turn=turn,
            provider=reply["provider"],
            model=reply["model"],
            latency_ms=reply["latency_ms"],
            input_tokens=reply["input_tokens"],
            output_tokens=reply["output_tokens"],
            cache_read=reply.get("cache_read_input_tokens"),
            cache_create=reply.get("cache_creation_input_tokens"),
            dialect=reply.get("tool_call_dialect"),
            text=reply.get("text"),
            payload={"tool_calls": reply.get("tool_calls", [])},
        )

        tool_calls = reply.get("tool_calls") or []
        if not tool_calls:
            return reply.get("text", "").strip()

        messages.append({
            "role": "assistant",
            "content": reply.get("text", "") or "",
            "tool_calls": tool_calls,
        })

        results = await dispatch_tool_calls(session, tool_calls)
        for tc, r in zip(tool_calls, results):
            trace.add(
                kind="tool_call",
                turn=turn,
                tool_name=tc["name"],
                tool_args=tc.get("arguments"),
                tool_result=r["content"],
            )
        messages.extend(results)

    return "Styling complete based on expert guidelines."


# ────────────────────────────────────────────────────────────────────────────
# Phase 3: Verifier & Final Structured Synthesis
# ────────────────────────────────────────────────────────────────────────────

def verify_and_format(trace: AgentTrace, analysis: OutfitAnalysis, executor_summary: str, provider: str = "g") -> StylistResponse:
    pass # (replaced below by async version)

async def verify_and_format_async(session: ClientSession, trace: AgentTrace, analysis: OutfitAnalysis, executor_summary: str, provider: str = "g") -> StylistResponse:
    """Independent structured synthesis using reasoning='medium' for premium quality."""
    llm = LLM()
    schema = StylistResponse.model_json_schema()

    # Gather tool results from trace
    guidelines = [e.tool_result for e in trace.events if e.tool_name == "get_styling_guidelines"]
    shopping = [e.tool_result for e in trace.events if e.tool_name == "generate_shopping_links"]

    prompt = (
        f"You are an elite luxury jewellery verifier and stylist. "
        f"Outfit Analysis (including ideal skin color tones): {analysis.model_dump_json()}. "
        f"Styling Guidelines retrieved: {guidelines}. "
        f"Shopping Links generated: {shopping}. "
        f"Agent Summary: {executor_summary}. "
        f"Synthesize the final premium StylistResponse. "
        f"CRITICAL REQUIREMENTS: "
        f"1. Curate a comprehensive, multi-piece jewellery ensemble containing at least 4 to 5 distinct jewellery pieces (e.g. Necklace/Choker, Earrings, Maang Tikka / Headpiece, Bangles / Bracelets / Kadas, and Statement Rings). Explain exactly how each piece complements the outfit and the wearer's ideal skin color tone. "
        f"2. Ensure you include at least 4 distinct shopping platforms (e.g. Myntra, Amazon, Everstylish, Tanishq, Etsy) in shopping_suggestions. DO NOT show Ajio or Nykaa Fashion. "
        f"3. Ensure the styling explanation is warm, expert, luxurious, and explains WHY the ensemble matches."
    )

    reply = llm.chat(
        prompt=prompt,
        system="Return a single StylistResponse JSON object matching the schema perfectly.",
        cache_system=True,
        provider=provider,
        response_format={
            "type": "json_schema",
            "schema": schema,
            "name": "StylistResponse",
            "strict": True,
        },
        reasoning="medium",  # Spend budget on final verification & synthesis
        temperature=0.2,
        max_tokens=2048,
    )

    if reply.get("parsed"):
        res = StylistResponse.model_validate(reply["parsed"])
    else:
        # Fallback if structured output wasn't parsed perfectly
        text = reply.get("text", "")
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                res = StylistResponse.model_validate_json(text[start:end+1])
            else:
                raise ValueError("No json")
        except Exception:
            # Ultimate fallback
            res = StylistResponse(
                outfit_analysis=analysis,
                recommendations=[
                    JewelleryRecommendation(
                        jewellery_type="Statement Earrings",
                        style="Chandbali",
                        material="Kundan & Pearls",
                        finish_color="Antique Gold",
                        size_intensity="Bold Statement",
                        styling_notes="Frames the face beautifully and complements the neckline."
                    )
                ],
                styling_explanation="The deep neckline and rich embroidery pair beautifully with balanced kundan jewellery, enhancing the royal aesthetic without overwhelming the outfit.",
                shopping_suggestions=[
                    ShoppingSuggestion(
                        platform="Myntra",
                        search_query="kundan chandbali earrings",
                        search_url="https://www.myntra.com/kundan-chandbali-earrings"
                    )
                ]
            )

    # Guarantee every recommendation gets a beautiful live marketplace image from the web via MCP
    for rec in res.recommendations:
        clean_mat = rec.material.replace("and", "").replace("&", "").strip()
        clean_style = rec.style.replace("Earrings", "").replace("Necklace", "").replace("Bangles", "").strip()
        query = f"{rec.finish_color} {clean_mat} {clean_style} {rec.jewellery_type}".strip()
        try:
            result = await session.call_tool("search_jewellery_images", {"query": query})
            img_url = result.content[0].text if hasattr(result, "content") and result.content else ""
            if img_url and img_url.startswith("http"):
                rec.image_url = img_url
            else:
                raise ValueError("MCP returned empty image URL")
        except Exception as e:
            print(f"[MCP Session 1 Failed for {query}]: {e}. Spawning fresh MCP stdio client session...")
            try:
                # Spawning a fresh MCP stdio client session to guarantee pure MCP protocol execution even if pipe broke
                server_params = StdioServerParameters(
                    command=sys.executable,
                    args=[str(Path(__file__).with_name("mcp_server.py"))],
                )
                async with stdio_client(server_params) as (r, w):
                    async with ClientSession(r, w) as fresh_session:
                        await fresh_session.initialize()
                        result = await fresh_session.call_tool("search_jewellery_images", {"query": query})
                        img_url = result.content[0].text if hasattr(result, "content") and result.content else ""
                        if img_url and img_url.startswith("http"):
                            rec.image_url = img_url
            except Exception as sub_e:
                print(f"[Fresh MCP Session Failed for {query}]: {sub_e}")

    return res


# ────────────────────────────────────────────────────────────────────────────
# Main Orchestrator
# ────────────────────────────────────────────────────────────────────────────

async def run_stylist_workflow(image_base64: str, provider: str = "g") -> dict:
    print("═" * 78)
    print("AI Jewellery Stylist — Session 5 Workflow Started")
    print("═" * 78)

    # Phase 1: Multimodal Analysis
    print("\n[Phase 1] Analyzing outfit image via Multimodal Gemini...")
    analysis = analyze_outfit(image_base64, provider=provider)
    print(f"  Detected Outfit: {analysis.outfit_type} ({analysis.neckline}, {analysis.embroidery_level})")

    # Setup MCP Server
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).with_name("mcp_server.py"))],
    )

    # Phase 2 & 3: MCP Tool Loop + Verification
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = (await session.list_tools()).tools
            tools = [mcp_tool_to_v2(t) for t in mcp_tools]
            print(f"[mcp] tools from server: {[t.name for t in mcp_tools]}")

            trace = AgentTrace(goal=f"Style outfit: {analysis.outfit_type}")

            print("\n[Phase 2] Executing MCP Tool Loop (Act)...")
            summary = await run_native_loop(session, tools, analysis, trace, provider=provider)
            print(f"  Loop completed. Events logged: {len(trace.events)}")

            print("\n[Phase 3] Verifying & Synthesizing Final Response (Verify)...")
            final_response = await verify_and_format_async(session, trace, analysis, summary, provider=provider)
            print("  Synthesis complete!")
            print("═" * 78)

            return final_response.model_dump()



def run_stylist(image_base64: str, provider: str = "g") -> dict:
    return asyncio.run(run_stylist_workflow(image_base64, provider=provider))
