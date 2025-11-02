import os, re, json, requests, sympy as sp
from typing import List, Dict, Any, Tuple

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", "")

KB_DOCS = [
    {"text": "Integrate x * e^(x^2) dx => Let u = x^2; result = (1/2) e^(x^2) + C.", "meta": {"source": "local"}},
    {"text": "lim_{x->0} sin(x)/x = 1.", "meta": {"source": "local"}},
    {"text": "Differentiate x^3 + 4x -> 3x^2 + 4.", "meta": {"source": "local"}},
    {"text": "Integrate sin(x) dx = -cos(x) + C.", "meta": {"source": "local"}}
]

def kb_search(q: str) -> List[Dict[str, Any]]:
    q = q.lower()
    hits = []
    for doc in KB_DOCS:
        t = doc["text"].lower()
        score = len(set(q.split()) & set(t.split())) / max(1, len(set(q.split())))
        hits.append({"text": doc["text"], "score": score})
    return sorted(hits, key=lambda x: x["score"], reverse=True)

def input_guardrail(q: str) -> bool:
    k = ["integrate","differentiate","solve","limit","math","sin","cos","tan","derivative","equation","integral"]
    return any(x in q.lower() for x in k)

def sympy_solver(q: str) -> Tuple[str, str]:
    x = sp.symbols('x')
    try:
        if "differentiate" in q or "derivative" in q:
            e = sp.sympify(q.split("differentiate")[-1].strip() or q.split("derivative")[-1].strip())
            d = sp.diff(e, x)
            return f"Derivative of {e} is {d}", "ok"
        if "integrate" in q or "integral" in q:
            e = re.sub(r".*(integrate|integral)\s*", "", q).replace("dx","").strip()
            i = sp.integrate(sp.sympify(e), x)
            return f"Integral of {e} is {i} + C", "ok"
        if "solve" in q or "=" in q:
            eq = q.split("solve")[-1].strip() or q
            if "=" in eq:
                l, r = eq.split("=")
                s = sp.solve(sp.Eq(sp.sympify(l), sp.sympify(r)), x)
            else:
                s = sp.solve(sp.sympify(eq), x)
            return f"Solution: {s}", "ok"
        if "limit" in q:
            m = re.search(r"limit of (.+) as x approaches (.+)", q)
            if m:
                e, v = m.groups()
                lim = sp.limit(sp.sympify(e), x, sp.sympify(v))
                return f"Limit of {e} as x→{v} = {lim}", "ok"
    except:
        pass
    return "", "fail"

def web_search(q: str) -> str:
    if not SERPAPI_API_KEY: return "No SERPAPI key"
    try:
        from serpapi import GoogleSearch
        r = GoogleSearch({"engine":"google","q":q,"num":2,"api_key":SERPAPI_API_KEY}).get_dict()
        return "\n".join([i.get("snippet","") for i in r.get("organic_results",[])[:2]])
    except Exception as e:
        return str(e)

def openai_call(q: str, ctx: str) -> str:
    if not OPENAI_API_KEY: return "No OPENAI key"
    h = {"Authorization":f"Bearer {OPENAI_API_KEY}","Content-Type":"application/json"}
    d = {"model":"gpt-3.5-turbo","messages":[{"role":"user","content":f"Using this context:\n{ctx}\nAnswer: {q}"}]}
    r = requests.post("https://api.openai.com/v1/chat/completions",headers=h,json=d)
    if r.status_code==200: return r.json()["choices"][0]["message"]["content"]
    return f"OpenAI error {r.status_code}"

def query_agent(q: str) -> Dict[str,Any]:
    if not input_guardrail(q): return {"error":"Only math queries allowed"}
    kb = kb_search(q)
    sym, s = sympy_solver(q)
    if s=="ok": return {"source":"sympy","answer":sym}
    if kb and kb[0]["score"]>0.4: return {"source":"kb","answer":kb[0]["text"]}
    w = web_search(q)
    ai = openai_call(q,w)
    return {"source":"online","web":w,"answer":ai}

if __name__=="__main__":
    q1="Integrate x * e^(x^2) dx"
    q2="Evaluate integral of x^2 * e^(-x) from 0 to infinity"
    print("Q1:", query_agent(q1))
    print("\nQ2:", query_agent(q2))
