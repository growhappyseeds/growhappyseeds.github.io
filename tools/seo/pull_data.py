#!/usr/bin/env python3
"""Pull Google Search Console and GA4 data for growhappyseeds.com into tools/seo/data/.

Runs on GitHub Actions (see .github/workflows/seo-data.yml) with a Google service
account whose JSON key is in the repository secret GOOGLE_SA_JSON. The account
must be a user on the Search Console property (sc-domain:growhappyseeds.com)
and a Viewer on GA4 property 558625133.

Writes, per run (UTC date of the run):
  tools/seo/data/gsc/YYYY-MM-DD.json   last 28 days by date; top queries and pages
                                        for the last 7 and 28 days; the last 3 days
                                        page+query detail (Search Console lags ~2-3 days)
  tools/seo/data/ga4/YYYY-MM-DD.json   last 28 days by date and channel; landing pages
                                        for organic search; key events
  tools/seo/data/latest.json            pointer + headline numbers for the Analyst agent

Only reads; never changes site pages.
"""
import json, os, sys, datetime, pathlib, urllib.parse
import google.auth.transport.requests
from google.oauth2 import service_account

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "tools/seo/data"
SITE = "sc-domain:growhappyseeds.com"
GA4_PROPERTY = os.environ.get("GA4_PROPERTY", "558625133")
TODAY = datetime.date.today()
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly",
          "https://www.googleapis.com/auth/analytics.readonly"]

creds = service_account.Credentials.from_service_account_info(
    json.loads(os.environ["GOOGLE_SA_JSON"]), scopes=SCOPES)
session = google.auth.transport.requests.AuthorizedSession(creds)

# Use whichever Search Console property the service account can see: the Domain
# property (sc-domain:) or a URL-prefix property (https://growhappyseeds.com/).
_sites = session.get("https://searchconsole.googleapis.com/webmasters/v3/sites", timeout=60)
if _sites.status_code >= 400:
    sys.exit(f"Search Console site list -> {_sites.status_code}: {_sites.text[:500]}")
_visible = [s["siteUrl"] for s in _sites.json().get("siteEntry", [])]
for _cand in (SITE, "https://growhappyseeds.com/", "https://www.growhappyseeds.com/", "http://growhappyseeds.com/"):
    if _cand in _visible:
        SITE = _cand
        break
else:
    sys.exit(f"Service account sees no growhappyseeds.com property in Search Console (sees: {_visible}). "
             "Add its email under Search Console > Settings > Users and permissions.")


def post(url, body):
    r = session.post(url, json=body, timeout=60)
    if r.status_code >= 400:
        sys.exit(f"{url} -> {r.status_code}: {r.text[:500]}")
    return r.json()


def gsc_query(start, end, dimensions, row_limit=250, filters=None):
    body = {"startDate": start.isoformat(), "endDate": end.isoformat(),
            "dimensions": dimensions, "rowLimit": row_limit, "dataState": "all"}
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]
    data = post(f"https://searchconsole.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(SITE, safe='')}/searchAnalytics/query", body)
    return [{"keys": r["keys"], "clicks": r["clicks"], "impressions": r["impressions"],
             "ctr": round(r["ctr"], 4), "position": round(r["position"], 1)} for r in data.get("rows", [])]


def ga4_report(dimensions, metrics, start, end, limit=250, dimension_filter=None):
    body = {"dateRanges": [{"startDate": start, "endDate": end}],
            "dimensions": [{"name": d} for d in dimensions],
            "metrics": [{"name": m} for m in metrics], "limit": limit}
    if dimension_filter:
        body["dimensionFilter"] = dimension_filter
    data = post(f"https://analyticsdata.googleapis.com/v1beta/properties/{GA4_PROPERTY}:runReport", body)
    rows = []
    for r in data.get("rows", []):
        row = {d: v["value"] for d, v in zip(dimensions, r["dimensionValues"])}
        row.update({m: float(v["value"]) if "." in v["value"] else int(v["value"]) for m, v in zip(metrics, r["metricValues"])})
        rows.append(row)
    return rows


def main():
    (OUT / "gsc").mkdir(parents=True, exist_ok=True)
    (OUT / "ga4").mkdir(parents=True, exist_ok=True)
    end = TODAY - datetime.timedelta(days=1)
    d7 = end - datetime.timedelta(days=6)
    d28 = end - datetime.timedelta(days=27)
    recent = end - datetime.timedelta(days=2)

    gsc = {
        "pulled": TODAY.isoformat(), "site": SITE, "range": [d28.isoformat(), end.isoformat()],
        "by_date": gsc_query(d28, end, ["date"], 400),
        "queries_7d": gsc_query(d7, end, ["query"], 250),
        "queries_28d": gsc_query(d28, end, ["query"], 500),
        "pages_7d": gsc_query(d7, end, ["page"], 250),
        "pages_28d": gsc_query(d28, end, ["page"], 500),
        "page_query_3d": gsc_query(recent, end, ["page", "query"], 1000),
        "countries_28d": gsc_query(d28, end, ["country"], 50),
        "devices_28d": gsc_query(d28, end, ["device"], 5),
    }
    (OUT / "gsc" / f"{TODAY.isoformat()}.json").write_text(json.dumps(gsc, indent=1))

    organic = {"filter": {"fieldName": "sessionDefaultChannelGroup", "stringFilter": {"value": "Organic Search"}}}
    ga4 = {
        "pulled": TODAY.isoformat(), "property": GA4_PROPERTY, "range": [d28.isoformat(), end.isoformat()],
        "by_date_channel": ga4_report(["date", "sessionDefaultChannelGroup"], ["sessions", "totalUsers", "engagedSessions", "keyEvents"], "28daysAgo", "yesterday", 1000),
        "organic_landing_28d": ga4_report(["landingPagePlusQueryString"], ["sessions", "engagedSessions", "averageSessionDuration", "keyEvents"], "28daysAgo", "yesterday", 250, organic),
        "all_landing_7d": ga4_report(["landingPagePlusQueryString", "sessionDefaultChannelGroup"], ["sessions", "engagedSessions", "keyEvents"], "7daysAgo", "yesterday", 250),
        "key_events_28d": ga4_report(["eventName"], ["eventCount"], "28daysAgo", "yesterday", 50,
                                     {"filter": {"fieldName": "isKeyEvent", "stringFilter": {"value": "true"}}}),
        "sources_7d": ga4_report(["sessionSource", "sessionMedium"], ["sessions"], "7daysAgo", "yesterday", 100),
    }
    (OUT / "ga4" / f"{TODAY.isoformat()}.json").write_text(json.dumps(ga4, indent=1))

    def tot(rows, k):
        return sum(r.get(k, 0) for r in rows)
    last7 = [r for r in gsc["by_date"] if r["keys"][0] >= d7.isoformat()]
    organic_rows = [r for r in ga4["by_date_channel"] if r["sessionDefaultChannelGroup"] == "Organic Search"]
    latest = {
        "pulled": TODAY.isoformat(),
        "gsc_file": f"tools/seo/data/gsc/{TODAY.isoformat()}.json",
        "ga4_file": f"tools/seo/data/ga4/{TODAY.isoformat()}.json",
        "gsc_clicks_7d": tot(last7, "clicks"), "gsc_impressions_7d": tot(last7, "impressions"),
        "gsc_clicks_28d": tot(gsc["by_date"], "clicks"), "gsc_impressions_28d": tot(gsc["by_date"], "impressions"),
        "gsc_pages_with_impressions_28d": len(gsc["pages_28d"]),
        "gsc_queries_28d": len(gsc["queries_28d"]),
        "ga4_sessions_28d": tot(ga4["by_date_channel"], "sessions"),
        "ga4_organic_sessions_28d": tot(organic_rows, "sessions"),
        "ga4_key_events_28d": tot(ga4["by_date_channel"], "keyEvents"),
    }
    (OUT / "latest.json").write_text(json.dumps(latest, indent=1))
    print(json.dumps(latest, indent=1))


if __name__ == "__main__":
    main()
